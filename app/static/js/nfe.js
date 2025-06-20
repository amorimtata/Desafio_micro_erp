/**
 * Arquivo principal de gerenciamento de Notas Fiscais Eletrônicas (NF-e).
 * Responsável por manipular a interface de criação e edição de NF-e.
 */

/**
 * Adiciona uma nova linha de item na tabela de produtos da NF-e.
 * Cria dinamicamente os campos necessários e configura os eventos.
 */
function adicionarItem() {
    const tbody = document.querySelector('#tabelaItens tbody');
    const tr = document.createElement('tr');
    
    // Monta um select de produtos dinamicamente com dados extras
    let selectHtml = '<select class="form-select" name="produto_id[]" required onchange="selecionarProduto(this)">';
    selectHtml += '<option value="">Selecione...</option>';
    produtos.forEach(produto => {
        selectHtml += `<option value="${produto.id}" data-preco="${produto.preco_unitario}" data-estoque="${produto.saldo_estoque}" data-ncm="${produto.ncm}" data-cfop="${produto.cfop}">${produto.nome}</option>`;
    });
    selectHtml += '</select>';

    // Template da linha com todos os campos necessários
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

/**
 * Manipula a seleção de um produto na linha da NF-e.
 * Preenche automaticamente os campos relacionados ao produto selecionado.
 * 
 * @param {HTMLSelectElement} select - Elemento select que disparou o evento
 */
function selecionarProduto(select) {
    const tr = select.closest('tr');
    const option = select.options[select.selectedIndex];
    
    if (option.value) {
        const preco = parseFloat(option.dataset.preco);
        const estoque = parseInt(option.dataset.estoque);
        const ncm = option.dataset.ncm;
        const cfop = option.dataset.cfop;
        
        tr.querySelector('.valor-unitario').value = preco.toFixed(2);
        tr.querySelector('input[name="ncm[]"]').value = ncm;
        tr.querySelector('input[name="cfop[]"]').value = cfop;
        
        atualizarValores();
    }
}

/**
 * Remove uma linha de item da NF-e.
 * 
 * @param {HTMLButtonElement} button - Botão que disparou o evento de remoção
 */
function removerItem(button) {
    const tr = button.closest('tr');
    tr.remove();
    atualizarValores();
}

function atualizarValores() {
    const linhas = document.querySelectorAll('#tabelaItens tbody tr');
    let total = 0;
    
    linhas.forEach(linha => {
        const quantidade = parseFloat(linha.querySelector('.quantidade').value) || 0;
        const valorUnitario = parseFloat(linha.querySelector('.valor-unitario').value) || 0;
        const valorTotal = quantidade * valorUnitario;
        
        linha.querySelector('.valor-total').value = valorTotal.toFixed(2);
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
    // Aplicar máscaras
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
    
    // Inicializar valores
    atualizarValores();
}); 