from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from app.models.nota_fiscal import NotaFiscal, ItemNotaFiscal
from app.models.produto import Produto
from app import db
from datetime import datetime
from app.services.nfe_service import NFEService
import os
from app.services.sefaz import enviar_nfe
from app.models.movimentacao import MovimentacaoEstoque
from sqlalchemy import func, cast, Integer
from sqlalchemy.exc import IntegrityError

# Controller responsável pelas rotas e operações relacionadas à Nota Fiscal Eletrônica (NF-e)
nfe_bp = Blueprint('nfe_bp', __name__, url_prefix='/nfe')
nfe_service = NFEService()

def gerar_proximo_numero():
    """
    Gera o próximo número de NF-e de forma segura, evitando concorrência e
    garantindo ordenação numérica correta mesmo com campo string
    """
    while True:
        try:
            # Inicia uma nova transação
            with db.session.begin_nested():
                # Busca o maior número existente usando CAST para garantir ordenação numérica
                ultimo_numero = db.session.query(
                    func.max(cast(NotaFiscal.numero, Integer))
                ).scalar() or 0
                
                # Incrementa para gerar o próximo número
                proximo_numero = str(ultimo_numero + 1)
                
                return proximo_numero
        except Exception as e:
            db.session.rollback()
            continue

@nfe_bp.route('/proximo_numero', methods=['GET'])
def get_proximo_numero():
    """
    Endpoint para buscar o próximo número disponível
    """
    proximo_numero = gerar_proximo_numero()
    return jsonify({'proximo_numero': proximo_numero})

@nfe_bp.route('/')
def listar_nfe():
    nfes = NotaFiscal.query.order_by(NotaFiscal.data_emissao.desc()).all()
    aliquota = 0.18
    nfes_com_icms = []
    for nfe in nfes:
        total_com_icms = 0
        for item in nfe.itens:
            valor_unitario_icms = item.valor_unitario / (1 - aliquota)
            valor_total_icms = valor_unitario_icms * item.quantidade
            total_com_icms += valor_total_icms
        nfes_com_icms.append({
            'id': nfe.id,
            'numero': nfe.numero,
            'serie': nfe.serie,
            'data_emissao': nfe.data_emissao,
            'destinatario_razao_social': nfe.destinatario_razao_social,
            'valor_total_icms': total_com_icms,
            'status': nfe.status,
            'xml_path': nfe.xml_path,
            'pdf_path': getattr(nfe, 'pdf_path', None),
        })
    return render_template('nfe/listar.html', nfes=nfes_com_icms)

