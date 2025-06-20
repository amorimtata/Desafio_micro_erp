/**
 * Este arquivo está responsável por gerenciar os modais relacionados ao estoque.
 * Inclui funções para entrada, saída e feedback visual das operações.
 */

/**
 * Exibe o modal de sucesso após uma operação bem-sucedida.
 * Usado para dar feedback visual ao usuário.
 */
function mostrarModalSucesso() {
    const modalSucesso = new bootstrap.Modal(document.getElementById('modalSucesso'));
    modalSucesso.show();
}

/**
 * Salva uma nova entrada de estoque.
 * Envia os dados para a API e exibe feedback visual.
 * Em caso de sucesso, fecha o modal, limpa o formulário e atualiza a lista.
 */
function salvarEntrada() {
    const form = document.getElementById('formNovaEntrada');
    const formData = new FormData(form);
    const data = {
        produto_codigo: formData.get('produto_codigo'),
        quantidade: parseInt(formData.get('quantidade')),
        nota_fiscal: formData.get('nota_fiscal'),
        observacao: formData.get('observacao')
    };
    fetch('/api/entrada', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            alert('Erro: ' + result.error);
        } else {
            const modalEntrada = bootstrap.Modal.getInstance(document.getElementById('modalNovaEntrada'));
            modalEntrada.hide();
            form.reset();
            carregarEntradas();
            
            // Mostrar modal de sucesso após a operação
            mostrarModalSucesso();
        }
    });
} 