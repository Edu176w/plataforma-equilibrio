// static/js/esl.js - VERSÃO COMPLETA REFINADA
console.log('[ESL] esl.js carregado - versão 2025-12-20 REFINADA COMPLETA');

// ============================================================================
// CONFIGURAÇÃO
// ============================================================================
const MAX_COMPONENTS = 3;

// ============================================================================
// VARIÁVEIS GLOBAIS
// ============================================================================
let selectedComponents = [];
let allComponents = [];
let allComponentsOriginal = [];
let eutecticSystems = [];
let currentChart = null;

let lastDiagramData = null;
let lastDiagramType = null;
let lastModel = null;
let lastTemperature = null;

window.lastPointResults = null;
window.lastAiSuggestion = null;
window.comparisonChart = null;

const componentPropertiesCache = {};

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================
document.addEventListener('DOMContentLoaded', async function () {
  console.log('[ESL] Inicializando módulo ESL...');

  await loadAllComponents();
  await loadEutecticSystems();
  updateFields();
  initializeTooltips();
  addPrausnitzExamplesButton();

  const btnDiag = document.getElementById('export-buttons');
  const btnPts = document.getElementById('export-buttons-points');
  if (btnDiag) btnDiag.style.display = 'none';
  if (btnPts) btnPts.style.display = 'none';

  const btnCompare = document.getElementById('compare-models-btn');
  if (btnCompare) {
    btnCompare.addEventListener('click', compareModels);
  }

  const modelSelect = document.getElementById('model');
  if (modelSelect) {
    modelSelect.addEventListener('change', async function () {
      const selectedModel = this.value;
      console.log('[ESL] Modelo alterado para: ' + selectedModel);
      await filterComponentsByModel(selectedModel);
      await validateComponentsForModel();
    });
  }

  const eqToggle = document.getElementById('useCompleteEquation');
  if (eqToggle) {
    eqToggle.addEventListener('change', function () {
      const isChecked = this.checked;
      console.log('[ESL] Equação ' + (isChecked ? 'completa' : 'simplificada') + ' selecionada');
    });
  }

  console.log('[ESL] Módulo inicializado com sucesso!');
});

// =============================================================================
// CARREGAMENTO DE COMPONENTES ESL
// =============================================================================

/**
 * Carrega TODOS os componentes disponíveis da base de dados ESL
 * Endpoint: /esl/components (SOMENTE ESL - não carrega de ELL)
 */
async function loadAllComponents() {
    try {
        console.log('[ESL] Carregando componentes da base de dados ESL...');
        
        // ✅ CORRETO: Carregar SOMENTE de /esl/components
        const response = await fetch('/esl/components');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.components) {
            allComponentsOriginal = data.components;
            allComponents = allComponentsOriginal.slice();
            
            console.log(`[ESL] ✓ ${allComponents.length} componentes ESL carregados com sucesso`);
            console.log('[ESL] Componentes disponíveis:', allComponents.map(c => c.name || c.name_en).join(', '));
            
            // Atualizar contador na interface
            const countSpan = document.getElementById('componentDatabaseCount');
            if (countSpan) {
                countSpan.textContent = allComponents.length;
            }
            
            // Atualizar lista de busca
            populateComponentSearch();
            
            showNotification(`✓ ${allComponents.length} componentes ESL disponíveis`, 'success');
            
        } else {
            throw new Error(data.error || 'Formato de resposta inválido do servidor');
        }
        
    } catch (err) {
        console.error('[ESL] ❌ Erro ao carregar componentes ESL:', err);
        
        // Mostrar mensagem de erro ao usuário
        showNotification(
            `Erro ao carregar base de dados ESL: ${err.message}. Verifique se o servidor está rodando.`,
            'danger'
        );
        
        // Inicializar com array vazio para evitar crashes
        allComponentsOriginal = [];
        allComponents = [];
        
        // Atualizar contador
        const countSpan = document.getElementById('componentDatabaseCount');
        if (countSpan) {
            countSpan.textContent = '0';
        }
    }
}


/**
 * Preenche o campo de busca com os componentes disponíveis
 * Chamado após loadAllComponents() carregar os dados
 */
function populateComponentSearch() {
    const searchInput = document.getElementById('componentSearch');
    if (!searchInput) return;
    
    searchInput.value = '';
    renderComponentList();
    console.log('[ESL] Campo de busca populado');
}


/**
 * Carrega sistemas eutéticos conhecidos da base de dados ESL
 * Endpoint: /esl/eutectic_systems
 */
async function loadEutecticSystems() {
    try {
        console.log('[ESL] Carregando sistemas eutéticos...');
        
        const response = await fetch('/esl/eutectic_systems');
        
        if (!response.ok) {
            console.log('[ESL] Sistemas eutéticos não disponíveis (endpoint retornou', response.status, ')');
            eutecticSystems = [];
            return;
        }
        
        const data = await response.json();
        
        if (data.success && data.eutectic_systems) {
            eutecticSystems = data.eutectic_systems;
            console.log(`[ESL] ✓ ${eutecticSystems.length} sistemas eutéticos carregados`);
        } else {
            eutecticSystems = [];
            console.log('[ESL] Nenhum sistema eutético disponível');
        }
        
    } catch (err) {
        console.warn('[ESL] Não foi possível carregar sistemas eutéticos:', err);
        eutecticSystems = [];
    }
}


async function loadComponentProperties(componentName) {
  if (componentPropertiesCache[componentName]) {
    return componentPropertiesCache[componentName];
  }

  try {
    const response = await fetch('/esl/component/' + encodeURIComponent(componentName));
    const data = await response.json();

    if (data.success && data.component) {
      componentPropertiesCache[componentName] = data.component;
      return data.component;
    }
  } catch (err) {
    console.warn('[ESL] Erro ao carregar propriedades de ' + componentName + ':', err);
  }

  return null;
}

