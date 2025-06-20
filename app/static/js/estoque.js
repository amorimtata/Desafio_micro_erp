/**
 * Arquivo principal de gestão de estoque.
 * Responsável por gerenciar entradas, saídas e consultas de estoque.
 * Inclui funções para manipulação de dados e interação com a API.
 */

// Funções para gestão de estoque
document.addEventListener('DOMContentLoaded', function() {
    // Inicialização de tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Validação do formulário de movimentação
    const formMovimentacao = document.querySelector('form');
    if (formMovimentacao) {
        formMovimentacao.addEventListener('submit', function(e) {
            const quantidade = document.getElementById('quantidade').value;
            if (quantidade <= 0) {
                e.preventDefault();
                alert('A quantidade deve ser maior que zero!');
                return;
            }
        });
    }
});

// Utilidades globais
function formatarDataLocal(dataIso) {
    if (!dataIso) return '';
    const dt = new Date(dataIso);
    return dt.toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
}

function carregarProdutosDropdown(selectId) {
    fetch('/api/produtos')
        .then(response => response.json())
        .then(produtos => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">Selecione um produto</option>';
            produtos.forEach(produto => {
                const option = document.createElement('option');
                option.value = produto.codigo;
                option.textContent = `${produto.codigo} - ${produto.nome}`;
                select.appendChild(option);
            });
        });
}

function carregarProdutosFiltro(selectId) {
    fetch('/api/produtos')
        .then(response => response.json())
        .then(produtos => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">Todos os Produtos</option>';
            produtos.forEach(produto => {
                const option = document.createElement('option');
                option.value = produto.codigo;
                option.textContent = produto.nome;
                select.appendChild(option);
            });
        });
}

// Entradas
function carregarEntradas() {
    const params = new URLSearchParams();
    const dataIni = document.getElementById('filtroEntradaDataInicial').value;
    const dataFim = document.getElementById('filtroEntradaDataFinal').value;
    const notaFiscal = document.getElementById('filtroEntradaNotaFiscal').value;
    const prod = document.getElementById('filtroEntradaProduto').value;
    if (dataIni) params.append('data_inicial', dataIni);
    if (dataFim) params.append('data_final', dataFim);
    if (notaFiscal) params.append('nota_fiscal', notaFiscal);
    if (prod) params.append('produto_codigo', prod);
    fetch('/api/entradas?' + params.toString())
        .then(response => response.json())
        .then(entradas => {
            const tbody = document.querySelector('#tabelaEntradas tbody');
            tbody.innerHTML = '';
            if (entradas.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhuma entrada registrada</td></tr>';
                return;
            }
            entradas.forEach(entrada => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${formatarDataLocal(entrada.data)}</td>
                    <td>${entrada.produto_nome}</td>
                    <td>${entrada.quantidade}</td>
                    <td>${entrada.nota_fiscal}</td>
                    <td>${entrada.observacao}</td>
                `;
                tbody.appendChild(row);
            });
        });
}

// Saídas
function carregarSaidas() {
    const params = new URLSearchParams();
    const dataIni = document.getElementById('filtroSaidaDataInicial').value;
    const dataFim = document.getElementById('filtroSaidaDataFinal').value;
    const notaFiscal = document.getElementById('filtroSaidaNotaFiscal').value;
    const prod = document.getElementById('filtroSaidaProduto').value;
    if (dataIni) params.append('data_inicial', dataIni);
    if (dataFim) params.append('data_final', dataFim);
    if (notaFiscal) params.append('nota_fiscal', notaFiscal);
    if (prod) params.append('produto_codigo', prod);
    fetch('/api/saidas?' + params.toString())
        .then(response => response.json())
        .then(saidas => {
            const tbody = document.querySelector('#tabelaSaidas tbody');
            tbody.innerHTML = '';
            if (saidas.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhuma saída registrada</td></tr>';
                return;
            }
            saidas.forEach(saida => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${formatarDataLocal(saida.data)}</td>
                    <td>${saida.produto_nome}</td>
                    <td>${saida.quantidade}</td>
                    <td>${saida.nota_fiscal}</td>
                    <td>${saida.observacao}</td>
                `;
                tbody.appendChild(row);
            });
        });
}

