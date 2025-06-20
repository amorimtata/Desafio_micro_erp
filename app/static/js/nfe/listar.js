// Função para confirmar exclusão de NF-e
function confirmarExclusao(url) {
    var modal = document.getElementById('modalExclusao');
    var form = document.getElementById('formExclusao');
    form.action = url;
    var bsModal = new bootstrap.Modal(modal);
    bsModal.show();
} 