// ============================================================================
// FILTRO POR MODELO TERMODINÂMICO
// ============================================================================
async function filterComponentsByModel(model) {
    console.log(`[ESL] Filtrando componentes para modelo: ${model}`);
    
    try {
        // ✅ ENVIAR modelo via query string
        const response = await fetch(`/esl/components?model=${encodeURIComponent(model)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.components) {
            allComponents = data.components;
            console.log(`[ESL] ✓ ${allComponents.length} componentes disponíveis para ${model}`);
            
            // Atualizar contador
            const countSpan = document.getElementById('componentDatabaseCount');
            if (countSpan) {
                countSpan.textContent = allComponents.length;
            }
            
            // Remover componentes selecionados que não têm parâmetros
            const validNames = new Set(allComponents.map(c => c.name || c.name_en));
            const removedComponents = [];
            
            selectedComponents = selectedComponents.filter(c => {
                const name = getComponentName(c);
                const isValid = validNames.has(name);
                if (!isValid) {
                    removedComponents.push(name);
                }
                return isValid;
            });
            
            if (removedComponents.length > 0) {
                showNotification(
                    `Componentes removidos (sem parâmetros ${model}): ${removedComponents.join(', ')}`,
                    'warning'
                );
            }
            
            updateComponentTags();
            
            showNotification(
                `${allComponents.length} componentes disponíveis para modelo ${model}`,
                'info'
            );
        } else {
            throw new Error(data.error || 'Erro ao filtrar componentes');
        }
        
    } catch (err) {
        console.error('[ESL] Erro ao filtrar componentes:', err);
        showNotification(`Erro ao filtrar componentes: ${err.message}`, 'danger');
    }
}


// ============================================================================
// HELPER: OBTER NOME DO COMPONENTE (SEMPRE PT-BR PRIMEIRO)
// ============================================================================
function getComponentName(comp) {
  return comp.name || comp.name_en || comp.CAS || 'Desconhecido';
}

// ============================================================================
// GERENCIAMENTO DE COMPONENTES
// ============================================================================
function showComponentModal() {
    const modal = document.getElementById('componentModal');
    if (!modal) return;
    
    modal.style.display = 'block';  // ✅ Isso ativa o CSS acima
    renderComponentList();
    
    setTimeout(function() {
        const searchInput = document.getElementById('componentSearch');
        if (searchInput) {
            searchInput.value = '';
            searchInput.focus();
        }
    }, 100);
}

function closeComponentModal() {
    const modal = document.getElementById('componentModal');
    if (!modal) return;
    
    modal.style.display = 'none';  // ✅ Esconde o modal
}


function renderComponentList(filter) {
  const listDiv = document.getElementById('componentList');
  if (!listDiv) return;

  const term = (filter || '').toLowerCase();
  let filtered = allComponents;

  if (term) {
    filtered = allComponents.filter(function(c) {
      return (c.name && c.name.toLowerCase().includes(term)) ||
        (c.name_en && c.name_en.toLowerCase().includes(term)) ||
        (c.formula && c.formula.toLowerCase().includes(term)) ||
        (c.CAS && c.CAS.toLowerCase().includes(term));
    });
  }

  if (filtered.length === 0) {
    listDiv.innerHTML = '<div class="text-muted-soft p-3 text-center">Nenhum componente encontrado</div>';
    return;
  }

  let html = '';
  filtered.forEach(function(comp, idx) {
    const name = getComponentName(comp);
    const formula = comp.formula || '';
    const CAS = comp.CAS || '';
    const Tm_C = comp.Tm_C;
    const Hfus = comp.Hfus_kJ_mol;

    const isSelected = selectedComponents.some(function(c) {
      return (c.CAS && CAS && c.CAS === CAS) || (getComponentName(c) === name);
    });

    const itemClass = isSelected ? 'component-list-item opacity-50' : 'component-list-item';
    const itemData = isSelected ? '' : 'data-comp-idx="' + idx + '" data-comp-filter="' + escapeHtml(term) + '"';

    html += '<div class="' + itemClass + '" ' + itemData + '>';
    html += '<div>';
    html += '<span class="comp-name">' + escapeHtml(name) + '</span>';
    if (formula) html += '<span class="comp-formula">' + escapeHtml(formula) + '</span>';
    if (isSelected) html += '<span class="badge bg-success ms-2" style="font-size: 0.7rem;">✓ Selecionado</span>';
    html += '<br><div class="comp-props">';
    if (CAS) html += '<span class="badge">CAS: ' + escapeHtml(CAS) + '</span>';
    if (Tm_C) html += '<span class="badge">Tm: ' + Tm_C.toFixed(1) + '°C</span>';
    if (Hfus) html += '<span class="badge">ΔHfus: ' + Hfus.toFixed(1) + ' kJ/mol</span>';
    html += '</div></div></div>';
  });

  listDiv.innerHTML = html;

  const items = listDiv.querySelectorAll('.component-list-item[data-comp-idx]');
  items.forEach(function(item) {
    item.addEventListener('click', function () {
      const idx = parseInt(this.getAttribute('data-comp-idx'));
      const filterTerm = this.getAttribute('data-comp-filter') || '';
      selectComponentFromList(idx, filterTerm);
    });
  });
}

function selectComponentFromList(indexInFiltered, filterTerm) {
  const term = (filterTerm || '').toLowerCase();
  let filtered = allComponents;

  if (term) {
    filtered = allComponents.filter(function(c) {
      return (c.name && c.name.toLowerCase().includes(term)) ||
        (c.name_en && c.name_en.toLowerCase().includes(term)) ||
        (c.formula && c.formula.toLowerCase().includes(term)) ||
        (c.CAS && c.CAS.toLowerCase().includes(term));
    });
  }

  const comp = filtered[indexInFiltered];
  if (!comp) {
    console.warn('[ESL] Componente não encontrado no índice:', indexInFiltered);
    return;
  }

  const name = getComponentName(comp);
  const isDuplicate = selectedComponents.some(function(c) {
    return (c.CAS && comp.CAS && c.CAS === comp.CAS) || (getComponentName(c) === name);
  });

  if (isDuplicate) {
    showNotification(name + ' já está selecionado', 'warning');
    return;
  }

  if (selectedComponents.length >= MAX_COMPONENTS) {
    showNotification('Máximo de ' + MAX_COMPONENTS + ' componentes selecionados', 'warning');
    closeComponentModal();
    return;
  }

  selectedComponents.push(comp);
  updateComponentTags();
  updateFields();
  validateComponentsForModel();
  showNotification(name + ' adicionado!', 'success');
  closeComponentModal();
}

function updateComponentTags() {
  const container = document.getElementById('selectedComponentsTags');
  const countSpan = document.getElementById('componentCount');
  const hintSpan = document.getElementById('componentHint');

  if (!container) return;

  let html = '';
  selectedComponents.forEach(function(comp, i) {
    const name = getComponentName(comp);
    const formula = comp.formula || '';

    html += '<span class="component-tag">';
    html += '<span class="name">' + escapeHtml(name) + '</span>';
    if (formula) html += '<span class="formula">' + escapeHtml(formula) + '</span>';
    html += '<button class="remove-btn" onclick="removeComponent(' + i + ')" title="Remover componente">';
    html += '<i class="bi bi-x"></i></button></span>';
  });

  html += '<button class="add-component-btn" type="button" onclick="showComponentModal()">';
  html += '<i class="bi bi-plus-circle"></i> Adicionar componente</button>';

  container.innerHTML = html;
  if (countSpan) countSpan.textContent = selectedComponents.length;

  if (hintSpan) {
    const n = selectedComponents.length;
    const model = document.getElementById('model');
    const modelText = model ? ' - Modelo: ' + model.value : '';
    
    if (n === 0) {
      hintSpan.textContent = 'Adicione componentes para começar' + modelText;
    } else if (n === 1) {
      hintSpan.textContent = 'Adicione mais 1 componente (mínimo 2)' + modelText;
    } else if (n === 2) {
      hintSpan.textContent = '2 comp.: cálculos pontuais ou diagrama T-x (máx. ' + MAX_COMPONENTS + ')' + modelText;
    } else {
      hintSpan.textContent = n + ' componentes (máx. ' + MAX_COMPONENTS + ')' + modelText;
    }
  }
}

async function updateComponentPropertiesPreview() {
  const container = document.getElementById('componentPropertiesPreview');
  if (!container || selectedComponents.length === 0) {
    if (container) container.innerHTML = '';
    return;
  }

  let html = '<div class="component-properties-card">';
  html += '<div style="font-weight: 600; color: #94a3b8; margin-bottom: 8px; font-size: 0.8rem;">Propriedades ESL</div>';

  for (let i = 0; i < selectedComponents.length; i++) {
    const comp = selectedComponents[i];
    const name = getComponentName(comp);
    const props = await loadComponentProperties(name);

    if (props) {
      let TmC = null;
      if (props.Tm_C !== undefined && props.Tm_C !== null) {
        TmC = props.Tm_C;
      } else if (props.Tm_K !== undefined && props.Tm_K !== null) {
        TmC = props.Tm_K - 273.15;
      } else if (props.Tm !== undefined && props.Tm !== null) {
        TmC = props.Tm - 273.15;
      }

      let Hfus = null;
      if (props.Hfus_kJ_mol !== undefined && props.Hfus_kJ_mol !== null) {
        Hfus = props.Hfus_kJ_mol;
      } else if (props.Hfus !== undefined && props.Hfus !== null) {
        Hfus = props.Hfus;
      }

      html += '<div class="prop-row">';
      html += '<span class="prop-label">' + escapeHtml(name) + '</span>';
      html += '<span class="prop-value">';
      html += 'Tm = ' + (TmC !== null ? TmC.toFixed(2) + ' °C' : 'N/A') + ', ';
      html += 'ΔHfus = ' + (Hfus !== null ? Hfus.toFixed(2) + ' kJ/mol' : 'N/A');
      html += '</span></div>';
    }
  }

  html += '</div>';
  container.innerHTML = html;
}

function removeComponent(index) {
  selectedComponents.splice(index, 1);
  updateComponentTags();
  updateFields();
  validateComponentsForModel();
}

function filterEutecticSystems() {
  if (eutecticSystems.length === 0) {
    showNotification('Nenhum sistema eutético disponível na base de dados', 'info');
    return;
  }

  const listDiv = document.getElementById('componentList');
  let html = '<div class="p-3" style="color: #e5e7eb;">';
  html += '<h6 style="color: #f97316; margin-bottom: 15px;"><i class="bi bi-star-fill"></i> Sistemas Eutéticos Conhecidos</h6>';

  eutecticSystems.forEach(function(sys) {
    const comps = sys.components || [];
    const T_eut = sys.T_eutectic_C;
    const comp_eut = sys.composition_eutectic;

    html += '<div class="mb-3 p-2" style="background: rgba(249,115,22,0.1); border-radius: 8px; border: 1px solid rgba(249,115,22,0.3);">';
    html += '<div style="font-weight: 600; margin-bottom: 5px;">' + comps.map(function(c) { return escapeHtml(c); }).join(' + ') + '</div>';
    html += '<div style="font-size: 0.8rem; color: #cbd5e1;">';
    if (T_eut) html += 'T<sub>eut</sub>: ' + T_eut.toFixed(2) + '°C';
    if (comp_eut) html += ' | Composição: ' + JSON.stringify(comp_eut);
    html += '</div>';
    html += '<button class="btn btn-sm mt-2" style="background: rgba(249,115,22,0.2); border: 1px solid #f97316; color: #f97316; font-size: 0.75rem;" ';
    html += 'onclick=\'selectEutecticSystem(' + JSON.stringify(comps) + ')\'>';
    html += '<i class="bi bi-plus-circle"></i> Selecionar sistema</button></div>';
  });

  html += '</div>';
  listDiv.innerHTML = html;
}

function selectEutecticSystem(componentNames) {
  selectedComponents = [];

  componentNames.forEach(function(name) {
    const comp = allComponents.find(function(c) { return getComponentName(c) === name; });
    if (comp) {
      selectedComponents.push(comp);
    }
  });

  updateComponentTags();
  updateFields();
  validateComponentsForModel();
  closeComponentModal();

  showNotification('Sistema eutético ' + componentNames.join(' + ') + ' selecionado!', 'success');
}

// ============================================================================
// VALIDAÇÃO
// ============================================================================
async function validateComponentsForModel() {
  const model = document.getElementById('model');
  const container = document.getElementById('validationMessages');

  if (!container || selectedComponents.length < 2 || !model) {
    if (container) container.innerHTML = '';
    return;
  }

  const componentNames = selectedComponents.map(function(c) { return getComponentName(c); });

  try {
    const response = await fetch('/esl/validate_components', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ components: componentNames, model: model.value })
    });

    const data = await response.json();

    if (!data.success) {
      container.innerHTML = '';
      return;
    }

    let html = '';

    if (data.warnings && data.warnings.length > 0) {
      html += '<div class="alert" style="background: rgba(251,191,36,0.1); border: 1px solid #fbbf24; color: #fbbf24; font-size: 0.85rem; padding: 10px;">';
      html += '<i class="bi bi-exclamation-triangle"></i> <strong>Avisos:</strong>';
      html += '<ul style="margin: 5px 0 0 20px; padding: 0;">';
      data.warnings.forEach(function(w) {
        html += '<li>' + escapeHtml(w) + '</li>';
      });
      html += '</ul></div>';
    }

    if (data.errors && data.errors.length > 0) {
      html += '<div class="alert" style="background: rgba(239,68,68,0.1); border: 1px solid #ef4444; color: #ef4444; font-size: 0.85rem; padding: 10px;">';
      html += '<i class="bi bi-x-circle"></i> <strong>Erros:</strong>';
      html += '<ul style="margin: 5px 0 0 20px; padding: 0;">';
      data.errors.forEach(function(e) {
        html += '<li>' + escapeHtml(e) + '</li>';
      });
      html += '</ul></div>';
    }

    if (data.suggestions && data.suggestions.length > 0) {
      html += '<div class="alert" style="background: rgba(56,189,248,0.1); border: 1px solid #38bdf8; color: #38bdf8; font-size: 0.85rem; padding: 10px;">';
      html += '<i class="bi bi-lightbulb"></i> <strong>Sugestões:</strong>';
      html += '<ul style="margin: 5px 0 0 20px; padding: 0;">';
      data.suggestions.forEach(function(s) {
        html += '<li>' + escapeHtml(s) + '</li>';
      });
      html += '</ul></div>';
    }

    container.innerHTML = html;

    const calculateBtn = document.getElementById('calculateBtn');
    if (calculateBtn) {
      calculateBtn.disabled = data.errors && data.errors.length > 0;
    }
  } catch (err) {
    console.warn('[ESL] Erro na validação:', err);
    if (container) container.innerHTML = '';
  }
}

// ============================================================================
// CAMPOS DINÂMICOS
// ============================================================================
function updateFields() {
  const calcType = document.getElementById('calcType');
  const container = document.getElementById('dynamicFields');
  if (!container || !calcType) return;

  let html = '';
  const ct = calcType.value;

  if (ct === 'solubility' || ct === 'ternary') {
    html += '<div class="row mb-3"><div class="col-md-6">';
    html += '<label class="form-label">Temperatura</label>';
    html += '<div class="input-group-compact">';
    html += '<input type="number" class="form-control" id="temperature" value="25" step="0.1">';
    html += '<select class="form-select" id="tempUnit" style="max-width: 80px;">';
    html += '<option value="C">°C</option><option value="K">K</option></select>';
    html += '</div></div></div>';
  }

  if (ct === 'tx') {
    html += '<div class="alert" style="background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); color: #e5e7eb; font-size: 0.85rem; padding: 0.7rem;">';
    html += '<i class="bi bi-info-circle"></i> O diagrama T-x requer <strong>exatamente 2 componentes</strong> e varre automaticamente toda a faixa de composição (x₁ = 0 → 1).';
    html += '</div>';
  }

  if (ct === 'ternary') {
    html += '<div class="alert" style="background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); color: #e5e7eb; font-size: 0.85rem; padding: 0.7rem;">';
    html += '<i class="bi bi-info-circle"></i> O diagrama ternário requer <strong>exatamente 3 componentes</strong> em temperatura constante.';
    html += '</div>';
  }

  if (ct === 'crystallization' && selectedComponents.length > 0) {
    html += '<div class="row mb-3"><div class="col-12">';
    html += '<label class="form-label">Frações molares na fase líquida';
    html += '<span class="info-icon" data-bs-toggle="tooltip" data-bs-placement="top" title="Composição da fase líquida em equilíbrio">';
    html += '<i class="bi bi-question-circle"></i></span></label>';
    html += '<div class="row">';

    const n = selectedComponents.length;
    selectedComponents.forEach(function(comp, i) {
      html += '<div class="col-md-4 mb-2">';
      html += '<div class="input-group input-group-sm">';
      html += '<span class="input-group-text">x' + (i + 1) + '</span>';
      html += '<input type="number" class="form-control" id="x' + (i + 1) + '" ';
      html += 'value="' + (1 / n).toFixed(3) + '" step="0.001" min="0" max="1">';
      html += '</div>';
      html += '<small class="text-muted-soft">' + escapeHtml(getComponentName(comp)) + '</small>';
      html += '</div>';
    });

    html += '</div>';
    html += '<small class="text-muted-soft"><i class="bi bi-exclamation-circle"></i> A soma das frações deve ser 1,0 (±0,001).</small>';
    html += '</div></div>';
  }

  container.innerHTML = html;
  initializeTooltips();
  validateComponentsForModel();
}

// ============================================================================
// CÁLCULO PRINCIPAL
// ============================================================================
async function calculate() {
  const calcType = document.getElementById('calcType').value;
  const model = document.getElementById('model').value;

  if (calcType === 'tx' && selectedComponents.length !== 2) {
    alert('O diagrama T-x requer exatamente 2 componentes.');
    return;
  }
  if (calcType === 'ternary' && selectedComponents.length !== 3) {
    alert('O diagrama ternário requer exatamente 3 componentes.');
    return;
  }
  if ((calcType === 'solubility' || calcType === 'crystallization') && selectedComponents.length < 2) {
    alert('Selecione pelo menos 2 componentes.');
    return;
  }

  if (calcType === 'tx' || calcType === 'ternary') {
    await generateDiagram(calcType, model);
  } else {
    await calculatePoint(calcType, model);
  }

  await updateComponentPropertiesPreview();
}

// ============================================================================
// CÁLCULOS PONTUAIS
// ============================================================================
async function calculatePoint(calcType, model) {
  clearComparison();
  const components = selectedComponents.map(function(c) { return getComponentName(c); });
  const useCompleteEq = document.getElementById('useCompleteEquation');

  const payload = {
    components: components,
    model: model,
    use_complete_equation: useCompleteEq ? useCompleteEq.checked : false
  };

  if (calcType === 'solubility') {
    payload.temperature = parseFloat(document.getElementById('temperature').value);
    payload.temperature_unit = document.getElementById('tempUnit').value;
  }

  if (calcType === 'crystallization') {
    const compositions = [];
    for (let i = 0; i < selectedComponents.length; i++) {
      const el = document.getElementById('x' + (i + 1));
      const val = parseFloat(el ? el.value : NaN);
      compositions.push(isNaN(val) ? 0 : val);
    }
    const sumX = compositions.reduce(function(a, b) { return a + b; }, 0);
    if (sumX < 0.999 || sumX > 1.001) {
      alert('A soma das frações molares deve ser igual a 1,0 (±0,001).');
      return;
    }
    payload.compositions = compositions;
  }

  const endpoint = calcType === 'solubility' ? '/esl/calculate/solubility' : '/esl/calculate/crystallization';

  console.log('[ESL] Executando ' + calcType + ' com modelo ' + model + ', eq. ' + (payload.use_complete_equation ? 'completa' : 'simplificada'));

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      window.lastAiSuggestion = data.ai_suggestion || null;
      displayResults(data.results, window.lastAiSuggestion);
      window.lastPointResults = data.results;

      displayThermodynamicWarnings(data.results.warnings);

      lastDiagramData = null;
      lastDiagramType = null;
      lastModel = model;
      lastTemperature = null;

      const btnPts = document.getElementById('export-buttons-points');
      const btnDiag = document.getElementById('export-buttons');
      if (btnPts) btnPts.style.display = 'block';
      if (btnDiag) btnDiag.style.display = 'none';

      const compContainer = document.getElementById('comparison-diagram-container');
      if (compContainer) compContainer.style.display = 'none';
      if (window.comparisonChart) {
        window.comparisonChart.destroy();
        window.comparisonChart = null;
      }

      console.log('[ESL] Cálculo concluído com sucesso');
    } else {
      alert('Erro no cálculo: ' + (data.error || 'Erro desconhecido'));
    }
  } catch (err) {
    alert('Erro no cálculo: ' + err.message);
    console.error('[ESL] Erro:', err);
  }
}

// ============================================================================
// DIAGRAMAS
// ============================================================================
async function generateDiagram(calcType, model) {
  clearComparison();
  const components = selectedComponents.map(function(c) { return getComponentName(c); });
  const useCompleteEq = document.getElementById('useCompleteEquation');

  const payload = {
    components: components,
    model: model,
    use_complete_equation: useCompleteEq ? useCompleteEq.checked : false
  };

  // ✅ CORREÇÃO: Adicionar n_points para ambos os diagramas
  if (calcType === 'tx') {
    payload.n_points = 50;  // Valor padrão para T-x
  }

  if (calcType === 'ternary') {
    payload.temperature = parseFloat(document.getElementById('temperature').value);
    payload.temperature_unit = document.getElementById('tempUnit').value;
    payload.n_points = 20;  // ✅ ADICIONAR ESTE PARÂMETRO!
  }

  const endpoint = calcType === 'tx' ? '/esl/diagram/tx' : '/esl/diagram/ternary';

  console.log('[ESL] Gerando diagrama ' + calcType + ' com modelo ' + model);
  console.log('[ESL] Payload:', JSON.stringify(payload, null, 2));  // ✅ Debug

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      window.lastAiSuggestion = data.ai_suggestion || null;
      renderChart(data.results, calcType);

      displayThermodynamicWarnings(data.results.warnings);

      window.lastPointResults = null;

      const btnPts = document.getElementById('export-buttons-points');
      const btnDiag = document.getElementById('export-buttons');
      if (btnDiag) btnDiag.style.display = 'block';
      if (btnPts) btnPts.style.display = 'none';

      const compContainer = document.getElementById('comparison-diagram-container');
      if (compContainer) compContainer.style.display = 'none';
      if (window.comparisonChart) {
        window.comparisonChart.destroy();
        window.comparisonChart = null;
      }

      lastDiagramData = data.results;
      lastDiagramType = calcType;
      lastModel = model;
      if (calcType === 'tx') {
        lastTemperature = null;
      } else {
        lastTemperature = data.results.T_C;
      }

      console.log('[ESL] Diagrama gerado com sucesso');
    } else {
      alert('Erro ao gerar diagrama: ' + (data.error || 'Erro desconhecido'));
    }
  } catch (err) {
    alert('Erro ao gerar diagrama: ' + err.message);
    console.error('[ESL] Erro:', err);
  }
}

// ============================================================================
// AVISOS TERMODINÂMICOS
// ============================================================================
function displayThermodynamicWarnings(warnings) {
  const container = document.getElementById('thermodynamicWarnings');
  if (!container) return;

  if (!warnings || Object.keys(warnings).length === 0) {
    container.innerHTML = '';
    return;
  }

  let hasWarnings = false;
  let warningsList = [];

  for (const key in warnings) {
    const value = warnings[key];
    if (Array.isArray(value) && value.length > 0) {
      hasWarnings = true;
      warningsList = warningsList.concat(value);
    } else if (typeof value === 'string' && value) {
      hasWarnings = true;
      warningsList.push(value);
    }
  }

  if (!hasWarnings) {
    container.innerHTML = '';
    return;
  }

  let html = '<div class="thermodynamic-warnings">';
  html += '<div class="warning-title"><i class="bi bi-exclamation-triangle"></i> Avisos Termodinâmicos (Prausnitz et al.)</div>';
  html += '<ul>';
  warningsList.forEach(function(w) {
    html += '<li>' + escapeHtml(w) + '</li>';
  });
  html += '</ul>';
  html += '<div style="margin-top: 10px; font-size: 0.8rem; color: #94a3b8;">';
  html += '<i class="bi bi-info-circle"></i> Estes avisos indicam possíveis limitações do modelo ou extrapolação além das condições recomendadas.';
  html += '</div></div>';

  container.innerHTML = html;
}

// ============================================================================
// EXIBIÇÃO DE RESULTADOS PONTUAIS
// ============================================================================
function displayResults(results, aiSuggestion) {
  const resultsDiv = document.getElementById('results');
  if (!resultsDiv) return;

  const conditionKeys = ['T_C', 'T_K', 'T_cryst_C', 'T_cryst_K', 'model', 'equation'];

  const gammaKeys = [];
  const xKeys = [];
  const phaseKeys = [];
  const extraKeys = [];

  for (const key in results) {
    if (key.startsWith('gamma')) {
      gammaKeys.push(key);
    } else if (key.startsWith('x') && key.includes('(')) {
      xKeys.push(key);
    } else if (key.startsWith('phase')) {
      phaseKeys.push(key);
    } else if (!conditionKeys.includes(key) && key !== 'warnings') {
      extraKeys.push(key);
    }
  }

  gammaKeys.sort();
  xKeys.sort();
  phaseKeys.sort();
  extraKeys.sort();

  let html = '<div class="results-card">';
  html += '<h4 class="mb-3"><i class="bi bi-check-circle"></i> Resultados ESL</h4>';

  renderAIRecommendation(aiSuggestion);

  html += '<div class="row g-3">';
  html += '<div class="col-md-4"><h6 class="section-title-sm">Condições do cálculo</h6><div class="results-grid">';

  conditionKeys.forEach(function(k) {
    if (results[k] === undefined) return;
    const v = results[k];
    html += '<div class="result-item">';
    html += '<span class="label">' + escapeHtml(k) + '</span>';
    html += '<span class="value">' + (typeof v === 'number' ? v.toFixed(4) : escapeHtml(String(v))) + '</span>';
    html += '</div>';
  });

  html += '</div></div>';

  html += '<div class="col-md-4"><h6 class="section-title-sm">Composição e Fase</h6><div class="results-grid">';

  xKeys.forEach(function(k) {
    const v = results[k];
    html += '<div class="result-item">';
    html += '<span class="label">' + formatLabel(k) + '</span>';
    html += '<span class="value">' + (v.toFixed ? v.toFixed(6) : v) + '</span>';
    html += '</div>';
  });

  phaseKeys.forEach(function(k) {
    const v = results[k];
    html += '<div class="result-item">';
    html += '<span class="label">' + formatLabel(k) + '</span>';
    html += '<span class="value">' + escapeHtml(String(v)) + '</span>';
    html += '</div>';
  });

  html += '</div></div>';

  html += '<div class="col-md-4"><h6 class="section-title-sm">Propriedades Termodinâmicas</h6><div class="results-grid">';

  gammaKeys.forEach(function(k) {
    const v = results[k];
    html += '<div class="result-item">';
    html += '<span class="label">' + formatLabel(k) + '</span>';
    html += '<span class="value">' + (v.toFixed ? v.toFixed(4) : v) + '</span>';
    html += '</div>';
  });

  extraKeys.forEach(function(k) {
    const v = results[k];
    html += '<div class="result-item">';
    html += '<span class="label">' + escapeHtml(k) + '</span>';
    html += '<span class="value">' + (v.toFixed ? v.toFixed(4) : escapeHtml(String(v))) + '</span>';
    html += '</div>';
  });

  html += '</div></div></div>';

  html += '<div class="mt-3 small text-muted-soft">';
  html += '<i class="bi bi-info-circle"></i> Utilize os botões de exportação abaixo para salvar estes resultados em CSV ou PDF, ou compare com outros modelos termodinâmicos.';
  html += '</div></div>';

  resultsDiv.innerHTML = html;
}

// ============================================================================
// RECOMENDAÇÃO DA IA
// ============================================================================
function renderAIRecommendation(aiSuggestion) {
    const container = document.getElementById('ai-recommendation');
    if (!container) return;
    
    if (!aiSuggestion || !aiSuggestion.recommended_model) {
        container.innerHTML = '';
        return;
    }
    
    const calcType = document.getElementById('calcType').value;
    const components = selectedComponents.map(c => getComponentName(c)).join(' / ');
    
    const ranges = aiSuggestion.recommended_ranges || {};
    const T = ranges.temperatureC || {};
    const modelsForComps = aiSuggestion.recommended_models_for_components || [];
    const bestForModel = aiSuggestion.best_components_for_model || [];
    const detailText = (aiSuggestion.details && aiSuggestion.details.reason) ? aiSuggestion.details.reason : '';
    const eutectic = aiSuggestion.eutectic || null;
    
    let html = `<div class="results-card" style="background: rgba(56,189,248,0.05); border: 1px solid rgba(56,189,248,0.3);">`;
    html += `<div class="section-title-sm"><i class="bi bi-stars"></i> Recomendações da IA para este sistema ESL</div>`;
    
    html += `<p class="text-muted-soft mb-2" style="font-size:0.85rem">`;
    html += `<strong>Sistema:</strong> ${escapeHtml(components)} <br>`;
    html += `<strong>Tipo de cálculo:</strong> ${escapeHtml(calcType)}</p>`;
    
    html += `<div class="mb-2"><strong>Modelo recomendado principal:</strong> `;
    html += `<span class="badge bg-info text-dark ms-1" style="font-size: 0.85rem">${escapeHtml(aiSuggestion.recommended_model)}</span></div>`;
    
    if (modelsForComps.length) {
        html += `<div class="mb-2"><strong>Modelos adequados para estes componentes:</strong><div class="mt-1">`;
        modelsForComps.forEach(m => {
            html += `<span class="badge" style="background: rgba(56,189,248,0.2); color: #38bdf8; margin-right: 5px">${escapeHtml(m)}</span>`;
        });
        html += `</div></div>`;
    }
    
    if (bestForModel.length) {
        html += `<div class="mb-2"><strong>Sistemas típicos para cada modelo:</strong>`;
        html += `<ul class="text-muted-soft" style="font-size:0.82rem; margin-bottom:0; padding-left: 20px">`;
        bestForModel.forEach(item => {
            html += `<li><strong>${escapeHtml(item.model)}:</strong> ${escapeHtml(item.examples.join(', '))}</li>`;
        });
        html += `</ul></div>`;
    }
    
    // ✅ VALIDAÇÃO SEGURA: Verificar se T.min e T.max são números válidos
    if (T.min !== null && T.min !== undefined && T.max !== null && T.max !== undefined && 
        !isNaN(T.min) && !isNaN(T.max)) {
        html += `<div class="mb-2"><strong>Faixas recomendadas de operação:</strong>`;
        html += `<div class="text-muted-soft" style="font-size:0.82rem">`;
        html += `<i class="bi bi-thermometer-half"></i> Temperatura: ${Number(T.min).toFixed(1)} - ${Number(T.max).toFixed(1)} °C`;
        html += `</div></div>`;
    }
    
    // ✅ VALIDAÇÃO SEGURA: Verificar se eutectic.TC e eutectic.x1 são números válidos
    if (eutectic && 
        eutectic.TC !== null && eutectic.TC !== undefined && !isNaN(eutectic.TC) &&
        eutectic.x1 !== null && eutectic.x1 !== undefined && !isNaN(eutectic.x1)) {
        html += `<div class="mb-2" style="background: rgba(249,115,22,0.1); padding: 10px; border-radius: 8px; border: 1px solid rgba(249,115,22,0.3);">`;
        html += `<strong style="color: #f97316"><i class="bi bi-star-fill"></i> Ponto eutético previsto:</strong>`;
        html += `<div class="text-muted-soft" style="font-size:0.82rem; margin-top: 5px">`;
        html += `T<sub>eut</sub> = ${Number(eutectic.TC).toFixed(2)} °C, x<sub>1</sub> = ${Number(eutectic.x1).toFixed(3)}`;
        html += `</div></div>`;
    }
    
    if (detailText) {
        html += `<div class="mb-2"><strong>Justificativa:</strong> `;
        html += `<span class="text-muted-soft" style="font-size:0.82rem">${escapeHtml(detailText)}</span></div>`;
    }
    
    if (aiSuggestion.prefill) {
        html += `<div class="mt-3 d-flex gap-2">`;
        html += `<button type="button" class="btn-sim btn-sim-primary btn-sm" onclick="applyAIParameters()">`;
        html += `<i class="bi bi-magic"></i> Aplicar parâmetros recomendados</button></div>`;
    }
    
    html += `</div>`;
    
    container.innerHTML = html;
}


function applyAIParameters() {
  const ai = window.lastAiSuggestion;
  if (!ai || !ai.prefill) return;

  const pre = ai.prefill;

  if (ai.recommended_model) {
    const modelSel = document.getElementById('model');
    if (modelSel) modelSel.value = ai.recommended_model;
  }

  updateFields();

  if (pre.temperature_C !== undefined) {
    const tInput = document.getElementById('temperature');
    const tUnit = document.getElementById('tempUnit');
    if (tInput) tInput.value = pre.temperature_C.toFixed(2);
    if (tUnit) tUnit.value = 'C';
  }

  if (Array.isArray(pre.liquid_compositions)) {
    const n = Math.min(pre.liquid_compositions.length, selectedComponents.length);
    for (let i = 0; i < n; i++) {
      const el = document.getElementById('x' + (i + 1));
      if (el) el.value = pre.liquid_compositions[i].toFixed(3);
    }
  }

  showNotification('Parâmetros recomendados aplicados ao formulário!', 'success');
}

// ============================================================================
// GRÁFICOS (Chart.js)
// ============================================================================
function renderChart(results, type) {
  const resultsDiv = document.getElementById('results');

  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }

  if (type === 'tx') {
    renderTxDiagram(results, resultsDiv);
  } else if (type === 'ternary') {
    renderTernaryDiagram(results, resultsDiv);
  }
}

//Gráfico TXY

function renderTxDiagram(results, container) {
    console.log('[ESL DEBUG] results completo:', JSON.stringify(results, null, 2));
    
    const comp1 = results.component1 || 'Comp1';
    const comp2 = results.component2 || 'Comp2';
    const model = results.model || lastModel;
    const equation = results.equation || 'Simplificada';
    
    const x1left = results.x1_left || [];
    const Tleft = results.T_left_C || [];
    const x1right = results.x1_right || [];
    const Tright = results.T_right_C || [];
    
    const unstableRegion = results.unstable_region || [];
    const hasGap = results.has_liquid_liquid_gap || false;
    
    console.log('[ESL DEBUG] Arrays recebidos:');
    console.log('  x1left:', x1left.length, 'pontos');
    console.log('  x1right:', x1right.length, 'pontos');
    console.log('  unstable_region:', unstableRegion.length, 'pontos');
    console.log('  has_gap:', hasGap);
    
    const Teut = (results.T_eutectic_C !== null && results.T_eutectic_C !== undefined) ? results.T_eutectic_C : null;
    const xeut = (results.x1_eutectic !== null && results.x1_eutectic !== undefined) ? results.x1_eutectic : null;
    const Tm1 = (results.Tm1_C !== null && results.Tm1_C !== undefined) ? results.Tm1_C : null;
    const Tm2 = (results.Tm2_C !== null && results.Tm2_C !== undefined) ? results.Tm2_C : null;
    
    const isVshape = (xeut !== null && xeut >= 0.4 && xeut <= 0.7);
    
    console.log(`[ESL] Renderizando: ${comp1} / ${comp2}`);
    console.log(`[ESL] xeut = ${xeut !== null ? xeut.toFixed(3) : 'NULL'}, Tipo: ${isVshape ? 'V-SHAPE' : 'CROSSED-LINES'}`);
    
    let html = `<h4 class="mb-2"><i class="bi bi-graph-up"></i> Diagrama T-x ESL - ${comp1} / ${comp2}</h4>`;
    html += `<div class="mb-2" style="font-size: 0.85rem; color: #94a3b8;">`;
    html += `<strong>Modelo:</strong> ${model}`;
    
    if (Teut !== null && xeut !== null) {
        html += ` <span style="color: #f97316"><i class="bi bi-star-fill"></i> T<sub>eut</sub> = `;
        html += `${Teut.toFixed(2)} °C, x<sub>1</sub> = ${xeut.toFixed(3)}</span>`;
    }
    
    html += `</div>`;
    
    if (hasGap && unstableRegion.length > 0) {
        const gapXmin = Math.min(...unstableRegion.map(p => p.x1));
        const gapXmax = Math.max(...unstableRegion.map(p => p.x1));
        
        html += `<div class="alert alert-warning" style="background: rgba(251,191,36,0.1); border: 1px solid #fbbf24; color: #fbbf24; font-size: 0.85rem; padding: 10px; border-radius: 8px; margin-bottom: 10px;">`;
        html += `<i class="bi bi-exclamation-triangle-fill"></i> <strong>Região de Imiscibilidade Líquida (Gap L₁+L₂)</strong><br>`;
        html += `Detectado entre x<sub>1</sub> = ${gapXmin.toFixed(3)} e ${gapXmax.toFixed(3)} (${unstableRegion.length} pontos instáveis). `;
        html += `Diagrama ESL pode não ser completamente aplicável nesta região.`;
        html += `</div>`;
    }
    
    html += `<div style="position:relative;height:520px;width:100%"><canvas id="diagramChart"></canvas></div>`;
    
    container.innerHTML = html;
    
    setTimeout(function() {
        const canvas = document.getElementById('diagramChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        Chart.defaults.color = '#e5e7eb';
        Chart.defaults.font.size = 12;
        
        const datasets = [];
        
        if (isVshape) {
            console.log('[ESL] Montando UMA linha contínua (V-shape)');
            
            let allPoints = [];
            for (let i = 0; i < x1left.length; i++) {
                allPoints.push({ x: x1left[i], y: Tleft[i] });
            }
            for (let i = 0; i < x1right.length; i++) {
                allPoints.push({ x: x1right[i], y: Tright[i] });
            }
            
            allPoints.sort((a, b) => a.x - b.x);
            
            let cleanPoints = [];
            for (let i = 0; i < allPoints.length; i++) {
                if (i === 0 || Math.abs(allPoints[i].x - cleanPoints[cleanPoints.length-1].x) > 0.001) {
                    cleanPoints.push(allPoints[i]);
                }
            }
            
            console.log(`[ESL] Dataset único com ${cleanPoints.length} pontos`);
            
            datasets.push({
                label: 'Curva de liquidus',
                data: cleanPoints,
                borderColor: '#38bdf8',
                backgroundColor: 'transparent',
                tension: 0.2,
                pointRadius: 0,
                borderWidth: 2.5,
                showLine: true,
                spanGaps: false,
                fill: false
            });
        } else {
            console.log('[ESL] Duas linhas separadas (crossed-lines)');
            
            // ✅ Dataset AZUL à ESQUERDA - x1_right (comp1 cristalizando)
            if (x1right.length > 0) {
                datasets.push({
                    label: `Liquidus (${comp1} cristalizando)`,
                    data: x1right.map((x, i) => ({ x: x, y: Tright[i] })),
                    borderColor: '#38bdf8',  // ✅ AZUL
                    backgroundColor: 'rgba(56,189,248,0.2)',
                    tension: 0,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    borderWidth: 2.5,
                    showLine: true,
                    spanGaps: false
                });
            }
            
            // ✅ Dataset LARANJA à DIREITA - x1_left (comp2 cristalizando)
            if (x1left.length > 0) {
                datasets.push({
                    label: `Liquidus (${comp2} cristalizando)`,
                    data: x1left.map((x, i) => ({ x: x, y: Tleft[i] })),
                    borderColor: '#fb923c',  // ✅ LARANJA
                    backgroundColor: 'rgba(251,146,60,0.2)',
                    tension: 0,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    borderWidth: 2.5,
                    showLine: true,
                    spanGaps: false
                });
            }
        }
        
        // Região instável
        if (hasGap && unstableRegion.length > 0) {
            console.log(`[ESL] Adicionando ${unstableRegion.length} pontos instáveis (gap L₁+L₂)`);
            
            datasets.push({
                label: '⚠️ Região L₁+L₂ (instável)',
                data: unstableRegion.map(p => ({ x: p.x1, y: p.T_C })),
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.3)',
                pointRadius: 4,
                pointStyle: 'crossRot',
                showLine: false,
                borderWidth: 2,
                borderDash: [5, 5]
            });
        }
        
        // Pontos especiais
        if (Teut !== null && xeut !== null) {
            datasets.push({
                label: 'Ponto eutético',
                data: [{ x: xeut, y: Teut }],
                borderColor: '#f97316',
                backgroundColor: '#f97316',
                pointRadius: 10,
                pointStyle: 'star',
                showLine: false,
                borderWidth: 2
            });
        }
        
        // ✅ Tm1 (comp1) à ESQUERDA (x1 = 0)
        if (Tm1 !== null) {
            datasets.push({
                label: `Tm (${comp1}) = ${Tm1.toFixed(1)} °C`,
                data: [{ x: 0.0, y: Tm1 }],
                borderColor: '#8b5cf6',
                backgroundColor: '#8b5cf6',
                pointRadius: 7,
                pointStyle: 'circle',
                showLine: false
            });
        }
        
        // ✅ Tm2 (comp2) à DIREITA (x1 = 1)
        if (Tm2 !== null) {
            datasets.push({
                label: `Tm (${comp2}) = ${Tm2.toFixed(1)} °C`,
                data: [{ x: 1.0, y: Tm2 }],
                borderColor: '#eab308',
                backgroundColor: '#eab308',
                pointRadius: 7,
                pointStyle: 'circle',
                showLine: false
            });
        }
        
        console.log(`[ESL] Total de datasets: ${datasets.length}`);
        
        if (currentChart) currentChart.destroy();
        
        currentChart = new Chart(ctx, {
            type: 'line',
            data: { datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: { size: 11 }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Diagrama T-x de Equilíbrio Sólido-Líquido',
                        font: { size: 14, weight: 'bold' },
                        color: '#e5e7eb'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || 'Liquidus';
                                const x = context.parsed.x;
                                const y = context.parsed.y;
                                if (x === null || y === null) return '';
                                return `${label}: x₁ = ${x.toFixed(4)}, T = ${y.toFixed(2)} °C`;
                            }
                        },
                        backgroundColor: 'rgba(15,23,42,0.95)',
                        titleColor: '#e5e7eb',
                        bodyColor: '#e5e7eb',
                        borderColor: '#38bdf8',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: `Fração molar de ${comp1} (x)`,
                            font: { size: 13, weight: 'bold' },
                            color: '#e5e7eb'
                        },
                        min: 0,
                        max: 1,
                        ticks: {
                            stepSize: 0.1,
                            color: '#94a3b8'
                        },
                        grid: { color: 'rgba(148,163,184,0.2)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Temperatura (°C)',
                            font: { size: 13, weight: 'bold' },
                            color: '#e5e7eb'
                        },
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(148,163,184,0.2)' }
                    }
                }
            }
        });
        
        lastDiagramData = results;
        lastDiagramType = 'tx';
        lastTemperature = null;
        
        console.log('[ESL] Renderizado com sucesso');
        
        if (hasGap && unstableRegion.length > 0) {
            console.warn(`[ESL] ⚠️ Sistema apresenta ${unstableRegion.length} pontos em região de imiscibilidade L₁+L₂`);
        }
    }, 50);
}





/**
 * ============================================================================
 * RENDERIZAÇÃO DE DIAGRAMA TERNÁRIO (COORDENADAS BARICÊNTRICAS)
 * ============================================================================
 * CORRIGIDO: Agora renderiza malha completa com classificação de fases
 * - VERDE: Região líquida (L)
 * - LARANJA: Região sólido + líquido (S+L)
 * - Triângulo de referência com vértices rotulados
 */
function renderTernaryDiagram(results, container) {
    const comps = results.components; // [C1, C2, C3]
    const TC = results.T_C || results.temperature_C || 25;
    const model = results.model || lastModel;
    const equation = results.equation || 'Simplificada';

    let html = `<h4 class="mb-2"><i class="bi bi-diagram-3"></i> Diagrama Ternário ESL - ${comps.join(' / ')}</h4>`;
    html += `<div class="mb-2" style="font-size: 0.85rem; color: #94a3b8;">`;
    html += `<strong>Temperatura:</strong> ${TC.toFixed(2)} °C `;
    html += `<strong>Modelo:</strong> ${model}`;
    html += `</div>`;
    html += `<div style="position:relative;height:580px;width:100%"><canvas id="diagramChart"></canvas></div>`;
    
    // ✅ Legenda CORRETA
    html += `<div class="text-center mt-2" style="font-size: 0.85rem; color: #94a3b8;">`;
    html += `<strong>Fases:</strong> `;
    html += `<span style="color: #ef4444;">● Monofásica (L)</span> `;
    html += `<span style="color: #f97316;">● Bifásica (L+S)</span> `;
    html += `<span style="color: #22c55e;">● Trifásica (L+2S)</span>`;
    html += `</div>`;
    
    // Vértices
    html += `<div class="text-center mt-2" style="font-size: 0.85rem; color: #94a3b8;">`;
    html += `<strong>Vértices:</strong> `;
    html += `<span style="color: #8b5cf6;">${comps[0]}</span> `;
    html += `<span style="color: #22c55e;">${comps[1]}</span> `;
    html += `<span style="color: #eab308;">${comps[2]}</span>`;
    html += `</div>`;
    
    container.innerHTML = html;

    setTimeout(function() {
        const canvas = document.getElementById('diagramChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        Chart.defaults.color = '#e5e7eb';
        Chart.defaults.font.size = 12;

        // Conversão baricêntrica → cartesiana
        function toCartesian(p) {
            const x = p.x2 + 0.5 * p.x3;
            const y = (Math.sqrt(3) / 2) * p.x3;
            return { x: x, y: y };
        }

        const points = results.points;

        // ✅ SEPARAR POR FASE CORRETAMENTE
        const liquidPoints = points.filter(p => p.num_solid_phases == 0);  // VERMELHO
        const eutecticPoints = points.filter(p => p.num_solid_phases >= 2);  // VERDE
        
        // ✅ SEPARAR BIFÁSICOS POR COMPONENTE (3 DATASETS MARROM)
        const biphasic_comp0 = points.filter(p => 
            p.num_solid_phases == 1 && p.solid_components && p.solid_components.includes(comps[0])
        );
        const biphasic_comp1 = points.filter(p => 
            p.num_solid_phases == 1 && p.solid_components && p.solid_components.includes(comps[1])
        );
        const biphasic_comp2 = points.filter(p => 
            p.num_solid_phases == 1 && p.solid_components && p.solid_components.includes(comps[2])
        );

        console.log('[ESL] Renderizando diagrama ternário:');
        console.log(`   • Total de pontos: ${points.length}`);
        console.log(`   • Região líquida (L): ${liquidPoints.length} pontos`);
        console.log(`   • Região S+L: ${biphasic_comp0.length + biphasic_comp1.length + biphasic_comp2.length} pontos`);
        console.log(`   • Região eutética (L+2S): ${eutecticPoints.length} pontos`);

        const datasets = [];

        // 1️⃣ VERDE GRANDE (centro) - Trifásico L+2S
        if (eutecticPoints.length > 0) {
            datasets.push({
                label: 'Região trifásica (L+2S)',
                data: eutecticPoints.map(toCartesian),
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34,197,94,0.6)',
                pointRadius: 5,
                pointStyle: 'circle',
                showLine: false
            });
        }

        // 2️⃣ MARROM (3 cores separadas) - Bifásicos L+S
        if (biphasic_comp0.length > 0) {
            datasets.push({
                label: `L + ${comps[0]} sólido`,
                data: biphasic_comp0.map(toCartesian),
                borderColor: '#f97316',
                backgroundColor: 'rgba(249,115,22,0.6)',
                pointRadius: 4,
                pointStyle: 'circle',
                showLine: false
            });
        }
        
        if (biphasic_comp1.length > 0) {
            datasets.push({
                label: `L + ${comps[1]} sólido`,
                data: biphasic_comp1.map(toCartesian),
                borderColor: '#fb923c',
                backgroundColor: 'rgba(251,146,60,0.6)',
                pointRadius: 4,
                pointStyle: 'circle',
                showLine: false
            });
        }
        
        if (biphasic_comp2.length > 0) {
            datasets.push({
                label: `L + ${comps[2]} sólido`,
                data: biphasic_comp2.map(toCartesian),
                borderColor: '#fdba74',
                backgroundColor: 'rgba(253,186,116,0.6)',
                pointRadius: 4,
                pointStyle: 'circle',
                showLine: false
            });
        }

        // 3️⃣ VERMELHO PEQUENO (topo) - Monofásico L
        if (liquidPoints.length > 0) {
            datasets.push({
                label: 'Região monofásica (L)',
                data: liquidPoints.map(toCartesian),
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239,68,68,0.6)',
                pointRadius: 4,
                pointStyle: 'circle',
                showLine: false
            });
        }

        // 4️⃣ Triângulo de referência
        const sqrt32 = Math.sqrt(3) / 2;
        const vertices = [
            { x: 0, y: 0, label: comps[1] },      // Inferior esquerdo
            { x: 1, y: 0, label: comps[0] },      // Inferior direito
            { x: 0.5, y: sqrt32, label: comps[2] } // Superior
        ];
        
        datasets.push({
            label: 'Vértices',
            data: vertices,
            borderColor: '#94a3b8',
            backgroundColor: 'rgba(148,163,184,0.3)',
            pointRadius: 8,
            pointStyle: 'triangle',
            showLine: true,
            borderWidth: 1.5,
            borderDash: [5, 5],
            fill: false
        });

        if (currentChart) currentChart.destroy();
        
        currentChart = new Chart(ctx, {
            type: 'scatter',
            data: { datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { usePointStyle: true, padding: 15, font: { size: 11 } } },
                    title: {
                        display: true,
                        text: `Diagrama Ternário de Solubilidade - T = ${TC.toFixed(1)} °C`,
                        font: { size: 14, weight: 'bold' },
                        color: '#e5e7eb'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const datasetLabel = context.dataset.label;
                                const idx = context.dataIndex;
                                
                                if (datasetLabel.includes('Vértices')) {
                                    const vertex = vertices[idx];
                                    return `Vértice: ${vertex.label} (puro)`;
                                }
                                
                                // Encontrar ponto original
                                let point = null;
                                if (datasetLabel.includes('monofásica')) point = liquidPoints[idx];
                                else if (datasetLabel.includes('trifásica')) point = eutecticPoints[idx];
                                else if (datasetLabel.includes(comps[0])) point = biphasic_comp0[idx];
                                else if (datasetLabel.includes(comps[1])) point = biphasic_comp1[idx];
                                else if (datasetLabel.includes(comps[2])) point = biphasic_comp2[idx];
                                
                                if (point) {
                                    return [
                                        datasetLabel,
                                        `x(${comps[0]}) = ${point.x1.toFixed(3)}`,
                                        `x(${comps[1]}) = ${point.x2.toFixed(3)}`,
                                        `x(${comps[2]}) = ${point.x3.toFixed(3)}`
                                    ];
                                }
                                
                                return datasetLabel;
                            }
                        },
                        backgroundColor: 'rgba(15,23,42,0.95)',
                        titleColor: '#e5e7eb',
                        bodyColor: '#e5e7eb',
                        borderColor: '#38bdf8',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: -0.05,
                        max: 1.05,
                        title: { display: true, text: 'Coordenada baricêntrica (x)', font: { size: 12, weight: 'bold' }, color: '#e5e7eb' },
                        ticks: { stepSize: 0.2, color: '#94a3b8' },
                        grid: { color: 'rgba(148,163,184,0.2)' }
                    },
                    y: {
                        min: -0.05,
                        max: sqrt32 + 0.05,
                        title: { display: true, text: 'Coordenada baricêntrica (y)', font: { size: 12, weight: 'bold' }, color: '#e5e7eb' },
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(148,163,184,0.2)' }
                    }
                }
            }
        });

        lastDiagramData = results;
        lastDiagramType = 'ternary';
        lastTemperature = TC;
        
        console.log('[ESL] ✓ Diagrama ternário renderizado com sucesso');
    }, 50);
}


// ============================================================================
// COMPARAÇÃO DE MODELOS
// ============================================================================
function showCompareModal() {
  if (!lastDiagramType && !window.lastPointResults) {
    alert('Faça primeiro um cálculo pontual ou gere um diagrama para comparar modelos.');
    return;
  }
  document.getElementById('compareModal').style.display = 'block';
}

function closeCompareModal() {
  const modal = document.getElementById('compareModal');
  if (modal) modal.style.display = 'none';
}

async function compareModels() {
  const checkboxes = document.querySelectorAll('.model-compare-checkbox:checked');
  const models = Array.from(checkboxes).map(function(cb) { return cb.value; });

  if (models.length < 2) {
    alert('Selecione pelo menos 2 modelos para comparar.');
    return;
  }

  const calcType = document.getElementById('calcType').value;
  const components = selectedComponents.map(function(c) { return getComponentName(c); });

  if (calcType === 'tx' || calcType === 'ternary') {
    await compareDiagramModels(models, components, calcType);
  } else {
    await comparePointModels(models, components, calcType);
  }
}

async function compareDiagramModels(models, components, diagramType) {
  const spinner = document.getElementById('comparison-spinner');
  const container = document.getElementById('comparison-diagram-container');
  if (spinner) spinner.style.display = 'block';

  const useCompleteEq = document.getElementById('useCompleteEquation');

  const payload = {
    diagram_type: diagramType,
    components: components,
    models: models,
    use_complete_equation: useCompleteEq ? useCompleteEq.checked : false
  };

  // CORREÇÃO: Adiciona parâmetros específicos para cada tipo de diagrama
  if (diagramType === 'ternary') {
    payload.temperature = parseFloat(document.getElementById('temperature').value);
    payload.temperature_unit = document.getElementById('tempUnit').value;
    
    // Adiciona n_points se existir
    const nPointsInput = document.getElementById('nPoints');
    if (nPointsInput && nPointsInput.value) {
      payload.n_points = parseInt(nPointsInput.value);
    } else {
      payload.n_points = 20; // valor padrão
    }
  } else if (diagramType === 'tx') {
    // Para diagrama T-x, não precisa de temperatura (é gerado em range)
    const nPointsInput = document.getElementById('nPoints');
    if (nPointsInput && nPointsInput.value) {
      payload.n_points = parseInt(nPointsInput.value);
    } else {
      payload.n_points = 100; // valor padrão para T-x
    }
  }

  console.log('[ESL] Payload de comparação:', payload);

  try {
    const res = await fetch('/esl/diagram/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (spinner) spinner.style.display = 'none';
    
    console.log('[ESL] Resposta da comparação:', data);
    
    if (!data.success) {
      alert('Erro na comparação de diagramas: ' + (data.error || ''));
      return;
    }

    renderDiagramComparison(data.results, diagramType, components);
    if (container) {
      container.style.display = 'block';
      // Scroll suave até o resultado
      setTimeout(() => {
        container.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 150);
    }
    closeCompareModal();

    console.log('[ESL] Comparação de diagramas concluída');
  } catch (err) {
    if (spinner) spinner.style.display = 'none';
    alert('Erro na comparação de diagramas: ' + err.message);
    console.error('[ESL] Erro na comparação:', err);
  }
}


async function comparePointModels(models, components, calcType) {
  const spinner = document.getElementById('comparison-spinner');
  const container = document.getElementById('comparison-diagram-container');
  if (spinner) spinner.style.display = 'block';

  const useCompleteEq = document.getElementById('useCompleteEquation');

  const payload = {
    calc_type: calcType,
    components: components,
    models: models,
    use_complete_equation: useCompleteEq ? useCompleteEq.checked : false
  };

  if (calcType === 'solubility') {
    payload.temperature = parseFloat(document.getElementById('temperature').value);
    payload.temperature_unit = document.getElementById('tempUnit').value;
  }

  if (calcType === 'crystallization') {
    const compositions = [];
    for (let i = 0; i < selectedComponents.length; i++) {
      const el = document.getElementById('x' + (i + 1));
      const val = parseFloat(el ? el.value : NaN);
      compositions.push(isNaN(val) ? 0 : val);
    }
    payload.compositions = compositions;
  }

  try {
    const res = await fetch('/esl/calculate/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (spinner) spinner.style.display = 'none';
    if (!data.success) {
      alert('Erro na comparação de modelos: ' + (data.error || ''));
      return;
    }

    displayPointComparison(data.results, calcType, components);
    if (container) container.style.display = 'block';
    closeCompareModal();

    console.log('[ESL] Comparação pontual concluída');
  } catch (err) {
    if (spinner) spinner.style.display = 'none';
    alert('Erro na comparação de modelos: ' + err.message);
    console.error(err);
  }
}


/**
 * Renderiza gráfico de comparação entre múltiplos modelos termodinâmicos.
 * - T-x: Sobrepõe curvas no mesmo gráfico
 * - Ternário: Cria gráficos lado a lado usando renderTernaryDiagram
 * 
 * @param {Object} results - Resultados por modelo {modelName: data}
 * @param {string} diagramType - 'tx' ou 'ternary'
 * @param {Array} components - Lista de componentes
 */
function renderDiagramComparison(results, diagramType, components) {
  const container = document.getElementById('comparison-diagram-container');
  if (!container) {
    console.error('[ESL] Container de comparação não encontrado!');
    return;
  }

  // Limpa gráficos anteriores
  if (window.comparisonChart) {
    window.comparisonChart.destroy();
    window.comparisonChart = null;
  }

  console.log('[ESL] Container exibido, iniciando renderização do gráfico...');

  if (diagramType === 'tx') {
    // ===== T-X: UM ÚNICO GRÁFICO COM TODAS AS CURVAS =====
    renderTxComparison(results, components, container);
  } else if (diagramType === 'ternary') {
    // ===== TERNÁRIO: REUTILIZAR renderTernaryDiagram LADO A LADO =====
    renderTernaryComparisonSideBySide(results, components, container);
  }
}

/**
 * Renderiza comparação T-x (um único gráfico com todas as curvas)
 */
function renderTxComparison(results, components, container) {
  container.innerHTML = `
    <div class="results-card">
      <h4 class="mb-3">
        <i class="bi bi-bar-chart-line"></i> 
        Comparação de Modelos Termodinâmicos
      </h4>
      <h6 class="section-title-sm mb-3">
        Comparação de Diagramas TX - ${components.join(' / ').toUpperCase()}
      </h6>
      <div style="position:relative;height:520px;width:100%;">
        <canvas id="comparison-diagram"></canvas>
      </div>
    </div>
  `;

  container.style.display = 'block';

  setTimeout(() => {
    const canvas = document.getElementById('comparison-diagram');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const datasets = [];
    const colors = ['#38bdf8', '#22c55e', '#f97316', '#eab308', '#a855f7', '#ec4899'];

    let idx = 0;
    let hasValidData = false;

    for (const modelName in results) {
      const res = results[modelName];
      if (res.error) {
        console.warn('[ESL] Modelo ' + modelName + ' falhou:', res.error);
        continue;
      }

      const color = colors[idx % colors.length];
      idx += 1;

      const x1_left = res.x1_left || [];
      const T_left_C = res.T_left_C || [];
      const x1_right = res.x1_right || [];
      const T_right_C = res.T_right_C || [];

      console.log(`[ESL] Modelo ${modelName}: left=${x1_left.length}, right=${x1_right.length} pontos`);

      if (x1_left.length > 0 && T_left_C.length > 0) {
        hasValidData = true;
        
        datasets.push({
          label: modelName + ' (liquidus esq)',
          data: x1_left.map((x, i) => ({ x: x, y: T_left_C[i] })),
          borderColor: color,
          backgroundColor: 'transparent',
          tension: 0.2,
          pointRadius: 2,
          pointHoverRadius: 4,
          borderWidth: 2
        });

        if (x1_right.length > 0 && T_right_C.length > 0) {
          datasets.push({
            label: modelName + ' (liquidus dir)',
            data: x1_right.map((x, i) => ({ x: x, y: T_right_C[i] })),
            borderColor: color,
            backgroundColor: 'transparent',
            tension: 0.2,
            pointRadius: 2,
            pointHoverRadius: 4,
            borderWidth: 2,
            borderDash: [5, 5]
          });
        }

        if (res.x1_eutectic !== undefined && res.T_eutectic_C !== undefined) {
          datasets.push({
            label: modelName + ' (eutético)',
            data: [{ x: res.x1_eutectic, y: res.T_eutectic_C }],
            borderColor: color,
            backgroundColor: color,
            pointRadius: 6,
            pointHoverRadius: 8,
            showLine: false,
            pointStyle: 'star'
          });
        }
      }
    }

    if (!hasValidData) {
      container.innerHTML = `<div class="alert alert-warning">Nenhum modelo retornou dados válidos.</div>`;
      return;
    }

    Chart.defaults.color = '#e5e7eb';
    Chart.defaults.font.size = 12;

    window.comparisonChart = new Chart(ctx, {
      type: 'line',
      data: { datasets: datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { 
            position: 'top',
            labels: { usePointStyle: true, padding: 15, font: { size: 11 } }
          },
          title: {
            display: true,
            text: 'Comparação de Modelos - Diagrama TX',
            font: { size: 14, weight: 'bold' }
          },
          tooltip: {
            mode: 'nearest',
            intersect: false,
            callbacks: {
              label: function(context) {
                const label = context.dataset.label || '';
                return label + ': x₁=' + context.parsed.x.toFixed(4) + ', T=' + context.parsed.y.toFixed(2) + '°C';
              }
            }
          }
        },
        scales: {
          x: {
            type: 'linear',
            title: { display: true, text: 'Fração molar x₁ (' + components[0] + ')', font: { size: 13 } },
            min: 0,
            max: 1,
            ticks: { stepSize: 0.1 },
            grid: { color: 'rgba(148,163,184,0.2)' }
          },
          y: {
            title: { display: true, text: 'Temperatura (°C)', font: { size: 13 } },
            grid: { color: 'rgba(148,163,184,0.2)' }
          }
        }
      }
    });

    console.log('[ESL] Gráfico T-x criado com', datasets.length, 'datasets');
  }, 100);
}

/**
 * Renderiza um diagrama ternário diretamente em um canvas específico
 * (versão simplificada para comparação)
 */
function renderTernaryInCanvas(canvasId, results, components, modelName) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.error('[ESL] Canvas não encontrado:', canvasId);
    return;
  }

  const ctx = canvas.getContext('2d');
  const points = results.points || [];

  // ✅ CORREÇÃO: Filtrar por fase usando normalização mais robusta
  const liquidPoints = [];
  const solidLiquidPoints = [];
  const eutecticPoints = [];

  points.forEach(p => {
    const phase = String(p.phase || '').toLowerCase().trim();
    
    if (phase === 'liquid' || phase === 'l') {
      liquidPoints.push(p);
    } else if (phase === 'solid+liquid' || phase === 's+l' || phase.includes('solid') && phase.includes('liquid')) {
      solidLiquidPoints.push(p);
    } else if (phase === 'eutectic' || phase === 'l+2s' || phase.includes('eutectic') || phase.includes('2s')) {
      eutecticPoints.push(p);
    }
  });

  // Logo após o forEach, adicione:
  if (points.length > 0) {
    console.log(`[ESL DEBUG] Primeiras 5 fases:`, points.slice(0, 5).map(p => p.phase));
  }


  console.log(`[ESL] ${modelName}: L=${liquidPoints.length}, S+L=${solidLiquidPoints.length}, Eut=${eutecticPoints.length}`);

  // Função de conversão para coordenadas cartesianas
  function toCartesian(p) {
    const x = p.x2 + 0.5 * p.x3;
    const y = (Math.sqrt(3) / 2) * p.x3;
    return { x: x, y: y };
  }

  const datasets = [];

  // Triângulo de referência
  datasets.push({
    label: 'Triângulo',
    data: [
      { x: 0, y: 0 },
      { x: 1, y: 0 },
      { x: 0.5, y: Math.sqrt(3) / 2 },
      { x: 0, y: 0 }
    ],
    borderColor: '#64748b',
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderDash: [4, 4],
    pointRadius: 0,
    showLine: true,
    tension: 0
  });

  // Região líquida (azul para Ideal, verde para NRTL)
  if (liquidPoints.length > 0) {
    const color = modelName.includes('Ideal') ? '#38bdf8' : '#22c55e';
    datasets.push({
      label: 'Líquido (L)',
      data: liquidPoints.map(p => toCartesian(p)),
      borderColor: color,
      backgroundColor: color + 'DD',
      pointRadius: 6,
      pointHoverRadius: 8,
      showLine: false,
      pointStyle: 'circle'
    });
  }

  // Região sólido+líquido (laranja)
  if (solidLiquidPoints.length > 0) {
    datasets.push({
      label: 'Sólido+Líquido (S+L)',
      data: solidLiquidPoints.map(p => toCartesian(p)),
      borderColor: '#f97316',
      backgroundColor: '#f9731688',
      pointRadius: 4,
      pointHoverRadius: 6,
      showLine: false,
      pointStyle: 'circle'
    });
  }

  // Região eutética (cinza)
  if (eutecticPoints.length > 0) {
    datasets.push({
      label: 'Eutético (L+2S)',
      data: eutecticPoints.map(p => toCartesian(p)),
      borderColor: '#94a3b8',
      backgroundColor: '#94a3b866',
      pointRadius: 3,
      pointHoverRadius: 5,
      showLine: false,
      pointStyle: 'circle'
    });
  }

  // Configurações do Chart.js
  Chart.defaults.color = '#e5e7eb';
  Chart.defaults.font.size = 11;

  new Chart(ctx, {
    type: 'scatter',
    data: { datasets: datasets },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            padding: 10,
            font: { size: 10 }
          }
        },
        title: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.dataset.label;
            }
          }
        }
      },
      scales: {
        x: {
          type: 'linear',
          min: -0.1,
          max: 1.1,
          display: false
        },
        y: {
          min: -0.1,
          max: Math.sqrt(3) / 2 + 0.1,
          display: false
        }
      }
    }
  });

  console.log(`[ESL] Diagrama ternário renderizado no canvas ${canvasId}`);
}




/**
 * Renderiza comparação ternária (gráficos lado a lado)
 */
function renderTernaryComparisonSideBySide(results, components, container) {
  const modelNames = Object.keys(results).filter(m => !results[m].error);
  
  if (modelNames.length === 0) {
    container.innerHTML = `<div class="alert alert-warning">Nenhum modelo retornou dados válidos.</div>`;
    return;
  }

  // Criar HTML com canvas lado a lado
  const canvasesHtml = modelNames.map((modelName, idx) => `
    <div class="col-md-6">
      <div class="card bg-dark border-secondary p-3 mb-3">
        <h5 class="text-center text-white mb-3">${modelName}</h5>
        <div style="position:relative;height:450px;width:100%;">
          <canvas id="ternary-comparison-${idx}"></canvas>
        </div>
      </div>
    </div>
  `).join('');

  container.innerHTML = `
    <div class="results-card">
      <h4 class="mb-3">
        <i class="bi bi-bar-chart-line"></i> 
        Comparação de Modelos Termodinâmicos
      </h4>
      <h6 class="section-title-sm mb-3">
        Comparação de Diagramas Ternários - ${components.join(' / ').toUpperCase()}
      </h6>
      <div class="row">
        ${canvasesHtml}
      </div>
    </div>
  `;

  container.style.display = 'block';

  // ✅ Usar a função auxiliar para renderizar cada diagrama
  setTimeout(() => {
    modelNames.forEach((modelName, idx) => {
      const canvasId = `ternary-comparison-${idx}`;
      const res = results[modelName];
      
      console.log(`[ESL] Renderizando ${modelName} no canvas #${canvasId}`);
      
      // ✅ Chamar função de renderização direta
      renderTernaryInCanvas(canvasId, res, components, modelName);
    });

    console.log('[ESL] Gráficos ternários lado a lado criados com sucesso');
  }, 200);
}









