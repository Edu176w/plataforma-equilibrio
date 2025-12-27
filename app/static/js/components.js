let allComponents = [];
let filteredComponents = [];
let selectedComponents = [];
let currentPage = 1;
const itemsPerPage = 20;

document.addEventListener('DOMContentLoaded', async function() {
    await loadComponents();
    setupFilters();
    setupSearch();
    setupSelectAll();
    
    // Restaurar seleção do sessionStorage
    const saved = sessionStorage.getItem('selectedComponents');
    if (saved) {
        selectedComponents = JSON.parse(saved);
        updateSelectionPanel();
    }
});

async function loadComponents() {
    try {
        const response = await fetch('/api/components/list');
        const data = await response.json();
        
        if (data.success) {
            allComponents = data.components;
            filteredComponents = allComponents;
            
            document.getElementById('totalComponents').textContent = allComponents.length;
            document.getElementById('filteredComponents').textContent = filteredComponents.length;
            
            renderTable();
            renderPagination();
        }
    } catch (error) {
        console.error('Erro ao carregar componentes:', error);
    }
}

function setupFilters() {
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', function() {
            document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            applyFilter(filter);
        });
    });
}

function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        filteredComponents = allComponents.filter(comp => {
            return comp.name.toLowerCase().includes(searchTerm) ||
                   comp.formula.toLowerCase().includes(searchTerm) ||
                   comp.cas.includes(searchTerm);
        });
        
        document.getElementById('filteredComponents').textContent = filteredComponents.length;
        currentPage = 1;
        renderTable();
        renderPagination();
    });
}

function setupSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.row-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = this.checked;
                const cas = cb.getAttribute('data-cas');
                if (this.checked) {
                    toggleSelection(cas, true);
                } else {
                    toggleSelection(cas, false);
                }
            });
        });
    }
}

function applyFilter(filter) {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    if (filter === 'all') {
        filteredComponents = allComponents;
    } else if (filter === 'common') {
        const common = ['Water', 'Ethanol', 'Methanol', 'Acetone', 'Benzene', 'Toluene', 
                       'Hexane', 'Heptane', 'Octane', 'Acetic acid'];
        filteredComponents = allComponents.filter(c => common.includes(c.name));
    } else if (filter === 'organic') {
        filteredComponents = allComponents.filter(c => c.formula.includes('C'));
    } else if (filter === 'polar') {
        filteredComponents = allComponents.filter(c => c.dipole && c.dipole > 0);
    } else if (filter === 'aromatic') {
        filteredComponents = allComponents.filter(c => 
            ['Benzene', 'Toluene', 'Xylene', 'Naphthalene', 'Phenol'].some(name => 
                c.name.includes(name)
            )
        );
    }
    
    if (searchTerm) {
        filteredComponents = filteredComponents.filter(comp => {
            return comp.name.toLowerCase().includes(searchTerm) ||
                   comp.formula.toLowerCase().includes(searchTerm) ||
                   comp.cas.includes(searchTerm);
        });
    }
    
    document.getElementById('filteredComponents').textContent = filteredComponents.length;
    currentPage = 1;
    renderTable();
    renderPagination();
}

