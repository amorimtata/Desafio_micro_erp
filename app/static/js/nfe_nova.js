// Pega o array de produtos do atributo data-produtos do form
const form = document.getElementById('formNFe');
const produtos = JSON.parse(form.dataset.produtos);

let produtosCarregados = true;


function adicionarItem() {
    if (!produtosCarregados) {
        alert('Aguarde o carregamento dos produtos!');
        return;
    }
    const tbody = document.querySelector('#tabelaItens tbody');
    const tr = document.createElement('tr');
    
    // Monta o select de produtos dinamicamente
    let selectHtml = '<select class="form-select" name="produto_id[]" required onchange="selecionarProduto(this)">';
    selectHtml += '<option value="">Selecione...</option>';
    produtos.forEach(produto => {
        selectHtml += `<option value="${produto.id}" data-preco="${produto.preco_unitario}" data-estoque="${produto.saldo_estoque}" data-ncm="${produto.ncm}" data-cfop="${produto.cfop}">${produto.nome}</option>`;
    });
    selectHtml += '</select>';

    tr.innerHTML = `
        <td>
            ${selectHtml}
        </td>
        <td>
            <input type="number" class="form-control quantidade" name="quantidade[]" value="1" required min="1" onchange="atualizarValores()">
        </td>
        <td>
            <input type="number" class="form-control valor-unitario" name="valor_unitario[]" value="0.00" required min="0" step="0.01" onchange="atualizarValores()">
        </td>
        <td>
            <input type="text" class="form-control icms-por-dentro" value="" readonly>
        </td>
        <td>
            <input type="number" class="form-control valor-total" value="0.00" readonly>
        </td>
        <td>
            <input type="text" class="form-control" name="ncm[]" value="00000000" required>
        </td>
        <td>
            <input type="text" class="form-control" name="cfop[]" value="5102" required>
        </td>
        <td>
            <button type="button" class="btn btn-danger btn-sm" onclick="removerItem(this)">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    tbody.appendChild(tr);
    atualizarValores();
}

function calcularPrecoFinalICMS(precoBase, aliquota) {
    return +(precoBase / (1 - aliquota)).toFixed(2);
}

function calcularICMSPorDentro(precoFinal, aliquota) {
    return +((precoFinal * aliquota) / (1 + aliquota)).toFixed(2);
}

function selecionarProduto(select) {
    const tr = select.closest('tr');
    const option = select.options[select.selectedIndex];
    
    if (option.value) {
        const preco = parseFloat(option.dataset.preco);
        const ncm = option.dataset.ncm;
        const cfop = option.dataset.cfop;
        const aliquota = 0.18;
        
        // Preço final com ICMS embutido
        const precoFinal = calcularPrecoFinalICMS(preco, aliquota);
        const icmsPorDentro = calcularICMSPorDentro(precoFinal, aliquota);
        
        tr.querySelector('.valor-unitario').value = preco.toFixed(2);
        tr.querySelector('input[name="ncm[]"]').value = ncm;
        tr.querySelector('input[name="cfop[]"]').value = cfop;
        // Atualiza campo de leitura ICMS
        let icmsInput = tr.querySelector('.icms-por-dentro');
        if (icmsInput) icmsInput.value = icmsPorDentro.toFixed(2);
        atualizarValores();
    }
}

function removerItem(button) {
    const tr = button.closest('tr');
    tr.remove();
    atualizarValores();
}

function atualizarValores() {
    const linhas = document.querySelectorAll('#tabelaItens tbody tr');
    let total = 0;
    const aliquota = 0.18;
    linhas.forEach(linha => {
        const quantidade = parseFloat(linha.querySelector('.quantidade').value) || 0;
        const valorUnitario = parseFloat(linha.querySelector('.valor-unitario').value) || 0;
        const precoFinal = calcularPrecoFinalICMS(valorUnitario, aliquota);
        const icmsPorDentro = calcularICMSPorDentro(precoFinal * quantidade, aliquota);
        const valorTotal = quantidade * precoFinal;
        linha.querySelector('.valor-total').value = valorTotal.toFixed(2);
        // Atualiza campo de leitura ICMS se existir
        let icmsInput = linha.querySelector('.icms-por-dentro');
        if (icmsInput) icmsInput.value = icmsPorDentro.toFixed(2);
        total += valorTotal;
    });
    document.getElementById('valorTotal').textContent = `R$ ${total.toFixed(2)}`;
}

// Máscara para CNPJ
function mascaraCNPJ(cnpj) {
    cnpj = cnpj.replace(/\D/g, '');
    cnpj = cnpj.replace(/^(\d{2})(\d)/, '$1.$2');
    cnpj = cnpj.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
    cnpj = cnpj.replace(/\.(\d{3})(\d)/, '.$1/$2');
    cnpj = cnpj.replace(/(\d{4})(\d)/, '$1-$2');
    return cnpj;
}

// Máscara para CEP
function mascaraCEP(cep) {
    cep = cep.replace(/\D/g, '');
    cep = cep.replace(/^(\d{5})(\d)/, '$1-$2');
    return cep;
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Garantir que o número da NF seja mantido
    const numeroInput = document.getElementById('numero');
    if (numeroInput && !numeroInput.value) {
        // Se por algum motivo o número não estiver preenchido, buscar o próximo número
        fetch('/nfe/proximo_numero')
            .then(response => response.json())
            .then(data => {
                numeroInput.value = data.proximo_numero;
            });
    }

    // Aplicar máscaras normalmente
    const cnpjInput = document.getElementById('destinatario_cnpj');
    if (cnpjInput) {
        cnpjInput.addEventListener('input', function(e) {
            e.target.value = mascaraCNPJ(e.target.value);
        });
    }
    const cepInput = document.getElementById('destinatario_cep');
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            e.target.value = mascaraCEP(e.target.value);
        });
    }
    atualizarValores();
});

window.adicionarItem = adicionarItem; 