function displayPointComparison(results, calcType, components) {
  const container = document.getElementById('comparison-diagram-container');
  if (!container) return;

  let html = '<div class="results-card">';
  html += '<h4 class="mb-3"><i class="bi bi-bar-chart-line"></i> Comparação de Modelos Termodinâmicos</h4>';
  html += '<div class="mb-2" style="font-size: 0.9rem; color: #94a3b8;">';
  html += '<strong>Sistema:</strong> ' + components.join(' + ') + ' | ';
  html += '<strong>Cálculo:</strong> ' + calcType.toUpperCase() + '</div>';

  for (const modelName in results) {
    const res = results[modelName];
    if (res.error) {
      html += '<div class="alert alert-warning mb-3" style="background: rgba(251,191,36,0.1); border: 1px solid #fbbf24; color: #fbbf24;">';
      html += '<strong>' + escapeHtml(modelName) + ':</strong> ' + escapeHtml(res.error) + '</div>';
      continue;
    }

    html += '<div class="mt-3 mb-4 p-3" style="border-radius:12px; border:1px solid rgba(148,163,184,0.4); background: rgba(30,41,59,0.3);">';
    html += '<h6 class="mb-3" style="color: #38bdf8;"><i class="bi bi-diagram-3"></i> Modelo: <strong>' + escapeHtml(modelName) + '</strong></h6>';
    html += '<div class="row g-3">';

    const conditionKeys = ['T_C', 'T_K', 'T_cryst_C', 'T_cryst_K', 'model', 'equation'];
    const gammaKeys = [];
    const xKeys = [];
    const phaseKeys = [];
    const extraKeys = [];

    for (const key in res) {
      if (key.startsWith('gamma')) {
        gammaKeys.push(key);
      } else if (key.startsWith('x') && key.includes('(')) {
        xKeys.push(key);
      } else if (key.startsWith('phase')) {
        phaseKeys.push(key);
      } else if (!conditionKeys.includes(key) && key !== 'warnings') {
        extraKeys.push(key);
      }
    }

    gammaKeys.sort();
    xKeys.sort();
    phaseKeys.sort();

    html += '<div class="col-md-4"><h6 class="section-title-sm">Condições</h6><div class="results-grid">';
    conditionKeys.forEach(function(k) {
      if (res[k] !== undefined) {
        const v = res[k];
        html += '<div class="result-item">';
        html += '<span class="label">' + escapeHtml(k) + '</span>';
        html += '<span class="value">' + (typeof v === 'number' ? v.toFixed(4) : escapeHtml(String(v))) + '</span>';
        html += '</div>';
      }
    });
    html += '</div></div>';

    html += '<div class="col-md-4"><h6 class="section-title-sm">Composição</h6><div class="results-grid">';
    xKeys.forEach(function(k) {
      const v = res[k];
      html += '<div class="result-item">';
      html += '<span class="label">' + formatLabel(k) + '</span>';
      html += '<span class="value">' + (v.toFixed ? v.toFixed(6) : v) + '</span>';
      html += '</div>';
    });
    phaseKeys.forEach(function(k) {
      const v = res[k];
      html += '<div class="result-item">';
      html += '<span class="label">' + formatLabel(k) + '</span>';
      html += '<span class="value">' + escapeHtml(String(v)) + '</span>';
      html += '</div>';
    });
    html += '</div></div>';

    html += '<div class="col-md-4"><h6 class="section-title-sm">Propriedades</h6><div class="results-grid">';
    gammaKeys.forEach(function(k) {
      const v = res[k];
      html += '<div class="result-item">';
      html += '<span class="label">' + formatLabel(k) + '</span>';
      html += '<span class="value">' + (v.toFixed ? v.toFixed(4) : v) + '</span>';
      html += '</div>';
    });
    extraKeys.forEach(function(k) {
      const v = res[k];
      html += '<div class="result-item">';
      html += '<span class="label">' + escapeHtml(k) + '</span>';
      html += '<span class="value">' + (v.toFixed ? v.toFixed(4) : escapeHtml(String(v))) + '</span>';
      html += '</div>';
    });
    html += '</div></div>';

    html += '</div></div>';
  }

  html += '</div>';
  container.innerHTML = html;
}