@nfe_bp.route('/nova', methods=['GET', 'POST'])
def nova_nfe():
    if request.method == 'POST':
        try:
            # Gerar próximo número de forma segura
            numero_nfe = gerar_proximo_numero()
            
            # Combinar a data informada com a hora atual
            data_informada = datetime.strptime(request.form['data_emissao'], '%Y-%m-%d')
            hora_atual = datetime.now().time()
            data_emissao = datetime.combine(data_informada.date(), hora_atual)
            
            # Criar a NF-e
            nfe = NotaFiscal(
                numero=numero_nfe,
                serie=request.form['serie'],
                data_emissao=data_emissao,
                valor_total=0,  # Inicializar com 0 para evitar erro de NOT NULL
                natureza_operacao=request.form['natureza_operacao'],
                status='rascunho',
                
                # Dados do emitente (usando dados do serviço)
                emitente_cnpj=nfe_service.emitente['cnpj'],
                emitente_razao_social=nfe_service.emitente['razao_social'],
                emitente_ie=nfe_service.emitente['ie'],
                emitente_endereco=nfe_service.emitente['endereco'],
                emitente_numero=nfe_service.emitente['numero'],
                emitente_bairro=nfe_service.emitente['bairro'],
                emitente_cidade=nfe_service.emitente['cidade'],
                emitente_uf=nfe_service.emitente['uf'],
                emitente_cep=nfe_service.emitente['cep'],
                
                # Dados do destinatário
                destinatario_cnpj=request.form['destinatario_cnpj'],
                destinatario_razao_social=request.form['destinatario_razao_social'],
                destinatario_ie=request.form['destinatario_ie'],
                destinatario_endereco=request.form['destinatario_endereco'],
                destinatario_numero=request.form['destinatario_numero'],
                destinatario_bairro=request.form['destinatario_bairro'],
                destinatario_cidade=request.form['destinatario_cidade'],
                destinatario_uf=request.form['destinatario_uf'],
                destinatario_cep=request.form['destinatario_cep']
            )
            
            # Adicionar a nota fiscal e dar flush para garantir que nfe.id exista
            db.session.add(nfe)
            db.session.flush()

            # Agora criar os itens
            valor_total = 0
            produto_ids = request.form.getlist('produto_id[]')
            quantidades = request.form.getlist('quantidade[]')
            valores_unitarios = request.form.getlist('valor_unitario[]')
            ncms = request.form.getlist('ncm[]')
            cfops = request.form.getlist('cfop[]')
            
            for i in range(len(produto_ids)):
                produto = Produto.query.get(produto_ids[i])
                quantidade = int(quantidades[i])
                valor_unitario = float(valores_unitarios[i])
                valor_total_item = quantidade * valor_unitario
                valor_total += valor_total_item
                
                if produto:
                    saldo_atual = produto.saldo_estoque()
                    if saldo_atual < quantidade:
                        flash(f'Estoque insuficiente para {produto.nome}. Disponível: {saldo_atual}, Solicitado: {quantidade}', 'danger')
                        return redirect(url_for('nfe_bp.nova_nfe'))
                
                item = ItemNotaFiscal(
                    nota_fiscal_id=nfe.id,
                    produto_id=produto_ids[i],
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total_item,
                    ncm=ncms[i],
                    cfop=cfops[i]
                )
                db.session.add(item)
            
            nfe.valor_total = valor_total
            db.session.commit()
            flash('NF-e criada com sucesso!', 'success')
            return redirect(url_for('nfe_bp.listar_nfe'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar NF-e: {str(e)}', 'danger')
    
    produtos = Produto.query.all()
    produtos_json = [
        {
            'id': p.id,
            'nome': p.nome,
            'preco_unitario': float(p.preco_unitario),
            'saldo_estoque': p.saldo_estoque(),
            'ncm': p.ncm or '00000000',
            'cfop': p.cfop or '5102'
        } for p in produtos
    ]
    
    # Buscar próximo número para exibir no formulário
    proximo_numero = gerar_proximo_numero()
    return render_template('nfe/nova.html', produtos=produtos_json, proximo_numero=proximo_numero)

@nfe_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_nfe(id):
    nfe = NotaFiscal.query.get_or_404(id)
    
    if nfe.status != 'rascunho':
        flash('Não é possível editar uma NF-e que não está em rascunho.', 'warning')
        return redirect(url_for('nfe_bp.listar_nfe'))
    
    if request.method == 'POST':
        try:
            # Atualizar dados básicos
            nfe.numero = request.form['numero']
            nfe.serie = request.form['serie']
            nfe.data_emissao = datetime.strptime(request.form['data_emissao'], '%Y-%m-%dT%H:%M')
            nfe.natureza_operacao = request.form['natureza_operacao']
            
            # Atualizar dados do emitente
            nfe.emitente_cnpj = request.form['emitente_cnpj']
            nfe.emitente_razao_social = request.form['emitente_razao_social']
            nfe.emitente_ie = request.form['emitente_ie']
            nfe.emitente_endereco = request.form['emitente_endereco']
            nfe.emitente_numero = request.form['emitente_numero']
            nfe.emitente_bairro = request.form['emitente_bairro']
            nfe.emitente_cidade = request.form['emitente_cidade']
            nfe.emitente_uf = request.form['emitente_uf']
            nfe.emitente_cep = request.form['emitente_cep']
            
            # Atualizar dados do destinatário
            nfe.destinatario_cnpj = request.form['destinatario_cnpj']
            nfe.destinatario_razao_social = request.form['destinatario_razao_social']
            nfe.destinatario_ie = request.form['destinatario_ie']
            nfe.destinatario_endereco = request.form['destinatario_endereco']
            nfe.destinatario_numero = request.form['destinatario_numero']
            nfe.destinatario_bairro = request.form['destinatario_bairro']
            nfe.destinatario_cidade = request.form['destinatario_cidade']
            nfe.destinatario_uf = request.form['destinatario_uf']
            nfe.destinatario_cep = request.form['destinatario_cep']
            
            # Remover itens existentes
            for item in nfe.itens:
                db.session.delete(item)
            
            # Adicionar os novos itens
            valor_total = 0
            produto_ids = request.form.getlist('produto_id[]')
            quantidades = request.form.getlist('quantidade[]')
            valores_unitarios = request.form.getlist('valor_unitario[]')
            ncms = request.form.getlist('ncm[]')
            cfops = request.form.getlist('cfop[]')
            
            for i in range(len(produto_ids)):
                quantidade = int(quantidades[i])
                valor_unitario = float(valores_unitarios[i])
                valor_total_item = quantidade * valor_unitario
                valor_total += valor_total_item
                
                item = ItemNotaFiscal(
                    nota_fiscal_id=nfe.id,
                    produto_id=produto_ids[i],
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_total=valor_total_item,
                    ncm=ncms[i],
                    cfop=cfops[i]
                )
                db.session.add(item)
            
            nfe.valor_total = valor_total
            
            db.session.commit()
            flash('NF-e atualizada com sucesso!', 'success')
            return redirect(url_for('nfe_bp.listar_nfe'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar NF-e: {str(e)}', 'danger')
    
    produtos = Produto.query.all()
    return render_template('nfe/editar.html', nfe=nfe, produtos=produtos)

@nfe_bp.route('/<int:id>/excluir', methods=['POST'])
def excluir_nfe(id):
    nfe = NotaFiscal.query.get_or_404(id)
    
    if nfe.status != 'rascunho':
        flash('Não é possível excluir uma NF-e que não está em rascunho.', 'warning')
        return redirect(url_for('nfe_bp.listar_nfe'))
    
    try:
        # Remover itens primeiro
        for item in nfe.itens:
            db.session.delete(item)
        
        db.session.delete(nfe)
        db.session.commit()
        flash('NF-e excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir NF-e: {str(e)}', 'danger')
    
    return redirect(url_for('nfe_bp.listar_nfe'))

@nfe_bp.route('/<int:id>/visualizar')
def visualizar_nfe(id):
    nfe = NotaFiscal.query.get_or_404(id)
    aliquota = 0.18
    itens_com_icms = []
    total_com_icms = 0
    for item in nfe.itens:
        valor_unitario_icms = item.valor_unitario / (1 - aliquota)
        valor_total_icms = valor_unitario_icms * item.quantidade
        itens_com_icms.append({
            'codigo': item.produto.codigo if item.produto else '',
            'nome': item.produto.nome if item.produto else '',
            'ncm': item.ncm,
            'cfop': item.cfop,
            'quantidade': item.quantidade,
            'valor_unitario_icms': valor_unitario_icms,
            'valor_total_icms': valor_total_icms
        })
        total_com_icms += valor_total_icms
    return render_template('nfe/visualizar.html', nfe=nfe, itens_com_icms=itens_com_icms, total_com_icms=total_com_icms)

@nfe_bp.route('/<int:id>/emitir', methods=['POST'])
def emitir_nfe(id):
    nfe = NotaFiscal.query.get_or_404(id)
    
    if nfe.status != 'rascunho':
        flash('Não é possível emitir uma NF-e que não está em rascunho.', 'warning')
        return redirect(url_for('nfe_bp.listar_nfe'))
    
    try:
        # Gerar XML da NF-e
        xml_nfe = nfe_service.gerar_xml(nfe)
        
        # Enviar para a SEFAZ
        sucesso, mensagem, dados = enviar_nfe(xml_nfe)
        
        if sucesso:
            nfe.status = 'autorizada'
            nfe.protocolo = dados['protocolo']
            nfe.chave = dados['chave']
            # Criar movimentação de saída para cada item
            for item in nfe.itens:
                # Buscar o produto para obter o código
                produto = Produto.query.get(item.produto_id)
                if produto:
                    movimentacao = MovimentacaoEstoque(
                        produto_codigo=produto.codigo,
                        tipo='saida',
                        quantidade=item.quantidade,
                        nota_fiscal=str(nfe.numero),
                        observacao=f'Saída automática pela NF-e {nfe.numero}'
                    )
                    db.session.add(movimentacao)
            db.session.commit()
            flash('NF-e autorizada com sucesso!', 'success')
        else:
            flash(f'Erro na autorização da NF-e: {mensagem}', 'danger')
        
        return redirect(url_for('nfe_bp.listar_nfe'))
    except Exception as e:
        flash(f'Erro ao emitir NF-e: {str(e)}', 'danger')
        return redirect(url_for('nfe_bp.listar_nfe'))

@nfe_bp.route('/<int:id>/xml')
def baixar_xml(id):
    nfe = NotaFiscal.query.get_or_404(id)
    
    if not nfe.xml_path or not os.path.exists(nfe.xml_path):
        flash('XML da NF-e não encontrado.', 'warning')
        return redirect(url_for('nfe_bp.listar_nfe'))
    
    return send_file(
        nfe.xml_path,
        mimetype='application/xml',
        as_attachment=True,
        download_name=f'nfe_{nfe.numero}.xml'
    )

@nfe_bp.route('/<int:id>/pdf')
def baixar_pdf(id):
    nfe = NotaFiscal.query.get_or_404(id)
    ok, msg = nfe_service.gerar_pdf(nfe)
    if ok and hasattr(nfe, 'pdf_path') and nfe.pdf_path:
        return send_file(nfe.pdf_path, as_attachment=True)
    else:
        flash('Erro ao gerar PDF: ' + msg, 'danger')
        return redirect(url_for('nfe_bp.visualizar_nfe', id=id))

@nfe_bp.route('/<int:id>/cancelar', methods=['POST'])
def cancelar_nfe(id):
    nfe = NotaFiscal.query.get_or_404(id)
    if nfe.status != 'autorizada':
        flash('Só é possível cancelar NF-e autorizada.', 'warning')
        return redirect(url_for('nfe_bp.listar_nfe'))
    # Reverter estoque: criar movimentação de entrada para cada item
    for item in nfe.itens:
        produto = Produto.query.get(item.produto_id)
        if produto:
            movimentacao = MovimentacaoEstoque(
                produto_codigo=produto.codigo,
                tipo='entrada',
                quantidade=item.quantidade,
                nota_fiscal=str(nfe.numero),
                observacao=f'Estorno por cancelamento da NF-e {nfe.numero} (NF cancelada)'
            )
            db.session.add(movimentacao)
    nfe.status = 'cancelada'
    db.session.commit()
    flash('NF-e cancelada com sucesso!', 'success')
    return redirect(url_for('nfe_bp.listar_nfe')) 