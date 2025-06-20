from app import db
from datetime import datetime

class ItemNotaFiscal(db.Model):
    __tablename__ = 'itens_nota_fiscal'
    
    id = db.Column(db.Integer, primary_key=True)
    nota_fiscal_id = db.Column(db.Integer, db.ForeignKey('notas_fiscais.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    
    # Campos NCM e CFOP
    ncm = db.Column(db.String(8), nullable=False)
    cfop = db.Column(db.String(4), nullable=False)
    
    def __repr__(self):
        return f'<ItemNotaFiscal {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nota_fiscal_id': self.nota_fiscal_id,
            'produto_id': self.produto_id,
            'quantidade': self.quantidade,
            'valor_unitario': self.valor_unitario,
            'valor_total': self.valor_total,
            'ncm': self.ncm,
            'cfop': self.cfop
        }

class NotaFiscal(db.Model):
    __tablename__ = 'notas_fiscais'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    serie = db.Column(db.String(3), nullable=False, default='1')
    data_emissao = db.Column(db.DateTime, default=datetime.utcnow)
    valor_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='rascunho')  # rascunho, emitida, cancelada
    xml_path = db.Column(db.String(255))  # caminho do arquivo XML
    
    # Campos do emitente
    emitente_cnpj = db.Column(db.String(14), nullable=False)
    emitente_razao_social = db.Column(db.String(100), nullable=False)
    emitente_ie = db.Column(db.String(20), nullable=False)
    emitente_endereco = db.Column(db.String(100), nullable=False)
    emitente_numero = db.Column(db.String(10), nullable=False)
    emitente_bairro = db.Column(db.String(50), nullable=False)
    emitente_cidade = db.Column(db.String(50), nullable=False)
    emitente_uf = db.Column(db.String(2), nullable=False)
    emitente_cep = db.Column(db.String(8), nullable=False)
    
    # Campos do destinatário
    destinatario_cnpj = db.Column(db.String(14), nullable=False)
    destinatario_razao_social = db.Column(db.String(100), nullable=False)
    destinatario_ie = db.Column(db.String(20), nullable=False)
    destinatario_endereco = db.Column(db.String(100), nullable=False)
    destinatario_numero = db.Column(db.String(10), nullable=False)
    destinatario_bairro = db.Column(db.String(50), nullable=False)
    destinatario_cidade = db.Column(db.String(50), nullable=False)
    destinatario_uf = db.Column(db.String(2), nullable=False)
    destinatario_cep = db.Column(db.String(8), nullable=False)
    
    # Campos fiscais
    natureza_operacao = db.Column(db.String(100), nullable=False, default='Venda ao Consumidor')
    tipo_operacao = db.Column(db.String(1), nullable=False, default='1')  # 1=Saída, 0=Entrada
    finalidade_emissao = db.Column(db.String(1), nullable=False, default='1')  # 1=Normal
    forma_pagamento = db.Column(db.String(1), nullable=False, default='0')  # 0=À Vista
    forma_emissao = db.Column(db.String(1), nullable=False, default='1')  # 1=Normal
    ambiente = db.Column(db.String(1), nullable=False, default='2')  # 2=Homologação
    
    # Relacionamentos
    itens = db.relationship('ItemNotaFiscal', backref='nota_fiscal', lazy=True)
    
    def __repr__(self):
        return f'<NotaFiscal {self.numero}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'serie': self.serie,
            'data_emissao': self.data_emissao.isoformat(),
            'valor_total': self.valor_total,
            'status': self.status,
            'xml_path': self.xml_path,
            'emitente': {
                'cnpj': self.emitente_cnpj,
                'razao_social': self.emitente_razao_social,
                'ie': self.emitente_ie,
                'endereco': self.emitente_endereco,
                'numero': self.emitente_numero,
                'bairro': self.emitente_bairro,
                'cidade': self.emitente_cidade,
                'uf': self.emitente_uf,
                'cep': self.emitente_cep
            },
            'destinatario': {
                'cnpj': self.destinatario_cnpj,
                'razao_social': self.destinatario_razao_social,
                'ie': self.destinatario_ie,
                'endereco': self.destinatario_endereco,
                'numero': self.destinatario_numero,
                'bairro': self.destinatario_bairro,
                'cidade': self.destinatario_cidade,
                'uf': self.destinatario_uf,
                'cep': self.destinatario_cep
            },
            'itens': [item.to_dict() for item in self.itens]
        } 