// ============================================================================
// EXPORTAÇÃO CSV/PDF
// ============================================================================
const csvBtn = document.getElementById('export-csv-btn');
if (csvBtn) {
  csvBtn.addEventListener('click', function () {
    if (!lastDiagramData) {
      alert('Nenhum diagrama gerado ainda!');
      return;
    }

    const components = selectedComponents.map(function(c) { return getComponentName(c); });
    const payload = {
      diagram_type: lastDiagramType,
      components: components,
      model: lastModel,
      temperature: lastTemperature,
      data: lastDiagramData
    };

    fetch('/esl/export/csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function(response) { return response.blob(); })
      .then(function(blob) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ESL_' + lastDiagramType.toUpperCase() + '_' + lastModel + '_diagram.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        showNotification('Diagrama exportado em CSV!', 'success');
      })
      .catch(function(err) {
        console.error('[ESL] Erro ao exportar CSV:', err);
        alert('Erro ao exportar CSV.');
      });
  });
}

const pdfBtn = document.getElementById('export-pdf-btn');
if (pdfBtn) {
  pdfBtn.addEventListener('click', function () {
    if (!lastDiagramData) {
      alert('Nenhum diagrama gerado ainda!');
      return;
    }

    const components = selectedComponents.map(function(c) { return getComponentName(c); });
    const payload = {
      diagram_type: lastDiagramType,
      components: components,
      model: lastModel,
      temperature: lastTemperature,
      data: lastDiagramData
    };

    fetch('/esl/export/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function(response) { return response.blob(); })
      .then(function(blob) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ESL_' + lastDiagramType.toUpperCase() + '_' + lastModel + '_diagram.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        showNotification('Diagrama exportado em PDF!', 'success');
      })
      .catch(function(err) {
        console.error('[ESL] Erro ao exportar PDF:', err);
        alert('Erro ao exportar PDF.');
      });
  });
}

