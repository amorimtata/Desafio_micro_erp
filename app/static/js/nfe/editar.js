// Funções para manipulação de itens da NF-e
function adicionarItem() {
    const container = document.getElementById('itens-container');
    const novoItem = container.children[0].cloneNode(true);
    
    // Limpar valores dos campos
    novoItem.querySelectorAll('input').forEach(input => input.value = '');
    novoItem.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
    
    container.appendChild(novoItem);
}

function removerItem(button) {
    const container = document.getElementById('itens-container');
    if (container.children.length > 1) {
        button.closest('.item-nfe').remove();
    }
} 