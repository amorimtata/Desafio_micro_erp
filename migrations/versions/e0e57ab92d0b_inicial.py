"""Inicial

Revision ID: e0e57ab92d0b
Revises: 
Create Date: 2025-06-16 15:03:14.666213

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0e57ab92d0b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notas_fiscais',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('numero', sa.String(length=20), nullable=False),
    sa.Column('serie', sa.String(length=3), nullable=False),
    sa.Column('data_emissao', sa.DateTime(), nullable=True),
    sa.Column('valor_total', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('xml_path', sa.String(length=255), nullable=True),
    sa.Column('pdf_path', sa.String(length=255), nullable=True),
    sa.Column('protocolo_path', sa.String(length=255), nullable=True),
    sa.Column('protocolo', sa.String(length=50), nullable=True),
    sa.Column('chave', sa.String(length=44), nullable=True),
    sa.Column('emitente_cnpj', sa.String(length=14), nullable=False),
    sa.Column('emitente_razao_social', sa.String(length=100), nullable=False),
    sa.Column('emitente_ie', sa.String(length=20), nullable=False),
    sa.Column('emitente_endereco', sa.String(length=100), nullable=False),
    sa.Column('emitente_numero', sa.String(length=10), nullable=False),
    sa.Column('emitente_bairro', sa.String(length=50), nullable=False),
    sa.Column('emitente_cidade', sa.String(length=50), nullable=False),
    sa.Column('emitente_uf', sa.String(length=2), nullable=False),
    sa.Column('emitente_cep', sa.String(length=8), nullable=False),
    sa.Column('destinatario_cnpj', sa.String(length=14), nullable=False),
    sa.Column('destinatario_razao_social', sa.String(length=100), nullable=False),
    sa.Column('destinatario_ie', sa.String(length=20), nullable=False),
    sa.Column('destinatario_endereco', sa.String(length=100), nullable=False),
    sa.Column('destinatario_numero', sa.String(length=10), nullable=False),
    sa.Column('destinatario_bairro', sa.String(length=50), nullable=False),
    sa.Column('destinatario_cidade', sa.String(length=50), nullable=False),
    sa.Column('destinatario_uf', sa.String(length=2), nullable=False),
    sa.Column('destinatario_cep', sa.String(length=8), nullable=False),
    sa.Column('natureza_operacao', sa.String(length=100), nullable=False),
    sa.Column('tipo_operacao', sa.String(length=1), nullable=False),
    sa.Column('finalidade_emissao', sa.String(length=1), nullable=False),
    sa.Column('forma_pagamento', sa.String(length=1), nullable=False),
    sa.Column('forma_emissao', sa.String(length=1), nullable=False),
    sa.Column('ambiente', sa.String(length=1), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero')
    )
    op.create_table('produtos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('codigo', sa.String(length=20), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=True),
    sa.Column('preco_unitario', sa.Float(), nullable=False),
    sa.Column('quantidade_estoque', sa.Integer(), nullable=True),
    sa.Column('data_cadastro', sa.DateTime(), nullable=True),
    sa.Column('ncm', sa.String(length=8), nullable=False),
    sa.Column('cfop', sa.String(length=4), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('codigo')
    )
    op.create_table('itens_nota_fiscal',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nota_fiscal_id', sa.Integer(), nullable=False),
    sa.Column('produto_id', sa.Integer(), nullable=False),
    sa.Column('quantidade', sa.Integer(), nullable=False),
    sa.Column('valor_unitario', sa.Float(), nullable=False),
    sa.Column('valor_total', sa.Float(), nullable=False),
    sa.Column('ncm', sa.String(length=8), nullable=False),
    sa.Column('cfop', sa.String(length=4), nullable=False),
    sa.ForeignKeyConstraint(['nota_fiscal_id'], ['notas_fiscais.id'], ),
    sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('itens_nota_fiscal')
    op.drop_table('produtos')
    op.drop_table('notas_fiscais')
    # ### end Alembic commands ###