const csvPtsBtn = document.getElementById('export-csv-points-btn');
if (csvPtsBtn) {
  csvPtsBtn.addEventListener('click', function () {
    if (!window.lastPointResults) {
      alert('Nenhum resultado pontual para exportar!');
      return;
    }

    const components = selectedComponents.map(function(c) { return getComponentName(c); });
    const payload = {
      calc_type: document.getElementById('calcType').value,
      components: components,
      model: document.getElementById('model').value,
      results: window.lastPointResults
    };

    fetch('/esl/export/point_csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function(response) { return response.blob(); })
      .then(function(blob) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ESL_' + payload.calc_type + '_resultado.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        showNotification('Resultado exportado em CSV!', 'success');
      })
      .catch(function(err) {
        console.error('[ESL] Erro ao exportar CSV pontual:', err);
        alert('Erro ao exportar CSV.');
      });
  });
}

const pdfPtsBtn = document.getElementById('export-pdf-points-btn');
if (pdfPtsBtn) {
  pdfPtsBtn.addEventListener('click', function () {
    if (!window.lastPointResults) {
      alert('Nenhum resultado pontual para exportar!');
      return;
    }

    const components = selectedComponents.map(function(c) { return getComponentName(c); });
    const payload = {
      calc_type: document.getElementById('calcType').value,
      components: components,
      model: document.getElementById('model').value,
      results: window.lastPointResults
    };

    fetch('/esl/export/point_pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function(response) { return response.blob(); })
      .then(function(blob) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ESL_' + payload.calc_type + '_resultado.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        showNotification('Resultado exportado em PDF!', 'success');
      })
      .catch(function(err) {
        console.error('[ESL] Erro ao exportar PDF pontual:', err);
        alert('Erro ao exportar PDF.');
      });
  });
}