// Histórico
function carregarHistorico() {
    const params = new URLSearchParams();
    const dataIni = document.getElementById('filtroHistoricoDataInicial').value;
    const dataFim = document.getElementById('filtroHistoricoDataFinal').value;
    const notaFiscal = document.getElementById('filtroHistoricoNotaFiscal').value;
    const prod = document.getElementById('filtroHistoricoProduto').value;
    if (dataIni) params.append('data_inicial', dataIni);
    if (dataFim) params.append('data_final', dataFim);
    if (notaFiscal) params.append('nota_fiscal', notaFiscal);
    if (prod) params.append('produto_codigo', prod);
    fetch('/api/historico?' + params.toString())
        .then(response => response.json())
        .then(historico => {
            const tbody = document.querySelector('#tabelaHistorico tbody');
            tbody.innerHTML = '';
            if (historico.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhuma movimentação encontrada</td></tr>';
                return;
            }
            historico.forEach(item => {
                const row = document.createElement('tr');
                if (item.status_nf_cancelada) {
                    row.classList.add('bg-warning', 'text-dark');
                }
                row.innerHTML = `
                    <td>${formatarDataLocal(item.data)}</td>
                    <td>${item.tipo === 'entrada' ? '<span class=\'badge bg-success\'>Entrada</span>' : '<span class=\'badge bg-danger\'>Saída</span>'}</td>
                    <td>${item.produto_nome}</td>
                    <td>${item.quantidade}</td>
                    <td>${item.nota_fiscal}</td>
                    <td>${item.status_nf_cancelada ? '<span class=\'fw-bold text-warning\'>NF cancelada</span>' : item.observacao}</td>
                `;
                tbody.appendChild(row);
            });
        });
}

/**
 * Registra uma nova saída de estoque.
 * Envia os dados para a API e atualiza a interface após o sucesso.
 * Inclui validações e feedback visual para o usuário.
 */
function salvarSaida() {
    const form = document.getElementById('formNovaSaida');
    const formData = new FormData(form);
    const data = {
        produto_codigo: formData.get('produto_codigo'),
        quantidade: parseInt(formData.get('quantidade')),
        nota_fiscal: formData.get('nota_fiscal'),
        observacao: formData.get('observacao')
    };
    fetch('/api/saida', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            alert('Erro: ' + result.error);
        } else {
            alert('Saída registrada com sucesso!');
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalNovaSaida'));
            modal.hide();
            form.reset();
            carregarSaidas();
        }
    });
}

// Controle de abas e botões
function atualizarBotoesAbas() {
    document.getElementById('btnNovaEntrada').classList.toggle('d-none', !document.getElementById('entradas').classList.contains('active'));
    document.getElementById('btnNovaSaida').classList.toggle('d-none', !document.getElementById('saidas').classList.contains('active'));
}

// Inicialização dos componentes e eventos quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Carregar produtos nos dropdowns dos modais
    carregarProdutosDropdown('produto');
    carregarProdutosDropdown('produto_saida');
    
    // Carregar produtos nos filtros de busca
    carregarProdutosFiltro('filtroEntradaProduto');
    carregarProdutosFiltro('filtroSaidaProduto');
    carregarProdutosFiltro('filtroHistoricoProduto');
    
    // Carregar dados iniciais das tabelas
    carregarEntradas();
    carregarSaidas();
    carregarHistorico();
    
    // Configurar eventos dos botões de salvar
    document.getElementById('btnSalvarEntrada').addEventListener('click', salvarEntrada);
    document.getElementById('btnSalvarSaida').addEventListener('click', salvarSaida);
    
    // Configurar eventos dos botões de filtro
    document.getElementById('btnFiltrarEntradas').addEventListener('click', carregarEntradas);
    document.getElementById('btnFiltrarSaidas').addEventListener('click', carregarSaidas);
    document.getElementById('btnFiltrarHistorico').addEventListener('click', carregarHistorico);
    
    // Configurar controle de abas
    document.getElementById('estoqueTabs').addEventListener('shown.bs.tab', function (event) {
        atualizarBotoesAbas();
    });
    atualizarBotoesAbas();
}); 