function renderTable() {
    const tbody = document.getElementById('componentsTableBody');
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageComponents = filteredComponents.slice(start, end);
    
    tbody.innerHTML = pageComponents.map(comp => {
        const isSelected = selectedComponents.some(s => s.cas === comp.cas);
        return `
        <tr class="${isSelected ? 'selected' : ''}">
            <td>
                <input type="checkbox" 
                       class="form-check-input row-checkbox" 
                       data-cas="${comp.cas}"
                       ${isSelected ? 'checked' : ''}
                       onchange="toggleSelectionCheckbox('${comp.cas}', this.checked)">
            </td>
            <td><strong>${escapeHtml(comp.name)}</strong></td>
            <td><code>${escapeHtml(comp.formula)}</code></td>
            <td>${escapeHtml(comp.cas)}</td>
            <td>${comp.MW ? comp.MW.toFixed(2) : 'N/A'}</td>
            <td>${comp.Tb ? comp.Tb.toFixed(2) : 'N/A'}</td>
            <td>${comp.Tc ? comp.Tc.toFixed(2) : 'N/A'}</td>
            <td>
                <button class="btn-sim ${isSelected ? 'btn-sim-secondary' : 'btn-sim-primary'} btn-sm" 
                        onclick="toggleSelection('${comp.cas}')">
                    <i class="bi bi-${isSelected ? 'check-circle-fill' : 'plus-circle'}"></i> 
                    ${isSelected ? 'Selecionado' : 'Selecionar'}
                </button>
            </td>
        </tr>
    `}).join('');
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function toggleSelectionCheckbox(cas, checked) {
    const comp = allComponents.find(c => c.cas === cas);
    if (!comp) return;
    
    const index = selectedComponents.findIndex(s => s.cas === cas);
    
    if (checked && index === -1) {
        selectedComponents.push(comp);
    } else if (!checked && index > -1) {
        selectedComponents.splice(index, 1);
    }
    
    sessionStorage.setItem('selectedComponents', JSON.stringify(selectedComponents));
    updateSelectionPanel();
    renderTable();
}

function toggleSelection(cas, forceState = null) {
    const comp = allComponents.find(c => c.cas === cas);
    if (!comp) return;
    
    const index = selectedComponents.findIndex(s => s.cas === cas);
    
    if (forceState === true) {
        if (index === -1) selectedComponents.push(comp);
    } else if (forceState === false) {
        if (index > -1) selectedComponents.splice(index, 1);
    } else {
        if (index > -1) {
            selectedComponents.splice(index, 1);
        } else {
            selectedComponents.push(comp);
        }
    }
    
    sessionStorage.setItem('selectedComponents', JSON.stringify(selectedComponents));
    updateSelectionPanel();
    renderTable();
}

function updateSelectionPanel() {
    const panel = document.getElementById('selectionPanel');
    const list = document.getElementById('selectedList');
    const count = document.getElementById('selectedCount');
    
    count.textContent = selectedComponents.length;
    
    if (selectedComponents.length === 0) {
        panel.classList.remove('show');
        return;
    }
    
    panel.classList.add('show');
    
    list.innerHTML = selectedComponents.map(comp => `
        <div class="selected-item">
            <span class="selected-item-name"><strong>${escapeHtml(comp.name)}</strong></span>
            <button class="remove-btn" onclick="toggleSelection('${comp.cas}')">
                <i class="bi bi-x-circle-fill"></i>
            </button>
        </div>
    `).join('');
}

function clearSelection() {
    selectedComponents = [];
    sessionStorage.removeItem('selectedComponents');
    updateSelectionPanel();
    renderTable();
}

function showModuleSelection() {
    const count = selectedComponents.length;
    const modal = document.getElementById('moduleModal');
    const message = document.getElementById('moduleMessage');
    
    if (count === 0) {
        alert('Selecione pelo menos 1 componente!');
        return;
    }
    
    if (count === 1) {
        message.textContent = '1 componente selecionado. Escolha o módulo:';
    } else if (count === 2) {
        message.textContent = '2 componentes selecionados. Recomendado: ELV ou ESL';
    } else if (count === 3) {
        message.textContent = '3 componentes selecionados. Recomendado: ELL';
    } else {
        message.textContent = count + ' componentes selecionados. Escolha o módulo:';
    }
    
    modal.classList.add('show');
}

function closeModuleModal() {
    document.getElementById('moduleModal').classList.remove('show');
}

function goToModule(module) {
    const names = selectedComponents.map(c => c.name);
    const params = new URLSearchParams();
    
    names.forEach((name, i) => {
        params.append('comp' + (i + 1), name);
    });
    
    window.location.href = '/' + module + '/calculator?' + params.toString();
}

function renderPagination() {
    const totalPages = Math.ceil(filteredComponents.length / itemsPerPage);
    const pagination = document.getElementById('pagination');
    
    let html = '';
    
    if (currentPage > 1) {
        html += '<button class="page-btn" onclick="changePage(' + (currentPage - 1) + ')">‹ Anterior</button>';
    }
    
    for (let i = 1; i <= Math.min(totalPages, 10); i++) {
        html += '<button class="page-btn ' + (i === currentPage ? 'active' : '') + '" onclick="changePage(' + i + ')">' + i + '</button>';
    }
    
    if (currentPage < totalPages) {
        html += '<button class="page-btn" onclick="changePage(' + (currentPage + 1) + ')">Próximo ›</button>';
    }
    
    pagination.innerHTML = html;
}

function changePage(page) {
    currentPage = page;
    renderTable();
    renderPagination();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function exportToCSV() {
    const csv = [
        ['Nome', 'Fórmula', 'CAS', 'MW', 'Tb', 'Tc', 'Pc', 'omega'],
        ...filteredComponents.map(c => [
            c.name, c.formula, c.cas, c.MW, c.Tb, c.Tc, c.Pc, c.omega
        ])
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'componentes.csv';
    a.click();
}

// Função para salvar simulação
async function saveSimulation(module, calcType, model, components, conditions, results, execTime, success = true, error = null) {
    try {
        await fetch('/api/dashboard/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                module: module,
                calculation_type: calcType,
                model: model,
                components: components,
                conditions: conditions,
                results: results,
                execution_time: execTime,
                success: success,
                error_message: error
            })
        });
    } catch (error) {
        console.error('Erro ao salvar simulação:', error);
    }
}

// Disponibilizar globalmente
window.saveSimulation = saveSimulation;