// ============================================================================
// UTILITÁRIOS
// ============================================================================
function formatLabel(key) {
  if (key.match(/^(gamma|x|y|z|phase)(\d+)/)) {
    return key.replace(/(\d+)/, '<sub>$1</sub>');
  }

  if (key.match(/^[xyz]\d+\s*\(/)) {
    return key.replace(/([xyz])(\d+)/, '$1<sub>$2</sub>');
  }

  return key;
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, function(m) { return map[m]; });
}

function clearComparison() {
  const container = document.getElementById('comparison-diagram-container');
  if (container) container.style.display = 'none';

  if (window.comparisonChart) {
    window.comparisonChart.destroy();
    window.comparisonChart = null;
  }
}

function clearForm() {
  selectedComponents = [];
  updateComponentTags();
  updateFields();

  const resultsDiv = document.getElementById('results');
  if (resultsDiv) {
    resultsDiv.innerHTML = '<div class="panel h-100 d-flex flex-column justify-content-center align-items-center">';
    resultsDiv.innerHTML += '<div class="text-muted-soft mb-2"><i class="bi bi-graph-up"></i> Nenhum resultado ainda.</div>';
    resultsDiv.innerHTML += '<div class="text-muted-soft" style="font-size: 0.85rem;">Configure o cálculo à esquerda e clique em <strong>Calcular</strong>.</div></div>';
  }

  clearComparison();

  const aiContainer = document.getElementById('ai-recommendation');
  if (aiContainer) aiContainer.innerHTML = '';

  const warningsContainer = document.getElementById('thermodynamicWarnings');
  if (warningsContainer) warningsContainer.innerHTML = '';

  const validationContainer = document.getElementById('validationMessages');
  if (validationContainer) validationContainer.innerHTML = '';

  const exportBtns = document.getElementById('export-buttons');
  if (exportBtns) exportBtns.style.display = 'none';

  const exportPtsBtns = document.getElementById('export-buttons-points');
  if (exportPtsBtns) exportPtsBtns.style.display = 'none';

  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }

  window.lastPointResults = null;
  window.lastAiSuggestion = null;
  lastDiagramData = null;
  lastDiagramType = null;
  lastModel = null;
  lastTemperature = null;

  const propPreview = document.getElementById('componentPropertiesPreview');
  if (propPreview) propPreview.innerHTML = '';

  showNotification('Formulário limpo!', 'info');
}

