// Funções para gestão de produtos

// Função para formatar valor em Real (R$)
function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

// Função para converter valor formatado em número
function converterParaNumero(valor) {
    return Number(valor.replace(/[^0-9,]/g, '').replace(',', '.'));
}

document.addEventListener('DOMContentLoaded', function() {
    // Formatação do campo de preço
    const precoInput = document.getElementById('preco_unitario');
    if (precoInput) {
        // Ao carregar, formatar o valor existente
        if (precoInput.value) {
            const valor = Number(precoInput.value);
            precoInput.value = valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }

        precoInput.addEventListener('input', function(e) {
            let valor = e.target.value.replace(/\D/g, '');
            valor = (Number(valor) / 100).toLocaleString('pt-BR', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2 
            });
            e.target.value = valor;
        });

        // Antes de enviar o form, converter para formato aceito pelo backend
        const formProduto = precoInput.closest('form');
        if (formProduto) {
            formProduto.addEventListener('submit', function(e) {
                e.preventDefault();
                const valor = converterParaNumero(precoInput.value);
                if (valor <= 0) {
                    alert('O preço deve ser maior que zero!');
                    return;
                }
                precoInput.value = valor;
                this.submit();
            });
        }
    }

    // Máscara para NCM
    const ncmInput = document.getElementById('ncm');
    if (ncmInput) {
        ncmInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 8);
        });
    }

    // Máscara para CFOP
    const cfopInput = document.getElementById('cfop');
    if (cfopInput) {
        cfopInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
        });
    }

    // Geração automática do código do produto a partir do nome
    const nomeInput = document.getElementById('nome');
    const codigoInput = document.getElementById('codigo');
    if (nomeInput && codigoInput) {
        nomeInput.addEventListener('input', function() {
            let nome = nomeInput.value.trim();
            if (nome.length === 0) {
                codigoInput.value = '';
                return;
            }
            let slug = nome.normalize('NFD').replace(/[^\w\s]/g, '').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '').toUpperCase();
            slug = slug.substring(0, 4);
            codigoInput.value = slug + '001';
        });
    }
}); 