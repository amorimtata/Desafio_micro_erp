/**
 * Arquivo responsável por gerenciar os modais relacionados aos produtos.
 * Inclui funções para confirmação de exclusão e feedback visual.
 */

/**
 * Exibe o modal de confirmação de exclusão de produto.
 * Configura o formulário com a URL correta e exibe o modal com animação.
 * 
 * @param {string} url - URL para onde o formulário de exclusão será enviado
 */
function confirmarExclusao(url) {
    const modal = new bootstrap.Modal(document.getElementById('modalExclusao'));
    document.getElementById('formExclusao').action = url;
    modal.show();
} 