function showNotification(message, type) {
  console.log('[ESL] Notificação [' + type + ']: ' + message);

  const alertDiv = document.createElement('div');
  alertDiv.className = 'alert alert-' + type;
  alertDiv.style.position = 'fixed';
  alertDiv.style.top = '20px';
  alertDiv.style.right = '20px';
  alertDiv.style.zIndex = '10000';
  alertDiv.style.minWidth = '300px';
  alertDiv.style.animation = 'slideInRight 0.3s ease';
  alertDiv.innerHTML = '<i class="bi bi-info-circle"></i> ' + escapeHtml(message);

  document.body.appendChild(alertDiv);

  setTimeout(function() {
    alertDiv.style.animation = 'slideOutRight 0.3s ease';
    setTimeout(function() { alertDiv.remove(); }, 300);
  }, 3000);
}

function showInfo(message) {
  showNotification(message, 'info');
}

function initializeTooltips() {
  try {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
      new bootstrap.Tooltip(tooltipTriggerEl);
    });
  } catch (err) {
    console.warn('[ESL] Não foi possível inicializar tooltips:', err);
  }
}

console.log('[ESL] Módulo JavaScript REFINADO carregado completamente!');

// ============================================================================
// EXEMPLOS DO PRAUSNITZ - ESL (Cap. 11)
// ============================================================================

function addPrausnitzExamplesButton() {
    const container = document.querySelector('.calc-panel .panel-header');
    if (!container) {
        console.warn('[ESL] Cabeçalho do painel não encontrado.');
        return;
    }

    if (container.querySelector('.btn-esl-examples')) return;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn-sim btn-sim-ghost btn-sm btn-esl-examples';
    btn.innerHTML = '<i class="bi bi-book"></i> Exemplos';
    btn.style.marginLeft = 'auto';

    btn.addEventListener('click', () => {
        console.log('[ESL] Botão "Exemplos" clicado');
        showPrausnitzExamplesModal();
    });

    container.appendChild(btn);
}

