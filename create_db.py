import sys

if not (sys.version_info.major == 3 and sys.version_info.minor in [10, 11]):
    print('ERRO: Este projeto só é suportado no Python 3.10 ou 3.11.\nInstale uma dessas versões para rodar corretamente.')
    sys.exit(1)

from app import create_app, db
from app.models.produto import Produto
from app.models.movimentacao import MovimentacaoEstoque
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Verificar se já existem produtos
        if Produto.query.first() is None:
            # Criar produtos de exemplo
            produtos = [
                Produto(
                    codigo='P001',
                    nome='Notebook Dell XPS',
                    descricao='Notebook Dell XPS 13 polegadas, 16GB RAM, 512GB SSD',
                    preco_unitario=8999.90
                ),
                Produto(
                    codigo='P002',
                    nome='Monitor LG 27"',
                    descricao='Monitor LG 27 polegadas, Full HD, HDMI',
                    preco_unitario=1299.90
                ),
                Produto(
                    codigo='P003',
                    nome='Teclado Mecânico',
                    descricao='Teclado mecânico RGB, switches blue',
                    preco_unitario=299.90
                )
            ]
            
            # Adicionar produtos ao banco
            for produto in produtos:
                db.session.add(produto)
            
            db.session.commit()
            
            # Criar movimentações de exemplo usando os códigos dos produtos
            movimentacoes = [
                MovimentacaoEstoque(
                    produto_codigo='P001',
                    tipo='entrada',
                    quantidade=10,
                    observacao='Entrada inicial de estoque'
                ),
                MovimentacaoEstoque(
                    produto_codigo='P002',
                    tipo='entrada',
                    quantidade=15,
                    observacao='Entrada inicial de estoque'
                ),
                MovimentacaoEstoque(
                    produto_codigo='P003',
                    tipo='entrada',
                    quantidade=20,
                    observacao='Entrada inicial de estoque'
                )
            ]
            
            # Adicionar movimentações ao banco
            for movimentacao in movimentacoes:
                db.session.add(movimentacao)
            
            # Commit das alterações
            db.session.commit()
            
            print("Banco de dados inicializado com sucesso!")
        else:
            print("O banco de dados já contém dados!")

if __name__ == '__main__':
    init_db() 