from app import db
from datetime import datetime
import pytz

class MovimentacaoEstoque(db.Model):
    __tablename__ = 'movimentacao_estoque'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('America/Sao_Paulo')))
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' ou 'saida'
    produto_codigo = db.Column(db.String(20), db.ForeignKey('produtos.codigo'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    nota_fiscal = db.Column(db.String(50))
    origem = db.Column(db.String(100))
    observacao = db.Column(db.Text)
    
    produto = db.relationship('Produto', backref='movimentacoes', foreign_keys=[produto_codigo])
    
    def __repr__(self):
        return f'<MovimentacaoEstoque {self.tipo} - {self.quantidade}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat(),
            'tipo': self.tipo,
            'produto_codigo': self.produto_codigo,
            'quantidade': self.quantidade,
            'nota_fiscal': self.nota_fiscal,
            'origem': self.origem,
            'observacao': self.observacao,
            'produto_nome': self.produto.nome if self.produto else ''
        } 