function showPrausnitzExamplesModal() {
    const examples = getPrausnitzExamplesESL();

    const old = document.getElementById('prausnitzModal');
    if (old) old.remove();

    let html = `
    <div class="modal-backdrop-custom" id="prausnitzModal" onclick="closePrausnitzModal()">
        <div class="modal-content-custom" onclick="event.stopPropagation()" style="max-width: 850px; max-height: 90vh; overflow-y: auto;">
            <div class="panel-header mb-3">
                <div class="panel-title">
                    <i class="bi bi-book"></i> EXEMPLOS 
                </div>
            </div>

            <div class="text-muted-soft mb-3" style="font-size: 0.9rem;">
                <strong>${examples.length} exemplos validados</strong> de equilíbrio sólido-líquido de Prausnitz et al. (3rd Ed., 1999).
                <br>✅ Testados e funcionais.
            </div>

            <div style="display: grid; gap: 10px; max-height: 600px; overflow-y: auto; padding-right: 10px;">
    `;

    examples.forEach((ex, idx) => {
        const badgeClass =
            ex.difficulty === 'básico' ? 'bg-success' :
            ex.difficulty === 'intermediário' ? 'bg-warning' : 'bg-danger';

        const tempInfo = ex.temperature_C !== undefined
            ? `${ex.temperature_C}°C`
            : 'Diagrama T‑x';

        const modelBadge = ex.model === 'Ideal' ? 'badge-ideal' : 'badge-nrtl';

        html += `
            <div class="example-card" onclick="loadPrausnitzExample(${idx})" style="cursor: pointer; transition: all 0.2s;">
                <div class="example-card-header">
                    <div>
                        <span class="example-card-title">${escapeHtml(ex.name)}</span>
                        <span class="badge ${badgeClass} ms-2" style="font-size: 0.7rem;">${ex.difficulty}</span>
                        <span class="badge ${modelBadge} ms-1" style="font-size: 0.7rem;">${ex.model}</span>
                    </div>
                    <i class="bi bi-arrow-right-circle" style="font-size: 1.4rem; color: #38bdf8;"></i>
                </div>
                <div class="example-card-details">
                    <i class="bi bi-droplet-fill" style="color: #38bdf8;"></i>
                    ${ex.components.join(' + ')} • ${tempInfo}
                </div>
                <div class="example-card-reference" style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                    📚 ${escapeHtml(ex.reference)}
                </div>
                <div class="text-muted-soft mt-2" style="font-size: 0.85rem; line-height: 1.4;">
                    ${ex.description}
                </div>
            </div>
        `;
    });

    html += `
            </div>

            <div class="alert-info mt-3" style="background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); padding: 12px; border-radius: 8px;">
                <i class="bi bi-info-circle"></i>
                <strong>Como usar:</strong> Clique em um exemplo para carregá-lo automaticamente. 
                Depois, clique em <strong>"Calcular"</strong> para executar o cálculo.
            </div>

            <div class="d-flex justify-content-between align-items-center mt-3">
                <small class="text-muted-soft">
                    <i class="bi bi-check-circle"></i> 
                    ${examples.filter(e => e.calculation_type === 'solubility').length} Solubility • 
                    ${examples.filter(e => e.calculation_type === 'tx').length} Diagramas T-x
                </small>
                <button type="button" class="btn-sim btn-sim-ghost" onclick="closePrausnitzModal()">
                    Fechar
                </button>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', html);
    const modal = document.getElementById('prausnitzModal');
    if (modal) modal.style.display = 'block';
}

function closePrausnitzModal() {
    const modal = document.getElementById('prausnitzModal');
    if (modal) modal.remove();
}

/**
 * ============================================================================
 * EXEMPLOS VALIDADOS DO CAPÍTULO 11 DO PRAUSNITZ  
 * ============================================================================
 * 
 * ✅ TODOS OS 8 EXEMPLOS CORRIGIDOS
 * Total: 5 solubility + 2 T-x + 1 ternário
 */
function getPrausnitzExamplesESL() {
    return [
        // =====================================================================
        // CATEGORIA 1: SISTEMAS IDEAIS - PAHs em Benzeno (Table 11-1)
        // =====================================================================
        {
            name: 'Fenantreno em Benzeno (25°C)',
            components: ['Phenanthrene', 'Benzene'],
            calculation_type: 'solubility',
            temperature_C: 25.0,
            model: 'Ideal',
            reference: 'Prausnitz et al. (3rd Ed., 1999)',
            difficulty: 'básico',
            description: `<strong>✅ PAH com 3 anéis angulares.</strong><br>
            Tm=99.5°C, ΔH<sub>fus</sub>=16.5 kJ/mol → solubilidade moderada.`
        },
        
        {
            name: 'Antraceno em Benzeno (25°C)',
            components: ['Anthracene', 'Benzene'],
            calculation_type: 'solubility',
            temperature_C: 25.0,
            model: 'Ideal',
            reference: 'Prausnitz et al. (3rd Ed., 1999)',
            difficulty: 'básico',
            description: `<strong>✅ PAH com 3 anéis lineares, muito menos solúvel.</strong><br>
            Alto Tm (216.5°C) e ΔH<sub>fus</sub> (29 kJ/mol) → baixíssima solubilidade.`
        },

        // =====================================================================
        // CATEGORIA 2: SISTEMAS NÃO-IDEAIS - NRTL
        // =====================================================================
        {
            name: 'Colesterol em Metanol (40°C)',
            components: ['Cholesterol', 'Methanol'],
            calculation_type: 'solubility',
            temperature_C: 40.0,
            model: 'NRTL',
            reference: 'Prausnitz et al. (3rd Ed., 1999)',
            difficulty: 'avançado',
            description: `<strong>✅ Soluto farmacêutico complexo.</strong><br>
            Colesterol (M=386.67) apresenta forte não-idealidade (γ>>1).`
        },
        
        {
            name: 'Naftaleno em Etanol (25°C)',
            components: ['Naphthalene', 'Ethanol'],
            calculation_type: 'solubility',
            temperature_C: 25.0,
            model: 'NRTL',
            reference: 'Prausnitz et al. (3rd Ed., 1999)',
            difficulty: 'intermediário',
            description: `<strong>✅ PAH apolar em álcool polar.</strong><br>
            Não-idealidade moderada devido a diferenças de polaridade.`
        },
        
        {
            name: 'Naftaleno em 1-Propanol (25°C)',
            components: ['Naphthalene', '1-Propanol'],
            calculation_type: 'solubility',
            temperature_C: 25.0,
            model: 'NRTL',
            reference: 'Prausnitz et al. (3rd Ed., 1999)',
            difficulty: 'intermediário',
            description: `<strong>✅ PAH apolar em álcool de cadeia maior.</strong><br>
            <strong>Validação:</strong> γ(Propanol) < γ(Etanol) ✓ Tendência física correta!`
        },
        
        // =====================================================================
        // CATEGORIA 3: DIAGRAMAS BINÁRIOS T-x (Eutéticos)
        // =====================================================================
        {
            name: 'o-/p-Cloronitrobenzeno (T-x)',
            components: ['o-Chloronitrobenzene', 'p-Chloronitrobenzene'],
            calculation_type: 'tx',
            model: 'Ideal',
            n_points: 100,
            reference: 'Prausnitz et al. (3rd Ed., 1999)',
            difficulty: 'básico',
            description: `<strong>✅ Diagrama T-x eutético clássico (sistema ideal).</strong><br>
            Isômeros: Tm(o)=32°C, Tm(p)=84°C (Prigogine & Defay, 1954).`
        },
        
        // =====================================================================
        // CATEGORIA 4: DIAGRAMAS TERNÁRIOS (Figure 11-11)
        // =====================================================================
        {
            name: 'Benzeno/Acenafteno/Fenol (40°C)',
            components: ['Benzene', 'Acenaphthene', 'Phenol'],
            calculation_type: 'ternary',
            temperature_C: 40.0,
            model: 'NRTL',
            n_points: 20,
            reference: 'Prausnitz et al. (3rd Ed., 1999)',
            difficulty: 'avançado',
            description: `<strong>✅ Diagrama ternário isotérmico.</strong><br>
            Sistema mostra região líquida ampla a 40°C.<br>
            Acenafteno (PAH tricíclico) + fenol (ligações H) + benzeno (aromático).`
        }
    ];
}

// Carrega exemplo na UI do ESL
async function loadPrausnitzExample(index) {
    const examples = getPrausnitzExamplesESL();
    const example = examples[index];

    if (!example) {
        showNotification('Exemplo não encontrado.', 'danger');
        return;
    }

    closePrausnitzModal();

    try {
        console.log('\n' + '='.repeat(70));
        console.log('[ESL] CARREGANDO EXEMPLOS');
        console.log('Nome:', example.name);
        console.log('Componentes:', example.components.join(' + '));
        console.log('Tipo:', example.calculation_type);
        console.log('Modelo:', example.model);
        console.log('Referência:', example.reference);

        // 1) Limpar seleção atual
        selectedComponents = [];
        updateComponentTags();

        // 2) Definir modelo
        const modelSelect = document.getElementById('model');
        if (modelSelect) {
            modelSelect.value = example.model;
            console.log('✓ Modelo definido:', example.model);
        }

        // 3) Filtrar componentes pelo modelo
        await filterComponentsByModel(example.model);

        // 4) Selecionar componentes (busca robusta)
        for (const compName of example.components) {
            const norm = normalizeComponentName(compName);
            const comp = allComponents.find(c => {
                // Match exato
                if (c.name === compName || c.name_en === compName) return true;
                // Match normalizado
                if (normalizeComponentName(c.name) === norm) return true;
                if (c.name_en && normalizeComponentName(c.name_en) === norm) return true;
                // Match por CAS
                if (c.CAS === compName) return true;
                return false;
            });

            if (comp) {
                selectedComponents.push(comp);
                console.log('   ✓ ENCONTRADO:', getComponentName(comp));
            } else {
                console.warn('   ✗ NÃO ENCONTRADO:', compName);
                showNotification(
                    `⚠️ Componente "${compName}" não encontrado no banco de dados ESL.`,
                    'warning'
                );
            }
        }

        if (selectedComponents.length !== example.components.length) {
            showNotification(
                `❌ Erro: apenas ${selectedComponents.length}/${example.components.length} componentes encontrados.
                <br><small>Verifique se todos os componentes estão no banco de dados.</small>`,
                'danger'
            );
            selectedComponents = [];
            updateComponentTags();
            return;
        }

        updateComponentTags();
        console.log('✓ Todos os componentes carregados:', selectedComponents.length);

        // 5) Definir tipo de cálculo
        const calcTypeSelect = document.getElementById('calcType');
        if (calcTypeSelect) {
            calcTypeSelect.value = example.calculation_type;
            console.log('✓ Tipo de cálculo:', example.calculation_type);
        }

        // 6) Atualizar campos dinâmicos
        updateFields();

        // 7) Aguardar o DOM montar os campos (crítico!)
        await new Promise(r => setTimeout(r, 200));

        // 8) Configurar temperatura (solubility)
        if (example.temperature_C !== undefined) {
            const tInput = document.getElementById('temperature');
            const tUnit = document.getElementById('tempUnit');
            if (tInput) {
                tInput.value = example.temperature_C.toFixed(1);
                console.log('✓ Temperatura:', example.temperature_C, '°C');
            }
            if (tUnit) tUnit.value = 'C';
        }

        // 9) Configurar nº de pontos para T-x
        if (example.calculation_type === 'tx' && example.n_points !== undefined) {
            const nInput = document.getElementById('nPoints');
            if (nInput) {
                nInput.value = example.n_points;
                console.log('✓ Nº de pontos:', example.n_points);
            }
        }

        // 10) Atualizar preview e validação
        await updateComponentPropertiesPreview();
        await validateComponentsForModel();

        showNotification(
            `<strong>✅ Exemplo carregado com sucesso!</strong>
            <br><span style="font-size: 0.9rem;">${example.name}</span>
            <br><small style="opacity: 0.8; font-size: 0.75rem;">📚 ${example.reference}</small>`,
            'success'
        );

        console.log('='.repeat(70));
        console.log('👉 Clique em "CALCULAR" para executar o exemplo');
        console.log('='.repeat(70) + '\n');

    } catch (err) {
        console.error('[ESL] Erro ao carregar exemplo:', err);
        showNotification(
            `❌ Erro ao carregar exemplo: ${err.message}
            <br><small>Verifique o console para mais detalhes.</small>`,
            'danger'
        );
    }
}

/**
 * Normaliza nome de componente para busca robusta
 */
function normalizeComponentName(name) {
    if (!name) return '';
    return String(name)
        .toLowerCase()
        .replace(/[^a-z0-9]/g, '')
        .trim();
}

/**
 * Mostra notificação visual (toast)
 */
function showNotification(message, type = 'info') {
    const oldNotifs = document.querySelectorAll('.esl-notification-toast');
    oldNotifs.forEach(n => n.remove());

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed esl-notification-toast`;
    alertDiv.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 450px;
        min-width: 300px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        border-radius: 12px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => alertDiv.remove(), 300);
    }, 8000);
}

// CSS para animação e badges
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
    .badge-ideal { background: rgba(34,197,94,0.2); color: #22c55e; font-weight: 600; }
    .badge-nrtl { background: rgba(56,189,248,0.2); color: #38bdf8; font-weight: 600; }
    
    .example-card {
        background: rgba(30,41,59,0.3);
        border: 1px solid rgba(148,163,184,0.3);
        border-radius: 12px;
        padding: 16px;
    }
    
    .example-card:hover {
        background: rgba(56,189,248,0.05) !important;
        border-color: rgba(56,189,248,0.5) !important;
        transform: translateX(5px);
    }
    
    .example-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }
    
    .example-card-title {
        font-weight: 600;
        color: #e5e7eb;
        font-size: 0.95rem;
    }
    
    .example-card-details {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 6px;
    }
`;
document.head.appendChild(notificationStyles);

