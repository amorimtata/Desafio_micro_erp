from flask import Blueprint, render_template, request, jsonify
from app.models.produto import Produto
from app.models.movimentacao import MovimentacaoEstoque
from app import db
from sqlalchemy import and_
from datetime import datetime

estoque_bp = Blueprint('estoque_bp', __name__)

# Controller responsável pelas rotas e operações relacionadas ao Estoque

@estoque_bp.route('/estoque')
def gestao_estoque():
    produtos = Produto.query.all()
    produtos_com_saldo = []
    for produto in produtos:
        saldo = produto.saldo_estoque()
        produtos_com_saldo.append({
            'id': produto.id,
            'codigo': produto.codigo,
            'nome': produto.nome,
            'unidade': getattr(produto, 'unidade', 'un'),
            'preco_unitario': produto.preco_unitario,
            'quantidade_minima': getattr(produto, 'quantidade_minima', None),
            'saldo_estoque': saldo
        })
    return render_template('estoque/gestao.html', produtos=produtos_com_saldo)

# API Produtos
@estoque_bp.route('/api/produtos')
def api_produtos():
    produtos = Produto.query.all()
    return jsonify([{
        'codigo': produto.codigo,
        'nome': produto.nome
    } for produto in produtos])

# API Entrada
@estoque_bp.route('/api/entrada', methods=['POST'])
def api_entrada():
    try:
        data = request.get_json()
        if not all(key in data for key in ['produto_codigo', 'quantidade']):
            return jsonify({'error': 'produto_codigo e quantidade são obrigatórios'}), 400
        produto = Produto.query.filter_by(codigo=data['produto_codigo']).first()
        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404
        movimentacao = MovimentacaoEstoque(
            tipo='entrada',
            produto_codigo=data['produto_codigo'],
            quantidade=data['quantidade'],
            nota_fiscal=data.get('nota_fiscal', ''),
            origem=data.get('origem', ''),
            observacao=data.get('observacao', '')
        )
        db.session.add(movimentacao)
        db.session.commit()
        return jsonify({'message': 'Entrada registrada com sucesso', 'id': movimentacao.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Saída
@estoque_bp.route('/api/saida', methods=['POST'])
def api_saida():
    try:
        data = request.get_json()
        if not all(key in data for key in ['produto_codigo', 'quantidade']):
            return jsonify({'error': 'produto_codigo e quantidade são obrigatórios'}), 400
        produto = Produto.query.filter_by(codigo=data['produto_codigo']).first()
        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404
        movimentacao = MovimentacaoEstoque(
            tipo='saida',
            produto_codigo=data['produto_codigo'],
            quantidade=data['quantidade'],
            nota_fiscal=data.get('nota_fiscal', ''),
            origem=data.get('origem', ''),
            observacao=data.get('observacao', '')
        )
        db.session.add(movimentacao)
        db.session.commit()
        return jsonify({'message': 'Saída registrada com sucesso', 'id': movimentacao.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Função auxiliar para filtros

def aplicar_filtros(query, tipo=None):
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    produto_codigo = request.args.get('produto_codigo')
    nota_fiscal = request.args.get('nota_fiscal')
    filtros = []
    if tipo:
        filtros.append(MovimentacaoEstoque.tipo == tipo)
    if data_inicial:
        try:
            dt_ini = datetime.strptime(data_inicial, '%Y-%m-%d')
            filtros.append(MovimentacaoEstoque.data >= dt_ini)
        except:
            pass
    if data_final:
        try:
            dt_fim = datetime.strptime(data_final, '%Y-%m-%d')
            filtros.append(MovimentacaoEstoque.data <= dt_fim)
        except:
            pass
    if produto_codigo:
        filtros.append(MovimentacaoEstoque.produto_codigo == produto_codigo)
    if nota_fiscal:
        filtros.append(MovimentacaoEstoque.nota_fiscal.ilike(f"%{nota_fiscal}%"))
    if filtros:
        query = query.filter(and_(*filtros))
    return query

# API Entradas (com filtro)
@estoque_bp.route('/api/entradas')
def api_entradas():
    try:
        query = db.session.query(MovimentacaoEstoque, Produto).join(
            Produto, MovimentacaoEstoque.produto_codigo == Produto.codigo
        )
        query = aplicar_filtros(query, tipo='entrada')
        entradas = query.order_by(MovimentacaoEstoque.data.desc()).all()
        return jsonify([{
            'data': mov.data.isoformat(),
            'produto_nome': prod.nome,
            'quantidade': mov.quantidade,
            'nota_fiscal': mov.nota_fiscal or '-',
            'observacao': mov.observacao or '-'
        } for mov, prod in entradas])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Saídas (com filtro)
@estoque_bp.route('/api/saidas')
def api_saidas():
    try:
        query = db.session.query(MovimentacaoEstoque, Produto).join(
            Produto, MovimentacaoEstoque.produto_codigo == Produto.codigo
        )
        query = aplicar_filtros(query, tipo='saida')
        saidas = query.order_by(MovimentacaoEstoque.data.desc()).all()
        return jsonify([{
            'data': mov.data.isoformat(),
            'produto_nome': prod.nome,
            'quantidade': mov.quantidade,
            'nota_fiscal': mov.nota_fiscal or '-',
            'observacao': mov.observacao or '-'
        } for mov, prod in saidas])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Histórico (entradas e saídas juntos, com filtro)
@estoque_bp.route('/api/historico')
def api_historico():
    try:
        query = db.session.query(MovimentacaoEstoque, Produto).join(
            Produto, MovimentacaoEstoque.produto_codigo == Produto.codigo
        )
        query = aplicar_filtros(query)
        historico = query.order_by(MovimentacaoEstoque.data.desc()).all()
        return jsonify([{
            'data': mov.data.isoformat(),
            'tipo': mov.tipo,
            'produto_nome': prod.nome,
            'quantidade': mov.quantidade,
            'nota_fiscal': mov.nota_fiscal or '-',
            'observacao': mov.observacao or '-',
            'status_nf_cancelada': 'NF cancelada' in (mov.observacao or '')
        } for mov, prod in historico])
    except Exception as e:
        return jsonify({'error': str(e)}), 500 