// Funções para os modal de NFE
function confirmarEmissao(url) {
    const modal = new bootstrap.Modal(document.getElementById('modalEmissao'));
    document.getElementById('formEmissaoModal').action = url;
    modal.show();
}

function confirmarCancelamento(url) {
    const modal = new bootstrap.Modal(document.getElementById('modalCancelamento'));
    document.getElementById('formCancelamento').action = url;
    modal.show();
}

function confirmarExclusao(url) {
    const modal = new bootstrap.Modal(document.getElementById('modalExclusao'));
    document.getElementById('formExclusao').action = url;
    modal.show();
} 