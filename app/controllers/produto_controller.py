from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.produto import Produto
from app import db

produto_bp = Blueprint('produto_bp', __name__)

# Controller responsável pelas rotas e operações relacionadas aos Produtos

@produto_bp.route('/produtos')
def listar_produtos():
    produtos = Produto.query.all()
    produtos_com_saldo = []
    for produto in produtos:
        saldo = produto.saldo_estoque()
        produtos_com_saldo.append({
            'id': produto.id,
            'codigo': produto.codigo,
            'nome': produto.nome,
            'preco_unitario': produto.preco_unitario,
            'unidade': produto.unidade,
            'saldo_estoque': saldo
        })
    return render_template('produtos/listar.html', produtos=produtos_com_saldo)

@produto_bp.route('/produtos/novo', methods=['GET', 'POST'])
def novo_produto():
    if request.method == 'POST':
        try:
            produto = Produto(
                codigo=request.form['codigo'],
                nome=request.form['nome'],
                descricao=request.form['descricao'],
                preco_unitario=float(request.form['preco_unitario']),
                ncm=request.form['ncm'],
                cfop=request.form['cfop'],
                unidade=request.form['unidade']
            )
            db.session.add(produto)
            db.session.commit()
            flash('Produto criado com sucesso!', 'success')
            return redirect(url_for('produto_bp.listar_produtos'))
        except Exception as e:
            flash(f'Erro ao criar produto: {str(e)}', 'danger')
    
    return render_template('produtos/novo.html')

@produto_bp.route('/produtos/<int:id>/editar', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            produto.codigo = request.form['codigo']
            produto.nome = request.form['nome']
            produto.descricao = request.form['descricao']
            produto.preco_unitario = float(request.form['preco_unitario'])
            produto.ncm = request.form['ncm']
            produto.cfop = request.form['cfop']
            produto.unidade = request.form['unidade']
            
            db.session.commit()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('produto_bp.listar_produtos'))
        except Exception as e:
            flash(f'Erro ao atualizar produto: {str(e)}', 'danger')
    
    return render_template('produtos/editar.html', produto=produto)

@produto_bp.route('/produtos/<int:id>/excluir', methods=['POST'])
def excluir(id):
    produto = Produto.query.get_or_404(id)

    # Verifica se o produto tem movimentações ou está em alguma nota fiscal
    if produto.movimentacoes or produto.itens_nota_fiscal:
        flash('Este produto não pode ser excluído, pois possui movimentações de estoque ou está vinculado a notas fiscais emitidas.', 'danger')
        return redirect(url_for('produto_bp.listar_produtos'))

    try:
        db.session.delete(produto)
        db.session.commit()
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir produto: {str(e)}', 'danger')
    
    return redirect(url_for('produto_bp.listar_produtos')) 