import sys
import os

if not (sys.version_info.major == 3 and sys.version_info.minor in [10, 11]):
    print('ERRO: Este projeto só é suportado no Python 3.10 ou 3.11.\nInstale uma dessas versões para rodar corretamente.')
    sys.exit(1)

from app import create_app, db
from app.models.produto import Produto
from app.models.movimentacao import MovimentacaoEstoque
from app.models.nota_fiscal import NotaFiscal

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Produto': Produto,
        'MovimentacaoEstoque': MovimentacaoEstoque,
        'NotaFiscal': NotaFiscal
    }

if __name__ == '__main__':
    # Criando diretório para NF-e se não existir
    if not os.path.exists('nfe_simulada'):
        os.makedirs('nfe_simulada')
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 