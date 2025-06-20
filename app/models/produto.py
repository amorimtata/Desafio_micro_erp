from app import db
from datetime import datetime

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco_unitario = db.Column(db.Float, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos fiscais
    ncm = db.Column(db.String(8), nullable=False, default='00000000')
    cfop = db.Column(db.String(4), nullable=False, default='5102')
    
    # Relacionamentos
    itens_nota_fiscal = db.relationship('ItemNotaFiscal', backref='produto', lazy=True)
    
    # Novos campos
    unidade = db.Column(db.String(10), nullable=False, default='un')
    quantidade_minima = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<Produto {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco_unitario': self.preco_unitario,
            'data_cadastro': self.data_cadastro.isoformat(),
            'ncm': self.ncm,
            'cfop': self.cfop,
            'unidade': self.unidade,
            'quantidade_minima': self.quantidade_minima
        }
    
    def saldo_estoque(self):
        from app.models.movimentacao import MovimentacaoEstoque
        entradas = db.session.query(db.func.sum(MovimentacaoEstoque.quantidade)).filter(
            MovimentacaoEstoque.produto_codigo == self.codigo,
            MovimentacaoEstoque.tipo == 'entrada'
        ).scalar() or 0
        saidas = db.session.query(db.func.sum(MovimentacaoEstoque.quantidade)).filter(
            MovimentacaoEstoque.produto_codigo == self.codigo,
            MovimentacaoEstoque.tipo == 'saida'
        ).scalar() or 0
        return entradas - saidas 