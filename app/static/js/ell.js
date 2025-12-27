// static/js/ell.js
// EQUILÍBRIO LÍQUIDO-LÍQUIDO (ELL)
// VERSÃO 3.0 - Corrigida conforme Prausnitz Tabela E-5 e E-6
// Baseado em: Prausnitz et al., Chapter 12 & Appendix E


// ============================================================================
// VARIÁVEIS GLOBAIS
// ============================================================================


let selectedComponents = [];
let allComponents = [];
let currentDiagram = null;


// Dados do último cálculo
let lastFlashResults = null;
let lastDiagramData = null;
let lastDiagramType = null;
let lastModel = null;
let lastTemperature = null;


// Resultados pontuais
window.lastPointResults = null;


// Sugestão de IA
window.lastAiSuggestion = null;


// ============================================================================
// SISTEMA DE NOTIFICAÇÕES TOAST
// ============================================================================

function showNotification(message, type = 'info', duration = 5000) {
  const container = document.getElementById('notification-container');
  if (!container) {
    // Fallback para alert se container não existir
    alert(message);
    return;
  }
  
  // Ícones por tipo
  const icons = {
    success: 'bi-check-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    error: 'bi-x-circle-fill',
    info: 'bi-info-circle-fill'
  };
  
  // Criar elemento da notificação
  const notification = document.createElement('div');
  notification.className = `notification-toast ${type}`;
  notification.innerHTML = `
    <i class="bi ${icons[type] || icons.info} notification-icon"></i>
    <div class="notification-content">${escapeHtml(message)}</div>
    <button class="notification-close" onclick="this.parentElement.remove()">×</button>
  `;
  
  // Adicionar ao container
  container.appendChild(notification);
  
  // Auto-remover após duração
  setTimeout(() => {
    if (notification.parentElement) {
      notification.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }
  }, duration);
}


// ============================================================================
// INICIALIZAÇÃO
// ============================================================================


document.addEventListener('DOMContentLoaded', async function() {
    await loadAllComponents();
    loadComponentsFromURL();
    updateFields();
    updateModelInfoPanel();
    
    const btnDiag = document.getElementById('export-buttons');
    const btnPts = document.getElementById('export-buttons-points');
    if (btnDiag) btnDiag.style.display = 'none';
    if (btnPts) btnPts.style.display = 'none';
    
    // Adicionar botão para exemplos do Prausnitz
    addPrausnitzExamplesButton();
    
    // ✅ CARREGAR PRESET DE CASO DE ESTUDO SE EXISTIR
    if (window.presetData) {
        await loadPreset();
    }
});



// ============================================================================
// CARREGAMENTO DE COMPONENTES
// ============================================================================


// ============================================================================
// CARREGAMENTO DE COMPONENTES (VERSÃO 2.0 - COM FILTRO POR TIPO DE CÁLCULO)
// ============================================================================

async function loadAllComponents() {
  try {
    const model = document.getElementById('model').value;
    const calcType = document.getElementById('calcType')?.value || 'ell_flash';  // ⭐ NOVO
    
    // ⭐ NOVO: Adicionar calc_type na query string se for extração
    let url = `/ell/api/components?model=${model}`;
    if (calcType === 'extraction') {
      url += '&calc_type=extraction';
      console.log('[ELL] 🔍 Filtrando componentes para EXTRAÇÃO');
    }
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.success) {
      allComponents = data.components;
      console.log(`[ELL] Carregados ${allComponents.length} componentes para ${model}${calcType === 'extraction' ? ' (filtrado para extração)' : ''}`);
    } else {
      console.error('[ELL] Erro ao carregar componentes:', data.error);
      allComponents = [];
    }
  } catch (err) {
    console.error('[ELL] Erro ao carregar componentes:', err);
    allComponents = [];
  }
}



function loadComponentsFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  
  for (let i = 1; i <= 3; i++) {
    const comp = urlParams.get('comp' + i);
    if (comp) {
      const c = allComponents.find(
        x => x.name_en === comp || x.name === comp
      );
      if (c && selectedComponents.length < 3) {
        selectedComponents.push(c);
      }
    }
  }
  
  updateComponentTags();
}


// ============================================================================
// GERENCIAMENTO DE COMPONENTES
// ============================================================================


/**
 * ============================================================================
 * TAGS DE COMPONENTES SELECIONADOS - PT-BR
 * ============================================================================
 */
function updateComponentTags() {
    const container = document.getElementById('selectedComponentsTags');
    const countSpan = document.getElementById('componentCount');
    
    if (!container) return;
    
    let html = '';
    
    selectedComponents.forEach((comp, i) => {
        // ⭐ PRIORIZAR NOME EM PORTUGUÊS
        const displayName = comp.name_pt || comp.name || comp.name_en;
        
        html += `
            <span class="component-tag">
                ${escapeHtml(displayName)}
                <i class="bi bi-x-circle" onclick="removeComponent(${i})"></i>
            </span>
        `;
    });
    
    if (selectedComponents.length < 3) {
        html += `
            <button class="add-component-btn" type="button" onclick="showComponentModal()">
                <i class="bi bi-plus-circle"></i> Adicionar componente
            </button>
        `;
    }
    
    container.innerHTML = html;
    
    if (countSpan) {
        countSpan.textContent = selectedComponents.length;
    }
}



function removeComponent(index) {
  selectedComponents.splice(index, 1);
  updateComponentTags();
  updateFields();
}


function showComponentModal() {
  if (selectedComponents.length >= 3) {
    alert('ELL requer exatamente 3 componentes. Remova um componente antes de adicionar outro.');
    return;
  }
  document.getElementById('componentModal').style.display = 'block';
  renderComponentList('');
}


function closeComponentModal() {
  document.getElementById('componentModal').style.display = 'none';
}


// ============================================================================
// RENDERIZAÇÃO DA LISTA DE COMPONENTES
// ============================================================================


/**
 * ============================================================================
 * RENDERIZAÇÃO DA LISTA DE COMPONENTES - PT-BR
 * ============================================================================
 * Exibe componentes no modal com nomes em português
 */
function renderComponentList(filter = '') {
    const listDiv = document.getElementById('componentList');
    const term = filter.toLowerCase();
    
    let filtered = allComponents;
    if (term) {
        filtered = allComponents.filter(c =>
            (c.name && c.name.toLowerCase().includes(term)) ||
            (c.name_en && c.name_en.toLowerCase().includes(term)) ||
            (c.name_pt && c.name_pt.toLowerCase().includes(term)) ||
            (c.formula && c.formula.toLowerCase().includes(term)) ||
            (c.cas && c.cas.toLowerCase().includes(term))
        );
    }
    
    let html = `<ul class="list-group list-group-flush">`;
    
    filtered.forEach((comp, idx) => {
        const casNumber = comp.cas || comp.name_en || comp.name;
        
        // ⭐ PRIORIZAR NOME EM PORTUGUÊS
        const displayName = comp.name_pt || comp.name || comp.name_en;
        const secondaryInfo = comp.name_en || comp.name_pt || '';
        
        html += `
            <li class="list-group-item" style="cursor:pointer" onclick="selectComponentByCAS('${casNumber}')">
                <div>
                    <strong>${escapeHtml(displayName)}</strong><br>
                    <small class="text-muted-soft">
                        ${escapeHtml(secondaryInfo)} • ${escapeHtml(comp.formula)} • ${escapeHtml(comp.cas)}
                    </small>
                </div>
            </li>
        `;
    });
    
    html += `</ul>`;
    listDiv.innerHTML = html;
}



// ============================================================================
// ⭐ NOVA FUNÇÃO: VERIFICAR MODELOS DISPONÍVEIS PARA COMPONENTES SELECIONADOS
// ============================================================================

async function checkAvailableModels(components) {
  try {
    console.log('[ELL] 🔍 Verificando modelos disponíveis para:', components);
    
    const response = await fetch('/ell/api/models/available', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ components })
    });
    
    const data = await response.json();
    
    if (data.success) {
      const availableModels = data.available_models || [];
      const currentModel = document.getElementById('model').value;
      
      console.log('[ELL] ✅ Modelos disponíveis:', availableModels);
      console.log('[ELL] 📌 Modelo atual:', currentModel);
      
      // ⭐ SE O MODELO ATUAL NÃO ESTÁ DISPONÍVEL, SUGERIR MUDANÇA
      if (!availableModels.includes(currentModel)) {
        const details = data.details[currentModel];
        const message = details?.message || 'Parâmetros não disponíveis para este modelo.';
        
        // Verificar se há modelo alternativo disponível
        if (availableModels.length > 0) {
          const alternativeModel = availableModels[0];
          
          if (confirm(
            `⚠️ Modelo ${currentModel} não disponível:\n\n` +
            `${message}\n\n` +
            `Deseja mudar para ${alternativeModel}? (Recomendado)`
          )) {
            document.getElementById('model').value = alternativeModel;
            await loadAllComponents(); // Recarregar componentes para o novo modelo
            showNotification(`✅ Modelo alterado para ${alternativeModel}`, 'success');
          } else {
            // Usuário optou por não mudar - avisar que cálculo pode falhar
            showNotification(
              `⚠️ Mantendo ${currentModel}. Cálculo pode falhar se parâmetros estiverem ausentes.`,
              'warning'
            );
          }
        } else {
          // Nenhum modelo disponível para esses componentes
          showNotification(
            `❌ Nenhum modelo disponível para:\n${components.join(', ')}\n\n` +
            `Escolha outros componentes ou adicione parâmetros ao banco de dados.`,
            'error'
          );
        }
      } else {
        // Modelo atual está OK
        const details = data.details[currentModel];
        if (details && details.reference) {
          console.log('[ELL] 📚 Referência:', details.reference);
        }
      }
      
      return data;
      
    } else {
      console.error('[ELL] ❌ Erro ao verificar modelos:', data.error);
      return null;
    }
    
  } catch (err) {
    console.error('[ELL] ❌ Erro ao verificar modelos:', err);
    return null;
  }
}


// ============================================================================
// SELEÇÃO DE COMPONENTE
// ============================================================================


function selectComponentByCAS(casOrName) {
  console.log('[ELL] 🔍 Buscando componente:', casOrName);
  
  const comp = allComponents.find(c => 
    c.cas === casOrName || 
    c.name_en === casOrName || 
    c.name === casOrName
  );

  if (!comp) {
    console.error('[ELL] ❌ Componente não encontrado:', casOrName);
    alert('Erro ao selecionar componente. Tente novamente.');
    return;
  }

  console.log('[ELL] 📦 Componente encontrado:', comp.name, '| CAS:', comp.cas, '| name_en:', comp.name_en);

  if (selectedComponents.length >= 3) {
    alert('ELL requer exatamente 3 componentes. Remova um antes de adicionar outro.');
    return;
  }

  const isDuplicate = selectedComponents.some(c => {
    if (c.cas && comp.cas) {
      return c.cas === comp.cas;
    }
    if (c.name_en && comp.name_en) {
      return c.name_en === comp.name_en;
    }
    return c.name === comp.name;
  });

  if (isDuplicate) {
    alert(`Componente "${comp.name}" já foi selecionado.`);
    console.log('[ELL] ⚠️ Componente duplicado detectado:', comp.name);
    return;
  }

  selectedComponents.push(comp);
  console.log('[ELL] ✅ Componente adicionado:', comp.name, '| Total:', selectedComponents.length);
  
  updateComponentTags();
  updateFields();
  closeComponentModal();
  
  // ⭐ NOVO: VERIFICAR MODELOS DISPONÍVEIS QUANDO COMPLETAR 3 COMPONENTES
  if (selectedComponents.length === 3) {
    const componentNames = selectedComponents.map(c => c.name_en || c.name);
    console.log('[ELL] 🎯 3 componentes completos! Verificando modelos disponíveis...');
    
    // Aguardar 500ms para garantir que UI foi atualizada
    setTimeout(() => {
      checkAvailableModels(componentNames);
    }, 500);
  }
}

/**
 * ============================================================================
 * PAINEL INFORMATIVO DINÂMICO - NRTL, UNIQUAC, UNIFAC
 * ============================================================================
 * Exibe informações específicas para cada modelo termodinâmico
 * Versão 4.0 - Suporta PT-BR + UNIFAC preditivo
 */
async function updateModelInfoPanel() {
    const model = document.getElementById('model')?.value;
    const infoPanel = document.getElementById('model-systems-info');
    
    if (!infoPanel) return;
    
    // Limpar painel
    infoPanel.innerHTML = '';
    infoPanel.style.display = 'none';
    
    let html = '';
    
    // PAINEL PARA NRTL
    if (model === 'NRTL') {
        html = `
        <div class="alert alert-info" style="margin-bottom: 1rem;">
            <div style="display: flex; align-items: flex-start; gap: 10px;">
                <i class="bi bi-info-circle" style="font-size: 1.2rem; color: #38bdf8; flex-shrink: 0;"></i>
                <div style="flex-grow: 1;">
                    <strong style="color: #e5e7eb;">ℹ️ Sistemas NRTL Disponíveis</strong>
                    <div style="margin-top: 8px; font-size: 0.85rem;">
                        <p style="margin: 0 0 8px 0; color: #cbd5e1;">
                            <strong>Todos os sistemas NRTL começam com Water (Água).</strong>
                        </p>
                        <ul style="margin: 0 0 8px 16px; padding: 0; color: #94a3b8; list-style: none;">
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>Água</strong> / <strong>1,1,2-Tricloroetano</strong> / <strong>Acetona</strong>
                                <span class="badge bg-info" style="margin-left: 8px;"></span>
                            </li>
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>Água</strong> / <strong>Tolueno</strong> / <strong>Ácido Acético</strong>
                                <span class="badge bg-success" style="margin-left: 8px;"></span>
                            </li>
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>Água</strong> / <strong>MIBK</strong> / <strong>Ácido Acético</strong>
                                <span class="badge bg-success" style="margin-left: 8px;"></span>
                            </li>
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>Água</strong> / <strong>Acetato de Etila</strong> / <strong>Ácido Acético</strong>
                                <span class="badge bg-success" style="margin-left: 8px;"></span>
                            </li>
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>Água</strong> / <strong>Ciclo-Hexano</strong> / <strong>Etanol</strong>
                                <span class="badge bg-success" style="margin-left: 8px;"></span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>`;
    }
    
    // PAINEL PARA UNIQUAC
    else if (model === 'UNIQUAC') {
        html = `
        <div class="alert alert-info" style="margin-bottom: 1rem;">
            <div style="display: flex; align-items: flex-start; gap: 10px;">
                <i class="bi bi-info-circle" style="font-size: 1.2rem; color: #38bdf8; flex-shrink: 0;"></i>
                <div style="flex-grow: 1;">
                    <strong style="color: #e5e7eb;">ℹ️ Sistemas UNIQUAC Disponíveis</strong>
                    <div style="margin-top: 8px; font-size: 0.85rem;">
                        <ul style="margin: 0; padding: 0; color: #94a3b8; list-style: none;">
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>Furfural</strong> / <strong>Ciclo-hexano</strong> / <strong>Benzeno</strong>
                            </li>
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>Sulfolano</strong> / <strong>n-Octano</strong> / <strong>Tolueno</strong>
                            </li>
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>2,5-Hexanodiona</strong> / <strong>1-Hexeno</strong> / <strong>n-Hexano</strong>
                            </li>
                            <li style="margin-bottom: 6px;">
                                <span style="color: #22c55e;">✓</span> <strong>1,4-Dioxano</strong> / <strong>n-Hexano</strong> / <strong>Metilciclopentano</strong>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>`;
    }
    
    // PAINEL PARA UNIFAC
    else if (model === 'UNIFAC') {
        html = `
        <div class="alert alert-info" style="margin-bottom: 1rem;">
            <div style="display: flex; align-items: flex-start; gap: 10px;">
                <i class="bi bi-stars" style="font-size: 1.2rem; color: #a5b4fc; flex-shrink: 0;"></i>
                <div style="flex-grow: 1;">
                    <strong style="color: #e5e7eb;">🔮 UNIFAC - Modelo Preditivo Universal</strong>
                    <div style="margin-top: 8px; font-size: 0.85rem; color: #cbd5e1;">
                        <p style="margin: 0 0 8px 0;">
                            <strong>Não requer parâmetros binários!</strong> Funciona para qualquer combinação de componentes.
                        </p>
                        <ul style="margin: 0; padding: 0 0 0 16px; color: #94a3b8;">
                            <li>✨ Contribuição de grupos funcionais</li>
                            <li>✨ Parâmetros universais (Fredenslund 1975)</li>
                            <li>✨ Ideal para screening de solventes</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>`;
    }
    
    if (html) {
        infoPanel.innerHTML = html;
        infoPanel.style.display = 'block';
    }
}


// ============================================================================
// CAMPOS DINÂMICOS / TIPOS DE CÁLCULO
// ============================================================================


function updateFields() {
  const calcType = document.getElementById('calcType').value;
  const container = document.getElementById('dynamicFields');
  if (!container) return;

  let html = '';

  // Temperatura (sempre presente em ELL)
  html += `
    <div class="row mb-3">
      <div class="col-md-6">
        <label class="form-label">Temperatura</label>
        <div class="input-group-compact">
          <input type="number" class="form-control" id="temperature" value="25.0" step="0.1">
          <select class="form-select" id="tempUnit">
            <option value="C">°C</option>
            <option value="K">K</option>
          </select>
        </div>
        <small class="text-muted-soft mt-1" style="font-size: 0.78rem;">
          ELL é tipicamente calculado a temperatura constante
        </small>
      </div>
    </div>
  `;

  // ========================================================================
  // CAMPOS ESPECÍFICOS POR TIPO DE CÁLCULO
  // ========================================================================
  
  if (calcType === 'ell_flash') {
    html += `
      <div class="row mb-3">
        <div class="col-12">
          <label class="form-label">Composição Global (z<sub>feed</sub>)</label>
          <div class="row">
    `;

    const n = Math.max(1, selectedComponents.length);
    selectedComponents.forEach((comp, i) => {
        html += `
            <div class="col-md-4 mb-2">
                <div class="input-group input-group-sm">
                    <span class="input-group-text">z${i+1}</span>
                    <input type="number" class="form-control" id="z${i+1}" 
                          value="${(1/n).toFixed(3)}" step="0.001" min="0" max="1">
                </div>
                <small class="text-muted-soft">${escapeHtml(comp.name_pt || comp.name)}</small>
            </div>
        `;
    });


    html += `
          </div>
          <small class="text-muted-soft">
            A soma das frações molares deve ser 1,0
          </small>
        </div>
      </div>
    `;
  }
  
  else if (calcType === 'ternary_diagram') {
      html += `
        <div class="row mb-3">
          <div class="col-md-6">
            <label class="form-label">Número de Tie-Lines</label>
            <input type="number" class="form-control" id="ntielines" value="5" step="1" min="3" max="10">
            <!--                                         ^^^^^^^^^  -->
            <!--                                         SEM UNDERSCORES -->
            <small class="text-muted-soft mt-1" style="font-size: 0.78rem;">
              Linhas de amarração conectando fases em equilíbrio (recomendado: 5-7)
            </small>
          </div>
        </div>
      `;
  }

  
  // ========================================================================
  // ⭐ NOVO: CAMPOS DE EXTRAÇÃO MULTI-ESTÁGIOS - SIMPLIFICADOS
  // ========================================================================
  
  else if (calcType === 'extraction') {
    html += `
      <div class="extraction-fields">
        <div class="field-group-title">
          <i class="bi bi-gear-fill"></i> Parâmetros de Extração (Método de Kremser-Souders-Brown)
        </div>
        
        <!-- Modo de cálculo -->
        <div class="extraction-mode-selector mb-3">
          <div class="mode-radio-card active" id="mode-card-recovery">
            <label>
              <input type="radio" name="extraction_mode" value="recovery" checked onchange="toggleExtractionMode()">
              <strong>Calcular N</strong> para recuperação desejada
            </label>
          </div>
          <div class="mode-radio-card" id="mode-card-fixed">
            <label>
              <input type="radio" name="extraction_mode" value="fixed" onchange="toggleExtractionMode()">
              <strong>Calcular recuperação</strong> com N fixo
            </label>
          </div>
        </div>
        
        <!-- Composição da alimentação -->
        <div class="mb-3">
          <label class="form-label">Composição da Alimentação (z<sub>feed</sub>)</label>
          <div class="row">
    `;
    
    const n = Math.max(1, selectedComponents.length);
    selectedComponents.forEach((comp, i) => {
        html += `
            <div class="col-md-4 mb-2">
                <div class="input-group input-group-sm">
                    <span class="input-group-text">z${i+1}</span>
                    <input type="number" class="form-control" id="z${i+1}" 
                          value="${(1/n).toFixed(3)}" step="0.001" min="0" max="1">
                </div>
                <small class="text-muted-soft">${escapeHtml(comp.name_pt || comp.name)}</small>
            </div>
        `;
    });

    
    html += `
          </div>
        </div>
        
        <!-- Parâmetros operacionais -->
        <div class="row mb-3">
          <div class="col-md-6">
            <label class="form-label">Razão Solvente/Alimentação (S/F)</label>
            <input type="number" class="form-control" id="S_F_ratio" value="2.0" step="0.1" min="0.1" max="10">
            <small class="text-muted-soft mt-1" style="font-size: 0.78rem;">
              Razão molar entre solvente e alimentação (típico: 1-5)
            </small>
          </div>
          
          <div class="col-md-6">
            <label class="form-label">Eficiência de Murphree (η)</label>
            <input type="number" class="form-control" id="efficiency" value="0.7" step="0.05" min="0.1" max="1.0">
            <small class="text-muted-soft mt-1" style="font-size: 0.78rem;">
              Eficiência da coluna (típico: 0.5-0.9)
            </small>
          </div>
        </div>
        
        <!-- Campos dinâmicos baseados no modo -->
        <div id="extraction-dynamic-fields">
          <!-- Preenchido via JavaScript -->
        </div>
        
        <div class="alert alert-info" style="font-size: 0.85rem;">
          <i class="bi bi-info-circle"></i>
          <strong>Método de Kremser-Souders-Brown</strong><br>
          Calcula número de estágios ideais para extração em contracorrente.
          O soluto será detectado automaticamente como o componente com menor K (menos distribuído entre fases).
        </div>
      </div>
    `;
    
    // Renderizar campos dinâmicos iniciais
    setTimeout(() => {
      updateExtractionDynamicFields('recovery');
    }, 100);
  }

  container.innerHTML = html;
}


// ========================================================================
// ⭐ NOVA FUNÇÃO: Toggle entre modos de extração
// ========================================================================

function toggleExtractionMode() {
  const mode = document.querySelector('input[name="extraction_mode"]:checked').value;
  
  // Atualizar visual dos cards
  document.getElementById('mode-card-recovery').classList.toggle('active', mode === 'recovery');
  document.getElementById('mode-card-fixed').classList.toggle('active', mode === 'fixed');
  
  // Atualizar campos dinâmicos
  updateExtractionDynamicFields(mode);
}

// ========================================================================
// ⭐ NOVA FUNÇÃO: Atualizar campos dinâmicos de extração
// ========================================================================

// ============================================================================
// NOVA FUNÇÃO: Atualizar campos dinâmicos de extração
// ============================================================================

function updateExtractionDynamicFields(mode) {
  const container = document.getElementById('extraction-dynamic-fields');
  if (!container) return;
  
  let html = '';
  
  if (mode === 'recovery') {
    html = `
      <div class="row mb-3">
        <div class="col-md-6">
          <label class="form-label">Recuperação Alvo (%)</label>
          <input type="number" class="form-control" id="target_recovery" value="95" step="1" min="50" max="99.9">
          <small class="text-muted-soft mt-1" style="font-size: 0.78rem;">
            Percentual do soluto a ser removido da fase rafinado
          </small>
        </div>
      </div>
    `;
  } else {
    html = `
      <div class="row mb-3">
        <div class="col-md-6">
          <label class="form-label">Número de Estágios (N)</label>
          <input type="number" class="form-control" id="N_stages" value="5" step="1" min="1" max="20">
          <small class="text-muted-soft mt-1" style="font-size: 0.78rem;">
            Número de estágios de equilíbrio na coluna
          </small>
        </div>
      </div>
    `;
  }
  
  // ⚠️ REMOVIDO: Campo "Selecionar soluto" (agora é auto-detectado)
  
  container.innerHTML = html;
}




// ============================================================================
// CÁLCULO PRINCIPAL
// ============================================================================

/**
 * DEBUG: Inspecionar DOM atual
 */
function debugDOM() {
    console.log('[DEBUG DOM] ========================================');
    console.log('[DEBUG DOM] dynamicFields innerHTML length:', document.getElementById('dynamicFields')?.innerHTML?.length || 0);
    
    // 🔍 PROCURAR TODOS OS INPUTS DENTRO DE dynamicFields
    const container = document.getElementById('dynamicFields');
    if (container) {
        const inputs = container.querySelectorAll('input[type="number"]');
        console.log('[DEBUG DOM] Total de inputs encontrados:', inputs.length);
        inputs.forEach((input, idx) => {
            console.log(`[DEBUG DOM] Input ${idx}: id="${input.id}", value="${input.value}"`);
        });
    }
    
    console.log('[DEBUG DOM] SFratio existe?', !!document.getElementById('SFratio'));
    console.log('[DEBUG DOM] S_F_ratio existe?', !!document.getElementById('S_F_ratio')); // 🔍 Teste alternativo
    console.log('[DEBUG DOM] efficiency existe?', !!document.getElementById('efficiency'));
    console.log('[DEBUG DOM] targetrecovery existe?', !!document.getElementById('targetrecovery'));
    console.log('[DEBUG DOM] target_recovery existe?', !!document.getElementById('target_recovery')); // 🔍 Teste alternativo
    console.log('[DEBUG DOM] z1 existe?', !!document.getElementById('z1'));
    console.log('[DEBUG DOM] z2 existe?', !!document.getElementById('z2'));
    console.log('[DEBUG DOM] z3 existe?', !!document.getElementById('z3'));
    console.log('[DEBUG DOM] ========================================');
}



/**
 * CÁLCULO PRINCIPAL
 */
async function calculate() {
    if (selectedComponents.length !== 3) {
        alert(`ELL requer exatamente 3 componentes. Você selecionou ${selectedComponents.length}.`);
        return;
    }

    const calcType = document.getElementById('calcType').value;
    const model = document.getElementById('model').value;

    console.log(`[ELL] Iniciando cálculo: tipo=${calcType}, modelo=${model}`);

    // ✅ VERIFICAR SE OS CAMPOS JÁ EXISTEM (COM IDs CORRETOS!)
    if (calcType === 'extraction') {
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // ✅ USAR O ID CORRETO: "S_F_ratio" (com underscore)
        const SFratioInput = document.getElementById('S_F_ratio');
        
        if (!SFratioInput) {
            console.log('[ELL] ⚠️ Campos de extração não encontrados. Tentando criar...');
            let attempts = 0;
            const maxAttempts = 3;
            
            while (!document.getElementById('S_F_ratio') && attempts < maxAttempts) {
                attempts++;
                console.log(`[ELL] Tentativa ${attempts}/${maxAttempts}: Criando campos...`);
                updateFields();
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            // Validação final
            if (!document.getElementById('S_F_ratio')) {
                alert('Erro: Não foi possível criar os campos de extração. Por favor, recarregue a página.');
                console.error('[ELL] ERRO CRÍTICO: Campos de extração não foram criados após 3 tentativas');
                return;
            }
        } else {
            console.log('[ELL] ✅ Campos de extração já existem. Prosseguindo...');
        }
        
    } else if (calcType === 'ternary_diagram') {
        await new Promise(resolve => setTimeout(resolve, 100));
        const nTieLinesInput = document.getElementById('ntielines');
        
        if (!nTieLinesInput) {
            console.log('[ELL] ⚠️ Campos de diagrama não encontrados. Tentando criar...');
            let attempts = 0;
            const maxAttempts = 3;
            
            while (!document.getElementById('ntielines') && attempts < maxAttempts) {
                attempts++;
                console.log(`[ELL] Tentativa ${attempts}/${maxAttempts}: Criando campos...`);
                updateFields();
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            if (!document.getElementById('ntielines')) {
                alert('Erro: Não foi possível criar os campos de diagrama. Por favor, recarregue a página.');
                console.error('[ELL] ERRO CRÍTICO: Campos de diagrama não foram criados após 3 tentativas');
                return;
            }
        } else {
            console.log('[ELL] ✅ Campos de diagrama já existem. Prosseguindo...');
        }
    }

    // ✅ EXECUTAR O CÁLCULO
    console.log('[ELL] ✅ Todos os campos validados. Executando cálculo...');
    
    if (calcType === 'ell_flash') {
        await calculateFlash(model);
    } else if (calcType === 'ternary_diagram') {
        await generateTernaryDiagram(model);
    } else if (calcType === 'extraction') {
        await calculateExtraction(model);
    }
}





/**
 * FLASH L1-L2
 */
async function calculateFlash(model) {
    const components = selectedComponents.map(c => c.name_en || c.name);
    const temperature = parseFloat(document.getElementById('temperature').value);
    const tempUnit = document.getElementById('tempUnit').value;

    // Coletar composições globais
    const z_feed = [];
    for (let i = 0; i < 3; i++) {
        const el = document.getElementById(`z${i + 1}`);
        const val = parseFloat(el ? el.value : NaN);
        z_feed.push(isNaN(val) ? 0 : val);
    }

    const sumZ = z_feed.reduce((a, b) => a + b, 0);
    if (sumZ < 0.999 || sumZ > 1.001) {
        alert(`A soma das frações molares globais (z_feed) deve ser igual a 1,0. Soma atual: ${sumZ.toFixed(3)}`);
        return;
    }

    const payload = {
        components,
        z_feed,
        temperature,
        temperature_unit: tempUnit,
        model
    };

    // ⭐ MOSTRAR LOADING
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultsDiv = document.getElementById('results');
    const loadingText = document.getElementById('loading-text');
    const loadingSubtitle = document.getElementById('loading-subtitle');
    const timeEstimate = document.getElementById('time-estimate');

    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
        loadingText.innerHTML = 'Calculando Flash L1-L2<span class="loading-dots"></span>';
        loadingSubtitle.textContent = 'Processando equilíbrio termodinâmico bifásico';
        timeEstimate.textContent = '~1-3 segundos';
    }
    if (resultsDiv) resultsDiv.style.display = 'none';

    try {
        const res = await fetch('/ell/calculate/flash', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        // ⭐ ESCONDER LOADING
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'block';

        if (data.success) {
            window.lastAiSuggestion = data.ai_suggestion || null;
            displayFlashResults(data.results, window.lastAiSuggestion);
            window.lastPointResults = data.results;
            lastFlashResults = data.results;
            lastDiagramData = null;
            lastDiagramType = null;
            lastModel = model;
            lastTemperature = temperature;

            const btnPts = document.getElementById('export-buttons-points');
            const btnDiag = document.getElementById('export-buttons');
            if (btnPts) btnPts.style.display = 'block';
            if (btnDiag) btnDiag.style.display = 'none';

            const compContainer = document.getElementById('comparison-diagram-container');
            if (compContainer) compContainer.style.display = 'none';
        } else {
            alert(`Erro no cálculo: ${data.error || 'Erro desconhecido'}`);
        }
    } catch (err) {
        // ⭐ ESCONDER LOADING EM CASO DE ERRO
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'block';
        
        alert(`Erro no cálculo: ${err.message}`);
        console.error(err);
    }
}


/**
 * NOVO: EXTRAÇÃO MULTI-ESTÁGIOS (KREMSER-SOUDERS-BROWN)
 */
async function calculateExtraction(model) {
    const components = selectedComponents.map(c => c.name_en || c.name);
    const temperature = parseFloat(document.getElementById('temperature').value);
    const tempUnit = document.getElementById('tempUnit').value;

    // Coletar composições globais
    const z_feed = [];
    for (let i = 0; i < 3; i++) {
        const el = document.getElementById(`z${i + 1}`);
        const val = parseFloat(el ? el.value : NaN);
        z_feed.push(isNaN(val) ? 0 : val);
    }

    const sumZ = z_feed.reduce((a, b) => a + b, 0);
    if (sumZ < 0.999 || sumZ > 1.001) {
        alert(`A soma das frações molares globais (z_feed) deve ser igual a 1,0. Soma atual: ${sumZ.toFixed(3)}`);
        return;
    }

    // ✅ VALIDAÇÃO: Verificar se os campos existem antes de acessar (IDs CORRETOS!)
    const SFratioInput = document.getElementById('S_F_ratio');      // ✅ COM UNDERSCORE
    const efficiencyInput = document.getElementById('efficiency');
    
    if (!SFratioInput || !efficiencyInput) {
        alert('Erro: Campos de extração não encontrados. Certifique-se de que o tipo de cálculo está configurado como "Extração".');
        console.error('[ELL EXTRAÇÃO] Campos não encontrados:', {
            S_F_ratio: !!SFratioInput,
            efficiency: !!efficiencyInput
        });
        return;
    }

    const S_F_ratio = parseFloat(SFratioInput.value);
    const efficiency = parseFloat(efficiencyInput.value);

    // ✅ VALIDAÇÃO: Verificar se o modo está selecionado
    const modeInput = document.querySelector('input[name="extraction_mode"]:checked');
    if (!modeInput) {
        alert('Erro: Modo de extração não selecionado.');
        return;
    }
    const mode = modeInput.value;

    let endpoint = '/ell/calculate/extraction';
    let payload = {
        components,
        z_feed,
        temperature,
        temperature_unit: tempUnit,
        model,
        S_F_ratio,
        efficiency
    };

    if (mode === 'recovery') {
        const targetRecoveryInput = document.getElementById('target_recovery'); // ✅ COM UNDERSCORE
        if (!targetRecoveryInput) {
            alert('Erro: Campo "Recuperação Alvo" não encontrado.');
            return;
        }
        const target_recovery = parseFloat(targetRecoveryInput.value) / 100.0;
        payload.target_recovery = target_recovery;
    } else {
        endpoint = '/ell/calculate/extraction-fixed';
        const NstagesInput = document.getElementById('N_stages'); // ✅ COM UNDERSCORE
        if (!NstagesInput) {
            alert('Erro: Campo "Número de Estágios" não encontrado.');
            return;
        }
        const N_stages = parseInt(NstagesInput.value);
        payload.N_stages = N_stages;
    }

    console.log('[ELL EXTRAÇÃO] Payload:', payload);

    // ⭐ MOSTRAR LOADING
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultsDiv = document.getElementById('results');
    const loadingText = document.getElementById('loading-text');
    const loadingSubtitle = document.getElementById('loading-subtitle');
    const timeEstimate = document.getElementById('time-estimate');

    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
        loadingText.innerHTML = 'Calculando Extração Multi-Estágios<span class="loading-dots"></span>';
        loadingSubtitle.textContent = 'Aplicando método de Kremser-Souders-Brown';
        timeEstimate.textContent = '~3-10 segundos';
    }
    if (resultsDiv) resultsDiv.style.display = 'none';

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        console.log('[ELL EXTRAÇÃO] Resposta:', data);

        // ⭐ ESCONDER LOADING
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'block';

        if (data.success) {
            window.lastAiSuggestion = data.ai_suggestion || null;
            displayExtractionResults(data.results, window.lastAiSuggestion, mode);
            window.lastPointResults = data.results;
            lastFlashResults = null;
            lastDiagramData = data.results;
            lastDiagramType = 'extraction';
            lastModel = model;
            lastTemperature = temperature;

            const btnPts = document.getElementById('export-buttons-points');
            const btnDiag = document.getElementById('export-buttons');
            if (btnPts) btnPts.style.display = 'block';
            if (btnDiag) btnDiag.style.display = 'none';

            const compContainer = document.getElementById('comparison-diagram-container');
            if (compContainer) compContainer.style.display = 'none';
        } else {
            alert(`Erro no cálculo: ${data.error || 'Erro desconhecido'}`);
        }
    } catch (err) {
        // ⭐ ESCONDER LOADING EM CASO DE ERRO
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'block';
        
        alert(`Erro no cálculo: ${err.message}`);
        console.error('[ELL EXTRAÇÃO] Erro:', err);
    }
}

// ============================================================================
// EXIBIÇÃO DE RESULTADOS: FLASH (CORRIGIDO COM VALIDAÇÃO)
// ============================================================================

/**
 * Formata número com segurança (evita erro de toFixed em undefined)
 */
function safeFormat(value, decimals = 4) {
    if (value === null || value === undefined || isNaN(value)) {
        return 'N/A';
    }
    if (typeof value === 'number') {
        return value.toFixed(decimals);
    }
    // Tentar converter string para número
    const num = parseFloat(value);
    if (!isNaN(num)) {
        return num.toFixed(decimals);
    }
    return 'N/A';
}

function displayFlashResults(results, aiSuggestion = null) {
  const resultsDiv = document.getElementById('results');
  if (!resultsDiv) return;

  // Renderizar recomendação da IA
  renderAIRecommendation(aiSuggestion);

  let html = '<div class="results-card">';
  html += '<h4 class="mb-3"><i class="bi bi-droplet-half"></i> Resultados do Flash L1-L2</h4>';

  // ✅ VALIDAÇÃO: Verificar se results existe e tem dados válidos
  if (!results) {
    html += '<div class="alert alert-danger">Erro: Nenhum resultado retornado do backend.</div>';
    html += '</div>';
    resultsDiv.innerHTML = html;
    return;
  }

  // ✅ Detectar sistema monofásico
  const isTwoPhase = results.two_phase === true;
  const hasWarning = results.warning !== null && results.warning !== undefined;

  // Status de convergência
  if (!isTwoPhase || hasWarning) {
    html += `
      <div class="alert alert-warning mb-3">
        <i class="bi bi-exclamation-triangle"></i>
        <strong>Sistema monofásico:</strong> ${escapeHtml(results.warning || 'Não houve separação de fases. O sistema está completamente miscível nesta temperatura e composição.')}
      </div>
    `;
  } else if (results.converged) {
    html += `
      <div class="alert alert-success mb-3">
        <i class="bi bi-check-circle"></i>
        <strong>Convergência alcançada:</strong> Sistema bifásico detectado. 
        Resíduo: ${safeFormat(results.residual, 2)}
      </div>
    `;
  }

  // Condições
  html += `
    <div class="row g-3">
      <div class="col-md-4">
        <h6 class="section-title-sm">Condições</h6>
        <div class="results-grid">
          <div class="result-item">
            <span class="label">T (°C)</span>
            <span class="value">${safeFormat(results.TC, 2)}</span>
          </div>
          <div class="result-item">
            <span class="label">T (K)</span>
            <span class="value">${safeFormat(results.TK, 2)}</span>
          </div>
          <div class="result-item">
            <span class="label">Modelo</span>
            <span class="value">${escapeHtml(results.model || 'N/A')}</span>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <h6 class="section-title-sm">Frações de Fase</h6>
        <div class="results-grid">
          <div class="result-item">
            <span class="label">β (Fração L2)</span>
            <span class="value">${safeFormat(results.beta, 6)}</span>
          </div>
          <div class="result-item">
            <span class="label">1-β (Fração L1)</span>
            <span class="value">${safeFormat(1.0 - (results.beta || 0), 6)}</span>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <h6 class="section-title-sm">Interpretação</h6>
        <div class="text-muted-soft" style="font-size: 0.85rem; padding: 0.5rem;">
          ${!isTwoPhase 
            ? 'Sistema homogêneo: apenas uma fase líquida estável'
            : (results.beta > 0.5 
              ? 'Sistema majoritariamente na fase L2 (fase rica em componente mais apolar)'
              : 'Sistema majoritariamente na fase L1 (fase rica em componente mais polar)')}
        </div>
      </div>
    </div>
  `;

  // Composições por componente
  html += `
    <div class="mt-3">
      <h6 class="section-title-sm">Composições e Propriedades</h6>
      <table class="table table-dark table-bordered" style="font-size: 0.9rem;">
        <thead>
          <tr style="background: rgba(59, 130, 246, 0.2);">
            <th>Componente</th>
            <th>z<sub>feed</sub></th>
            <th>x<sub>L1</sub></th>
            <th>x<sub>L2</sub></th>
            <th>K = x<sub>L2</sub>/x<sub>L1</sub></th>
            <th>γ<sub>L1</sub></th>
            <th>γ<sub>L2</sub></th>
          </tr>
        </thead>
        <tbody>
  `;

  // ✅ CORREÇÃO: Usar arrays diretos ao invés de propriedades nomeadas
  const z_feed = results.z_feed || [0, 0, 0];
  const x_L1 = results.x_L1 || [0, 0, 0];
  const x_L2 = results.x_L2 || [0, 0, 0];
  const K_values = results.K || [0, 0, 0];
  const gamma_L1 = results.gamma_L1 || [1, 1, 1];
  const gamma_L2 = results.gamma_L2 || [1, 1, 1];

  selectedComponents.forEach((comp, i) => {
    html += `
      <tr>
        <td><strong>${escapeHtml(comp.name)}</strong></td>
        <td>${safeFormat(z_feed[i], 4)}</td>
        <td>${safeFormat(x_L1[i], 4)}</td>
        <td>${safeFormat(x_L2[i], 4)}</td>
        <td>${safeFormat(K_values[i], 4)}</td>
        <td>${safeFormat(gamma_L1[i], 4)}</td>
        <td>${safeFormat(gamma_L2[i], 4)}</td>
      </tr>
    `;
  });

  html += `
        </tbody>
      </table>
      <small class="text-muted-soft">
        <strong>K > 1:</strong> componente se distribui mais para L2 · 
        <strong>K < 1:</strong> componente se distribui mais para L1 · 
        <strong>γ > 1:</strong> desvio positivo da idealidade
      </small>
    </div>
  `;

  html += '</div>';
  resultsDiv.innerHTML = html;
}

// FUNÇÃO DE DEBUG - ADICIONAR ANTES DE plotTernaryDiagram()
function debugTieLines(results) {
    console.log("=".repeat(70));
    console.log("🔍 DEBUG: Estrutura dos dados recebidos");
    console.log("=".repeat(70));
    
    console.log("Results completo:", results);
    console.log("\nTie-lines array:", results.tie_lines);
    
    if (results.tie_lines && results.tie_lines.length > 0) {
        const firstTieLine = results.tie_lines[0];
        console.log("\nPrimeira tie-line (estrutura completa):");
        console.log(JSON.stringify(firstTieLine, null, 2));
        
        console.log("\nPropriedades disponíveis:");
        console.log("- x_L1:", firstTieLine.x_L1);
        console.log("- x_L2:", firstTieLine.x_L2);
        console.log("- xL1:", firstTieLine.xL1);
        console.log("- xL2:", firstTieLine.xL2);
        console.log("- beta:", firstTieLine.beta);
    }
    
    console.log("=".repeat(70));
}

// ============================================================================
// ⭐ NOVA FUNÇÃO: EXIBIÇÃO DE RESULTADOS DE EXTRAÇÃO
// ============================================================================

function displayExtractionResults(results, aiSuggestion = null, mode = 'recovery') {
  const resultsDiv = document.getElementById('results');
  if (!resultsDiv) return;

  // Renderizar recomendação da IA
  renderAIRecommendation(aiSuggestion);

  let html = '<div class="results-card">';
  html += '<h4 class="mb-3"><i class="bi bi-funnel"></i> Resultados da Extração Multi-Estágios</h4>';

  // Validação
  if (!results) {
    html += '<div class="alert alert-danger">Erro: Nenhum resultado retornado do backend.</div>';
    html += '</div>';
    resultsDiv.innerHTML = html;
    return;
  }

  // Status de convergência
  if (results.converged) {
    html += `
      <div class="alert alert-success mb-3">
        <i class="bi bi-check-circle"></i>
        <strong>Cálculo concluído com sucesso!</strong> 
        ${mode === 'recovery' 
          ? `Número de estágios calculado: <strong>${results.N_rounded}</strong>` 
          : `Recuperação alcançada: <strong>${(results.recovery_achieved * 100).toFixed(2)}%</strong>`}
      </div>
    `;
  } else {
    html += `
      <div class="alert alert-warning mb-3">
        <i class="bi bi-exclamation-triangle"></i>
        <strong>Aviso:</strong> ${results.warning || 'Cálculo não convergiu completamente'}
      </div>
    `;
  }

  // Dentro da função displayExtractionResults(), substituir a seção de Parâmetros Operacionais:

  // Parâmetros operacionais
  html += `
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <h6 class="section-title-sm">Parâmetros Operacionais</h6>
        <div class="results-grid">
          <div class="result-item">
            <span class="label">Temperatura</span>
            <span class="value">${safeFormat(results.TC, 1)}°C</span>
          </div>
          <div class="result-item">
            <span class="label">Modelo</span>
            <span class="value">${escapeHtml(results.model || 'N/A')}</span>
          </div>
          <div class="result-item">
            <span class="label">Razão S/F</span>
            <span class="value">${safeFormat(results.S_F_ratio, 2)}</span>
          </div>
          <div class="result-item" style="background: rgba(34, 197, 94, 0.1);">
            <span class="label">⭐ Soluto Detectado</span>
            <span class="value">${escapeHtml(results.solute_name || selectedComponents[results.solute_index || 0].name)}</span>
          </div>
        </div>
      </div>


      <div class="col-md-4">
        <h6 class="section-title-sm">Número de Estágios</h6>
        <div class="results-grid">
          <div class="result-item">
            <span class="label">N<sub>teórico</sub></span>
            <span class="value">${safeFormat(results.N_theoretical, 2)}</span>
          </div>
          <div class="result-item">
            <span class="label">N<sub>real</sub> (η = ${safeFormat(results.efficiency * 100, 0)}%)</span>
            <span class="value">${safeFormat(results.N_actual, 2)}</span>
          </div>
          <div class="result-item">
            <span class="label">N<sub>arredondado</sub></span>
            <span class="value" style="color: #22c55e; font-size: 1.2rem;">${results.N_rounded}</span>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <h6 class="section-title-sm">Desempenho</h6>
        <div class="results-grid">
          <div class="result-item">
            <span class="label">Fator de Extração (E)</span>
            <span class="value">${safeFormat(results.extraction_factor, 4)}</span>
          </div>
          <div class="result-item">
            <span class="label">K (distribuição)</span>
            <span class="value">${safeFormat(results.K_distribution, 4)}</span>
          </div>
          <div class="result-item">
            <span class="label">Recuperação</span>
            <span class="value" style="color: #22c55e; font-size: 1.1rem;">${safeFormat(results.recovery_achieved * 100, 2)}%</span>
          </div>
        </div>
      </div>
    </div>
  `;

  // Composições
  if (results.x_raffinate && results.x_extract) {
    html += `
      <div class="mt-3">
        <h6 class="section-title-sm">Composições das Correntes</h6>
        <table class="table table-dark table-bordered" style="font-size: 0.9rem;">
          <thead>
            <tr style="background: rgba(59, 130, 246, 0.2);">
              <th>Componente</th>
              <th>z<sub>feed</sub></th>
              <th>x<sub>rafinado</sub> (fase empobrecida)</th>
              <th>x<sub>extrato</sub> (fase rica)</th>
            </tr>
          </thead>
          <tbody>
    `;

    selectedComponents.forEach((comp, i) => {
      const isSolute = i === (results.solute_index || 0);
      html += `
        <tr ${isSolute ? 'style="background: rgba(34, 197, 94, 0.1);"' : ''}>
          <td><strong>${escapeHtml(comp.name)}</strong> ${isSolute ? '<span class="badge bg-success">Soluto</span>' : ''}</td>
          <td>${safeFormat(results.z_feed[i], 4)}</td>
          <td>${safeFormat(results.x_raffinate[i], 4)}</td>
          <td>${safeFormat(results.x_extract[i], 4)}</td>
        </tr>
      `;
    });

    html += `
          </tbody>
        </table>
        <small class="text-muted-soft">
          <strong>Rafinado:</strong> corrente de saída pobre em soluto · 
          <strong>Extrato:</strong> corrente de solvente rica em soluto
        </small>
      </div>
    `;
  }

  // Interpretação
  html += `
    <div class="mt-4 p-3" style="background: rgba(56, 189, 248, 0.05); border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2);">
      <h6 class="mb-2"><i class="bi bi-lightbulb"></i> Interpretação dos Resultados</h6>
      <ul style="margin: 0; font-size: 0.85rem; color: #94a3b8;">
        <li><strong>Fator de Extração (E = ${safeFormat(results.extraction_factor, 2)}):</strong> 
          ${results.extraction_factor > 1.5 
            ? 'Favorável para extração. Soluto transfere-se preferencialmente para o solvente.'
            : results.extraction_factor > 0.7
            ? 'Moderado. Extração possível mas requer mais estágios.'
            : 'Desfavorável. Considere aumentar razão S/F ou mudar solvente.'}
        </li>
        <li><strong>N° de estágios (${results.N_rounded}):</strong> 
          ${results.N_rounded <= 5 
            ? 'Processo compacto, economicamente viável.'
            : results.N_rounded <= 10
            ? 'Moderado. Avaliar custo x benefício.'
            : 'Alto. Considere aumentar S/F ou melhorar eficiência.'}
        </li>
        <li><strong>Recuperação (${safeFormat(results.recovery_achieved * 100, 1)}%):</strong>
          ${results.recovery_achieved >= 0.95
            ? 'Excelente remoção do soluto.'
            : results.recovery_achieved >= 0.85
            ? 'Boa remoção. Adequado para maioria das aplicações.'
            : 'Moderada. Considere adicionar mais estágios.'}
        </li>
      </ul>
    </div>
  `;

  html += '</div>';
  resultsDiv.innerHTML = html;
}


/**
 * DIAGRAMA TERNÁRIO
 */
async function generateTernaryDiagram(model) {
    const components = selectedComponents.map(c => c.name_en || c.name);
    const temperature = parseFloat(document.getElementById('temperature').value);
    const tempUnit = document.getElementById('tempUnit').value;
    
    // ✅ VALIDAÇÃO: Verificar se o elemento existe antes de acessar
    const nTieLinesInput = document.getElementById('ntielines');
    const nTieLines = nTieLinesInput ? parseInt(nTieLinesInput.value) : 5; // Default: 5

    const payload = {
        components,
        temperature,
        temperature_unit: tempUnit,
        model,
        n_tie_lines: nTieLines
    };

    // ⭐ MOSTRAR LOADING COM MENSAGEM ESPECIAL PARA DIAGRAMA
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultsDiv = document.getElementById('results');
    const loadingText = document.getElementById('loading-text');
    const loadingSubtitle = document.getElementById('loading-subtitle');
    const timeEstimate = document.getElementById('time-estimate');

    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
        loadingText.innerHTML = 'Gerando Diagrama Ternário<span class="loading-dots"></span>';
        loadingSubtitle.textContent = 'Calculando curva binodal e tie-lines. Este processo pode levar até 5 minutos';
        timeEstimate.textContent = '~30-180 segundos';
    }
    if (resultsDiv) resultsDiv.style.display = 'none';

    try {
        const res = await fetch('/ell/diagram/ternary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        // ⭐ ESCONDER LOADING
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'block';

        if (data.success) {
            window.lastAiSuggestion = data.ai_suggestion || null;
            renderTernaryDiagram(data.results, window.lastAiSuggestion);
            lastDiagramData = data;
            lastDiagramType = 'ternary';
            lastFlashResults = null;
            window.lastPointResults = null;
            lastModel = model;
            lastTemperature = temperature;

            const btnDiag = document.getElementById('export-buttons');
            const btnPts = document.getElementById('export-buttons-points');
            if (btnDiag) btnDiag.style.display = 'block';
            if (btnPts) btnPts.style.display = 'none';

            const compContainer = document.getElementById('comparison-diagram-container');
            if (compContainer) compContainer.style.display = 'none';
        } else {
            alert(`Erro ao gerar diagrama: ${data.error || 'Erro desconhecido'}`);
        }
    } catch (err) {
        // ⭐ ESCONDER LOADING EM CASO DE ERRO
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'block';
        
        alert(`Erro ao gerar diagrama: ${err.message}`);
        console.error(err);
    }
}




// ============================================================================
// RENDERIZAÇÃO: DIAGRAMA TERNÁRIO (PLOTLY) - CORRIGIDO
// ============================================================================


function renderTernaryDiagram(results, aiSuggestion = null) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    
    renderAIRecommendation(aiSuggestion);
    
    let html = `<div class="results-card">`;
    html += `<h4 class="mb-3"><i class="bi bi-diagram-3"></i> Diagrama Ternário - ${results.model} a ${results.TC.toFixed(1)}°C</h4>`;
    html += `<div id="ternaryDiagram" style="width:100%;height:600px;"></div>`;
    html += `</div>`;
    resultsDiv.innerHTML = html;
    
    // 🔍 ADICIONAR ESTA LINHA:
    setTimeout(() => {
        debugTieLines(results);  // ← DEBUG
        plotTernaryDiagram(results);
    }, 100);
}



/**
 * ORDENA PONTOS AO REDOR DO CENTROIDE (FORMAÇÃO DE CURVA FECHADA SUAVE)
 * VERSÃO 3.7 - CORRIGIDA COM PROJEÇÃO 2D DO TRIÂNGULO EQUILÁTERO
 */
function sortPointsAngular(points) {
    if (points.length <= 2) return points;
    
    console.log(`  🔧 Ordenando ${points.length} pontos...`);
    
    // ========================================================================
    // ETAPA 1: CONVERTER COORDENADAS TERNÁRIAS PARA CARTESIANAS 2D
    // ========================================================================
    // Triângulo equilátero com vértices:
    //   Water (x1):     (0, 0)
    //   TCE (x2):       (1, 0)
    //   Acetone (x3):   (0.5, √3/2)
    //
    // Fórmula de projeção:
    //   x = x2 + 0.5 * x3
    //   y = (√3/2) * x3
    // ========================================================================
    
    const sqrt3_2 = Math.sqrt(3) / 2;
    
    const points2D = points.map(p => {
        const x1 = p[0]; // Water
        const x2 = p[1]; // TCE
        const x3 = p[2]; // Acetone
        
        // Projeção no plano 2D
        const x = x2 + 0.5 * x3;
        const y = sqrt3_2 * x3;
        
        return { 
            ternary: p, 
            x: x, 
            y: y 
        };
    });
    
    // ========================================================================
    // ETAPA 2: CALCULAR CENTROIDE NO ESPAÇO 2D
    // ========================================================================
    
    const centroid_x = points2D.reduce((sum, pt) => sum + pt.x, 0) / points2D.length;
    const centroid_y = points2D.reduce((sum, pt) => sum + pt.y, 0) / points2D.length;
    
    console.log(`  Centroide 2D: (${centroid_x.toFixed(3)}, ${centroid_y.toFixed(3)})`);
    
    // ========================================================================
    // ETAPA 3: CALCULAR ÂNGULO DE CADA PONTO EM RELAÇÃO AO CENTROIDE
    // ========================================================================
    
    const pointsWithAngles = points2D.map(pt => {
        const dx = pt.x - centroid_x;
        const dy = pt.y - centroid_y;
        const angle = Math.atan2(dy, dx); // Retorna [-π, π]
        
        return {
            ternary: pt.ternary,
            angle: angle
        };
    });
    
    // ========================================================================
    // ETAPA 4: ORDENAR POR ÂNGULO CRESCENTE (SENTIDO ANTI-HORÁRIO)
    // ========================================================================
    
    pointsWithAngles.sort((a, b) => a.angle - b.angle);
    
    // Retornar apenas os pontos ternários ordenados
    const ordered = pointsWithAngles.map(item => item.ternary);
    
    console.log(`  ✅ Ordenação concluída: ${ordered.length} pontos`);
    
    return ordered;
}

/**
 * PLOTAGEM DO DIAGRAMA TERNÁRIO ELL
 * VERSÃO 5.0 - SEM ORDENAÇÃO (backend já ordena corretamente)
 */
function plotTernaryDiagram(results) {
    console.log("\n🎨 PLOTANDO DIAGRAMA TERNÁRIO");
    console.log("=".repeat(70));
    
    const components = results.components;
    const comp_rotated = [components[2], components[0], components[1]];
    
    let binodalL1 = results.binodal_L1 || [];
    let binodalL2 = results.binodal_L2 || [];
    
    console.log(`\n📊 Binodal recebida: ${binodalL1.length} pontos L1 + ${binodalL2.length} pontos L2`);
    
    // ========================================================================
    // ETAPA 1: PREPARAR CURVA BINODAL
    // ========================================================================
    
    let binodal_complete;
    
    if (binodalL2.length === 0) {
        // ✅ NOVA LÓGICA: Curva única já fechada pelo backend
        console.log("\n✅ USANDO CURVA ÚNICA (L1 contém toda a binodal)");
        binodal_complete = binodalL1;
    } else {
        // 🔄 COMPATIBILIDADE: Concatenar L1 + L2 (versão antiga)
        console.log("\n🔄 CONCATENANDO L1 + L2 (compatibilidade)");
        binodal_complete = [...binodalL1, ...binodalL2];
    }
    
    console.log(`  ✓ Total: ${binodal_complete.length} pontos`);
    
    // ========================================================================
    // ETAPA 2: ROTACIONAR COORDENADAS
    // ========================================================================
    
    const binodalA = binodal_complete.map(p => p[2]); // Acetone
    const binodalB = binodal_complete.map(p => p[0]); // Water
    const binodalC = binodal_complete.map(p => p[1]); // TCE
    
    // Fechar a curva (garantir que primeiro = último)
    const binodalA_closed = [...binodalA, binodalA[0]];
    const binodalB_closed = [...binodalB, binodalB[0]];
    const binodalC_closed = [...binodalC, binodalC[0]];
    
    console.log(`  ✓ Curva fechada: ${binodalA_closed.length} pontos`);
    
    // ========================================================================
    // TIE-LINES
    // ========================================================================
    
    const tieLines = results.tie_lines || [];
    console.log(`\n🔗 Tie-lines: ${tieLines.length} linhas`);
    
    let traces = [];
    
    // ========================================================================
    // TRACE 1: BINODAL (CURVA FECHADA SUAVE)
    // ========================================================================
    
    if (binodal_complete.length > 0) {
        traces.push({
            type: 'scatterternary',
            mode: 'lines',
            a: binodalA_closed,
            b: binodalB_closed,
            c: binodalC_closed,
            name: 'Curva Binodal',
            line: { 
                color: '#3b82f6',        // Azul vibrante
                width: 3,
                shape: 'spline',         // Suavização por spline
                smoothing: 1.3           // Alta suavização
            },
            fill: 'toself',              // Preencher interior da curva
            fillcolor: 'rgba(59, 130, 246, 0.08)',  // Azul transparente
            hoverinfo: 'skip',
            showlegend: true
        });
        
        console.log(`  ✓ Trace binodal adicionado (${binodalA_closed.length} pontos)`);
    }
    
    // ========================================================================
    // TRACES 2-N: TIE-LINES
    // ========================================================================
    
    tieLines.forEach((tieLine, idx) => {
        const xL1 = tieLine.x_L1;
        const xL2 = tieLine.x_L2;
        
        // Validação
        if (!Array.isArray(xL1) || !Array.isArray(xL2) || 
            xL1.length !== 3 || xL2.length !== 3) {
            console.warn(`  ⚠️ Tie-line ${idx + 1}: Dados inválidos`);
            return;
        }
        
        // Rotacionar coordenadas
        const a_values = [Number(xL1[2]), Number(xL2[2])];  // Acetone
        const b_values = [Number(xL1[0]), Number(xL2[0])];  // Water
        const c_values = [Number(xL1[1]), Number(xL2[1])];  // TCE
        
        traces.push({
            type: 'scatterternary',
            mode: 'lines+markers',
            a: a_values,
            b: b_values,
            c: c_values,
            name: `Tie-line ${idx + 1}`,
            line: { 
                color: '#22c55e',        // Verde vibrante
                width: 2
            },
            marker: { 
                symbol: 'diamond',       // Diamante nas extremidades
                size: 8, 
                color: '#22c55e',
                line: { color: '#ffffff', width: 1 }
            },
            text: [`L1`, `L2`],
            hovertemplate: 
                `<b>Tie-line ${idx + 1}</b><br>` +
                `β = ${tieLine.beta.toFixed(3)}<br>` +
                `${comp_rotated[0]}: %{a:.3f}<br>` +
                `${comp_rotated[1]}: %{b:.3f}<br>` +
                `${comp_rotated[2]}: %{c:.3f}<extra></extra>`,
            showlegend: (idx === 0)  // Apenas primeira tie-line na legenda
        });
        
        console.log(`  ✓ Tie-line ${idx + 1} adicionada (dist: ${tieLine.distance?.toFixed(3) || 'N/A'})`);
    });
    
    console.log(`\n✅ Total traces: ${traces.length} (1 binodal + ${tieLines.length} tie-lines)`);
    console.log("=".repeat(70));
    
    // ========================================================================
    // LAYOUT
    // ========================================================================
    
    const layout = {
        title: {
            text: `Diagrama Ternário ELL - ${components.join(' / ')} @ ${results.TC}°C`,
            font: { size: 16, color: '#f1f5f9' }
        },
        ternary: {
            sum: 1,
            aaxis: {
                title: { text: comp_rotated[0], font: { size: 14, color: '#f1f5f9' } },
                min: 0,
                linewidth: 2,
                linecolor: '#64748b',
                gridcolor: 'rgba(148, 163, 184, 0.15)'
            },
            baxis: {
                title: { text: comp_rotated[1], font: { size: 14, color: '#f1f5f9' } },
                min: 0,
                linewidth: 2,
                linecolor: '#64748b',
                gridcolor: 'rgba(148, 163, 184, 0.15)'
            },
            caxis: {
                title: { text: comp_rotated[2], font: { size: 14, color: '#f1f5f9' } },
                min: 0,
                linewidth: 2,
                linecolor: '#64748b',
                gridcolor: 'rgba(148, 163, 184, 0.15)'
            },
            bgcolor: 'rgba(15, 23, 42, 0.4)'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: true,
        legend: {
            font: { color: '#f1f5f9' },
            bgcolor: 'rgba(15, 23, 42, 0.8)',
            bordercolor: '#64748b',
            borderwidth: 1
        },
        margin: { t: 70, b: 50, l: 50, r: 50 }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };
    
    // ========================================================================
    // RENDERIZAÇÃO
    // ========================================================================
    
    console.log("\n🎨 Chamando Plotly.newPlot()...");
    
    try {
        Plotly.newPlot('ternaryDiagram', traces, layout, config);
        currentDiagram = true;
        console.log("✅ Plotagem concluída com sucesso!");
    } catch (err) {
        console.error("❌ Erro na plotagem:", err);
        alert(`Erro ao plotar diagrama: ${err.message}`);
    }
}


// ============================================================================
// EXEMPLOS DO PRAUSNITZ (CORRIGIDOS - VERSÃO 3.0)
// ============================================================================


function addPrausnitzExamplesButton() {
  const container = document.querySelector('.calc-panel .panel-header');
  if (!container) return;
  
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn-sim btn-sim-ghost btn-sm';
  btn.innerHTML = '<i class="bi bi-book"></i> Exemplos';
  btn.onclick = showPrausnitzExamplesModal;
  btn.style.marginLeft = 'auto';
  
  container.appendChild(btn);
}


function showPrausnitzExamplesModal() {
  const examples = getPrausnitzExamples();
  
  let html = `
    <div class="modal-backdrop-custom" onclick="closePrausnitzModal()" id="prausnitzModal">
      <div class="modal-content-custom" onclick="event.stopPropagation()" style="max-width: 700px;">
        <div class="panel-header mb-3">
          <div class="panel-title">
            <i class="bi bi-book"></i> Exemplos 
          </div>
        </div>
        
        <div class="text-muted-soft mb-3" style="font-size: 0.9rem;">
          Sistemas ternários validados experimentalmente com parâmetros da literatura.
        </div>
        
        <div style="display: grid; gap: 10px;">
  `;
  
  examples.forEach((ex, idx) => {
    html += `
        <div class="model-checkbox-card" onclick="loadPrausnitzExample(${idx})" style="cursor: pointer">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${ex.name}</strong><br>
                    <small class="text-muted-soft">${(ex.components_pt || ex.components).join(' / ')} • ${ex.model} • ${ex.temperature}°C</small><br>

            <small class="text-muted-soft" style="font-size: 0.75rem;">
              ${ex.reference}
            </small>
          </div>
          <i class="bi bi-arrow-right-circle" style="font-size: 1.5rem; color: #38bdf8;"></i>
        </div>
      </div>
    `;
  });
  
  html += `
        </div>
        
        <div class="d-flex justify-content-end mt-3">
          <button type="button" class="btn-sim btn-sim-ghost" onclick="closePrausnitzModal()">
            Fechar
          </button>
        </div>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', html);
}


function closePrausnitzModal() {
  const modal = document.getElementById('prausnitzModal');
  if (modal) modal.remove();
}


/**
 * Retorna exemplos validados do Prausnitz (Apêndice E)
 * 
 * FONTE:
 *   - Tabela E-5 (NRTL): 1 sistema @ 25°C
 *   - Tabela E-6 (UNIQUAC): 4 sistemas @ 25°C
 * 
 * VERSÃO 3.0 - Corrigida conforme Prausnitz p. 798
 * 
 * @returns {Array} Lista de exemplos validados
 */
/**
 * ============================================================================
 * EXEMPLOS DO PRAUSNITZ - VERSÃO PT-BR
 * ============================================================================
 * Retorna exemplos validados do Prausnitz (Apêndice E)
 * FONTE:
 * - Tabela E-5 (NRTL): 1 sistema 25°C
 * - Tabela E-6 (UNIQUAC): 4 sistemas 25°C
 * @returns {Array} Lista de exemplos validados
 */
function getPrausnitzExamples() {
    return [
        // ====================================================================
        // SISTEMA NRTL (Tabela E-5)
        // ====================================================================
        {
            name: 'Água / Tricloroetano / Acetona (NRTL)',
            components: ['Water', '1,1,2-Trichloroethane', 'Acetone'],
            components_pt: ['Água', '1,1,2-Tricloroetano', 'Acetona'],
            zfeed: [0.30, 0.40, 0.30],
            temperature: 25.0,
            model: 'NRTL',
            calcType: 'ell_flash',
            reference: 'Bender & Block (1975)',
            description: 'Sistema clássico água-solvente clorado-cosolvente. TCE imiscível com água, acetona distribui-se entre fases.',
            applications: 'Extração líquido-líquido, tratamento de efluentes'
        },
        
        // ====================================================================
        // SISTEMAS UNIQUAC (Tabela E-6)
        // ====================================================================
        {
            name: 'Furfural / Ciclo-hexano / Benzeno (UNIQUAC)',
            components: ['Furfural', 'Cyclohexane', 'Benzene'],
            components_pt: ['Furfural', 'Ciclo-hexano', 'Benzeno'],
            zfeed: [0.33, 0.33, 0.34],
            temperature: 25.0,
            model: 'UNIQUAC',
            calcType: 'ell_flash',
            reference: 'Anderson & Prausnitz (1978)',
            description: 'Separação aromático/alifático usando furfural como solvente polar seletivo.',
            applications: 'Refinaria de petróleo, separação de aromáticos'
        },
        
        {
            name: 'Sulfolano / n-Octano / Tolueno (UNIQUAC)',
            components: ['Sulfolane', 'n-Octane', 'Toluene'],
            components_pt: ['Sulfolano', 'n-Octano', 'Tolueno'],
            zfeed: [0.35, 0.30, 0.35],
            temperature: 25.0,
            model: 'UNIQUAC',
            calcType: 'ell_flash',
            reference: 'Anderson & Prausnitz (1978)',
            description: 'Processo industrial Sulfolane para extração de aromáticos de correntes parafínicas.',
            applications: 'Indústria petroquímica, purificação de BTX'
        },
        
        {
            name: '2,5-Hexanodiona / 1-Hexeno / n-Hexano (UNIQUAC)',
            components: ['2,5-Hexanedione', '1-Hexene', 'n-Hexane'],
            components_pt: ['2,5-Hexanodiona', '1-Hexeno', 'n-Hexano'],
            zfeed: [0.30, 0.35, 0.35],
            temperature: 25.0,
            model: 'UNIQUAC',
            calcType: 'ell_flash',
            reference: 'Anderson & Prausnitz (1978)',
            description: 'Forte imiscibilidade entre dicetona polar e hidrocarbonetos insaturados/saturados.',
            applications: 'Separação olefinas/parafinas, estudos de solubilidade'
        },
        
        {
            name: '1,4-Dioxano / n-Hexano / Metilciclopentano (UNIQUAC)',
            components: ['1,4-Dioxane', 'n-Hexane', 'Methylcyclopentane'],
            components_pt: ['1,4-Dioxano', 'n-Hexano', 'Metilciclopentano'],
            zfeed: [0.35, 0.32, 0.33],
            temperature: 25.0,
            model: 'UNIQUAC',
            calcType: 'ell_flash',
            reference: 'Anderson & Prausnitz (1978)',
            description: 'Sistema polar/apolar com éter cíclico e cicloparafinas. Demonstra capacidade do UNIQUAC.',
            applications: 'Separação de isômeros, extração com éteres'
        },
        
        // ====================================================================
        // DIAGRAMAS TERNÁRIOS COMPLETOS
        // ====================================================================
        {
            name: 'Água / Tricloroetano / Acetona - Diagrama Ternário (NRTL)',
            components: ['Water', '1,1,2-Trichloroethane', 'Acetone'],
            components_pt: ['Água', '1,1,2-Tricloroetano', 'Acetona'],
            temperature: 25.0,
            model: 'NRTL',
            calcType: 'ternary_diagram',
            ntielines: 5,
            reference: 'Bender & Block (1975)',
            description: 'Diagrama completo com curva binodal e tie-lines para sistema aquoso-orgânico.',
            applications: 'Visualização de regiões de imiscibilidade'
        },
        
        {
            name: 'Furfural / Ciclo-hexano / Benzeno - Diagrama Ternário (UNIQUAC)',
            components: ['Furfural', 'Cyclohexane', 'Benzene'],
            components_pt: ['Furfural', 'Ciclo-hexano', 'Benzeno'],
            temperature: 25.0,
            model: 'UNIQUAC',
            calcType: 'ternary_diagram',
            ntielines: 6,
            reference: 'Anderson & Prausnitz (1978)',
            description: 'Diagrama para processo de extração de aromáticos com furfural.',
            applications: 'Design de colunas de extração, otimização de processos'
        },
        
        // ====================================================================
        // ⭐ EXEMPLOS DE EXTRAÇÃO MULTI-ESTÁGIOS
        // ====================================================================
        {
            name: 'Extração de Acetona (30% em água)',
            components: ['Water', '1,1,2-Trichloroethane', 'Acetone'],
            components_pt: ['Água', '1,1,2-Tricloroetano', 'Acetona'],
            zfeed: [0.70, 0.00, 0.30],
            temperature: 25.0,
            model: 'NRTL',
            calcType: 'extraction',
            S_F_ratio: 2.0,
            target_recovery: 0.90,
            efficiency: 0.70,
            reference: 'Bender & Block (1975)',
            description: 'Extração de acetona de solução aquosa usando tricloroetano (TCE) como solvente. Sistema clássico com 2 fases: fase aquosa (rafinado) e fase orgânica (extrato rico em acetona).',
            applications: 'Recuperação de acetona, purificação de correntes aquosas'
        },

        {
            name: 'Extração de Acetona (12% em água)',
            components: ['Water', '1,1,2-Trichloroethane', 'Acetone'],
            components_pt: ['Água', '1,1,2-Tricloroetano', 'Acetona'],
            zfeed: [0.88, 0.00, 0.12],
            temperature: 25.0,
            model: 'NRTL',
            calcType: 'extraction',
            S_F_ratio: 1.5,
            target_recovery: 0.85,
            efficiency: 0.65,
            reference: 'Bender & Block (1975)',
            description: 'Extração de baixas concentrações de acetona de água. Demonstra que menor S/F requer mais estágios para mesma recuperação.',
            applications: 'Tratamento de efluentes, recuperação de traços de solventes'
        }
    ];
}



/**
 * Normalizar nomes de componentes para busca robusta
 * Remove TODOS os caracteres especiais, espaços, pontuação
 * 
 * @param {string} name - Nome do componente
 * @returns {string} Nome normalizado (apenas letras e números minúsculos)
 */
function normalizeComponentName(name) {
    return name.toLowerCase()
        .replace(/[^a-z0-9]/g, '')  // Remove TUDO exceto letras e números
        .trim();
}


/**
 * Aguarda até que um elemento exista no DOM
 * @param {string} selector - Seletor CSS do elemento (ex: '#temperature', '#z1')
 * @param {number} timeout - Tempo máximo de espera em ms (padrão: 3000)
 * @returns {Promise<Element|null>}
 */
function waitForElement(selector, timeout = 3000) {
    return new Promise((resolve) => {
        // Se já existe, retornar imediatamente
        const element = document.querySelector(selector);
        if (element) {
            resolve(element);
            return;
        }

        // Configurar observer para detectar mudanças no DOM
        const observer = new MutationObserver(() => {
            const element = document.querySelector(selector);
            if (element) {
                observer.disconnect();
                resolve(element);
            }
        });

        // Observar mudanças no container de campos dinâmicos
        const container = document.getElementById('dynamicFields');
        if (container) {
            observer.observe(container, {
                childList: true,
                subtree: true
            });
        } else {
            // Fallback: observar o body inteiro
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }

        // Timeout para evitar espera infinita
        setTimeout(() => {
            observer.disconnect();
            resolve(null);
        }, timeout);
    });
}


/**
 * Carrega um exemplo do Prausnitz na interface
 * 
 * MELHORIAS VERSÃO 4.0:
 *   - Busca case-insensitive robusta
 *   - Normalização de nomes (remove espaços, hífens, vírgulas)
 *   - Validação de todos os campos antes de preencher
 *   - ⭐ Suporte para extração multi-estágios (SEM solute_index)
 *   - Aguarda criação de campos dinâmicos
 * 
 * @param {number} index - Índice do exemplo na lista
 */
async function loadPrausnitzExample(index) {
    const examples = getPrausnitzExamples();
    const example = examples[index];
    
    if (!example) {
        showNotification('Exemplo não encontrado', 'error');
        return;
    }
    
    closePrausnitzModal();
    
    try {
        console.log('[ELL] ========================================');
        console.log('[ELL] 📚 Carregando exemplo:', example.name);
        console.log('[ELL] ========================================');
        
        // 1. Limpar seleção atual
        selectedComponents = [];
        
        // 2. Definir modelo ANTES de recarregar componentes
        const modelSelect = document.getElementById('model');
        if (modelSelect) {
            modelSelect.value = example.model;
            console.log('[ELL] ✅ Modelo definido:', example.model);
        }
        
        // 3. Recarregar componentes para o modelo correto
        await loadAllComponents();
        console.log('[ELL] ✅ Componentes recarregados:', allComponents.length, 'disponíveis');
        
        // 4. Selecionar componentes do exemplo com busca ROBUSTA
        for (const compName of example.components) {
            console.log(`[ELL] 🔍 Buscando: "${compName}"`);
            
            const normalizedSearch = normalizeComponentName(compName);
            
            const comp = allComponents.find(c => {
                // Busca 1: Nome exato
                if (c.name === compName || c.name_en === compName) {
                    console.log(`[ELL]   ✅ MATCH EXATO: ${c.name}`);
                    return true;
                }
                
                // Busca 2: Nome normalizado
                if (normalizeComponentName(c.name) === normalizedSearch ||
                    normalizeComponentName(c.name_en || '') === normalizedSearch) {
                    console.log(`[ELL]   ✅ MATCH NORMALIZADO: ${c.name}`);
                    return true;
                }
                
                // Busca 3: CAS exato
                if (c.cas === compName) {
                    console.log(`[ELL]   ✅ MATCH CAS: ${c.name} (${c.cas})`);
                    return true;
                }
                
                return false;
            });
            
            if (comp) {
                selectedComponents.push(comp);
                console.log(`[ELL] ✅ ${selectedComponents.length}/3 adicionado: ${comp.name}`);
            } else {
                console.error(`[ELL] ❌ NÃO ENCONTRADO: "${compName}"`);
                console.error(`[ELL]    Disponíveis: ${allComponents.map(c => c.name).join(', ')}`);
            }
        }
        
        // 5. Validar se encontrou todos os 3 componentes
        if (selectedComponents.length !== 3) {
            const missing = example.components.filter((name, idx) => 
                !selectedComponents[idx] || selectedComponents[idx].name !== name
            );
            
            showNotification(
                `❌ Erro: Apenas ${selectedComponents.length}/3 componentes encontrados.\n` +
                `Faltando: ${missing.join(', ')}\n\n` +
                `Modelo ${example.model} pode não ter esses componentes no banco de dados.`,
                'error'
            );
            selectedComponents = [];
            updateComponentTags();
            return;
        }
        
        updateComponentTags();
        console.log('[ELL] ✅ 3 componentes selecionados');
        
        // 6. Definir tipo de cálculo
        const calcTypeSelect = document.getElementById('calcType');
        if (calcTypeSelect) {
            calcTypeSelect.value = example.calcType;
            console.log('[ELL] ✅ Tipo de cálculo:', example.calcType);
        }
        
        // 7. Atualizar campos dinâmicos
        updateFields();
        console.log('[ELL] ✅ updateFields() chamado');
        
        // 8. AGUARDAR campo de temperatura
        console.log('[ELL] ⏳ Aguardando campo temperature...');
        const tempInput = await waitForElement('#temperature', 3000);
        
        if (!tempInput) {
            showNotification('❌ Erro: Campo de temperatura não foi criado', 'error');
            return;
        }
        
        console.log('[ELL] ✅ Campo temperature encontrado');
        
        // 9. Preencher temperatura
        tempInput.value = example.temperature.toFixed(1);
        console.log(`[ELL] ✅ Temperatura: ${example.temperature}°C`);
        
        const tempUnitSelect = document.getElementById('tempUnit');
        if (tempUnitSelect) {
            tempUnitSelect.value = 'C';
        }
        
        // ====================================================================
        // 10. PREENCHER CAMPOS ESPECÍFICOS POR TIPO DE CÁLCULO
        // ====================================================================
        
        if (example.calcType === 'ell_flash' && example.zfeed) {
            console.log('[ELL] ⏳ Preenchendo composições flash...');
            
            for (let i = 0; i < example.zfeed.length; i++) {
                const fieldId = `z${i+1}`;
                const el = await waitForElement(`#${fieldId}`, 3000);
                
                if (el) {
                    el.value = example.zfeed[i].toFixed(3);
                    console.log(`[ELL] ✅ z${i+1} = ${example.zfeed[i]}`);
                } else {
                    console.error(`[ELL] ❌ Campo z${i+1} não encontrado!`);
                }
            }
        }
        
        else if (example.calcType === 'ternary_diagram' && example.ntielines) {
            console.log('[ELL] ⏳ Preenchendo n_tie_lines...');
            
            const el = await waitForElement('#n_tie_lines', 3000);
            if (el) {
                el.value = example.ntielines;
                console.log(`[ELL] ✅ n_tie_lines = ${example.ntielines}`);
            } else {
                console.error('[ELL] ❌ Campo n_tie_lines não encontrado!');
            }
        }
        
        // ⭐ NOVO: PREENCHER CAMPOS DE EXTRAÇÃO MULTI-ESTÁGIOS
        else if (example.calcType === 'extraction') {
            console.log('[ELL] ⏳ Preenchendo campos de extração...');
            
            // Composições da alimentação (z_feed)
            if (example.zfeed) {
                for (let i = 0; i < example.zfeed.length; i++) {
                    const fieldId = `z${i+1}`;
                    const el = await waitForElement(`#${fieldId}`, 3000);
                    
                    if (el) {
                        el.value = example.zfeed[i].toFixed(3);
                        console.log(`[ELL] ✅ z${i+1} = ${example.zfeed[i]}`);
                    } else {
                        console.error(`[ELL] ❌ Campo z${i+1} não encontrado!`);
                    }
                }
            }
            
            // Razão S/F
            if (example.S_F_ratio !== undefined) {
                const el = await waitForElement('#S_F_ratio', 3000);
                if (el) {
                    el.value = example.S_F_ratio.toFixed(1);
                    console.log(`[ELL] ✅ S_F_ratio = ${example.S_F_ratio}`);
                }
            }
            
            // Eficiência
            if (example.efficiency !== undefined) {
                const el = await waitForElement('#efficiency', 3000);
                if (el) {
                    el.value = example.efficiency.toFixed(2);
                    console.log(`[ELL] ✅ efficiency = ${example.efficiency}`);
                }
            }
            
            // Modo de extração (recovery ou fixed)
            const mode = example.target_recovery !== undefined ? 'recovery' : 'fixed';
            const modeRadio = document.querySelector(`input[name="extraction_mode"][value="${mode}"]`);
            if (modeRadio) {
                modeRadio.checked = true;
                toggleExtractionMode();  // Atualizar campos dinâmicos
                console.log(`[ELL] ✅ Modo de extração: ${mode}`);
            }
            
            // Aguardar campos dinâmicos serem criados
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Recuperação alvo (se modo = recovery)
            if (example.target_recovery !== undefined) {
                const el = await waitForElement('#target_recovery', 3000);
                if (el) {
                    el.value = (example.target_recovery * 100).toFixed(1);
                    console.log(`[ELL] ✅ target_recovery = ${example.target_recovery * 100}%`);
                }
            }
            
            // Número de estágios (se modo = fixed)
            if (example.N_stages !== undefined) {
                const el = await waitForElement('#N_stages', 3000);
                if (el) {
                    el.value = example.N_stages;
                    console.log(`[ELL] ✅ N_stages = ${example.N_stages}`);
                }
            }
            
            // ⚠️ REMOVIDO: solute_index (agora é auto-detectado pelo backend)
            // Não há mais campo HTML para preencher
        }
        
        console.log('[ELL] ========================================');
        console.log('[ELL] ✅ EXEMPLO CARREGADO COM SUCESSO!');
        console.log('[ELL] ========================================');
        
        // Mostrar informações do exemplo
        showNotification(
            `✅ Exemplo carregado: ${example.name}\n\n` +
            `📚 ${example.reference}\n\n` +
            `${example.description}`,
            'success'
        );
        
    } catch (error) {
        console.error('[ELL] ❌ ERRO ao carregar exemplo:', error);
        console.error(error.stack);
        showNotification('❌ Erro ao carregar exemplo: ' + error.message, 'error');
    }
}

/**
 * ===============================================
 * CARREGAMENTO DE PRESET DE CASO DE ESTUDO
 * ===============================================
 * Carrega automaticamente um caso de estudo do módulo educacional
 * Similar a loadPrausnitzExample(), mas recebe dados de window.presetData
 */
async function loadPreset() {
    if (!window.presetData) {
        console.log('[ELL] Nenhum preset detectado');
        return;
    }
    
    const preset = window.presetData;
    console.log('═'.repeat(70));
    console.log('[ELL] 📚 CARREGANDO PRESET DE CASO DE ESTUDO');
    console.log('[ELL] Título:', preset.title);
    console.log('[ELL] ID:', preset.id);
    console.log('═'.repeat(70));
    
    try {
        // 1. Limpar seleção atual
        selectedComponents = [];
        
        // 2. Definir modelo ANTES de recarregar componentes
        const modelSelect = document.getElementById('model');
        if (modelSelect && preset.model) {
            modelSelect.value = preset.model;
            console.log('[ELL] ✅ Modelo definido:', preset.model);
        }
        
        // 3. Recarregar componentes para o modelo correto
        await loadAllComponents();
        console.log('[ELL] ✅ Componentes recarregados:', allComponents.length, 'disponíveis');
        
        // 4. Selecionar componentes do preset com busca ROBUSTA
        for (const compName of preset.components) {
            console.log('[ELL] 🔍 Buscando:', compName);
            
            const normalizedSearch = normalizeComponentName(compName);
            const comp = allComponents.find(c => {
                // Busca 1: Nome exato
                if (c.name === compName || c.name_en === compName) {
                    console.log('[ELL] ✅ MATCH EXATO:', c.name);
                    return true;
                }
                // Busca 2: Nome normalizado
                if (normalizeComponentName(c.name) === normalizedSearch || 
                    normalizeComponentName(c.name_en) === normalizedSearch) {
                    console.log('[ELL] ✅ MATCH NORMALIZADO:', c.name);
                    return true;
                }
                // Busca 3: CAS exato
                if (c.cas === compName) {
                    console.log('[ELL] ✅ MATCH CAS:', c.name, c.cas);
                    return true;
                }
                return false;
            });
            
            if (comp) {
                selectedComponents.push(comp);
                console.log('[ELL] ✅', selectedComponents.length + '/3 adicionado:', comp.name);
            } else {
                console.error('[ELL] ❌ NÃO ENCONTRADO:', compName);
                console.error('[ELL] Disponíveis:', allComponents.map(c => c.name).join(', '));
            }
        }
        
        // 5. Validar se encontrou todos os 3 componentes
        if (selectedComponents.length !== 3) {
            const missing = preset.components.filter((name, idx) => 
                !selectedComponents[idx] || selectedComponents[idx].name !== name
            );
            showNotification(
                `Erro: Apenas ${selectedComponents.length}/3 componentes encontrados. Faltando: ${missing.join(', ')}. Modelo ${preset.model} pode não ter esses componentes no banco de dados.`,
                'error'
            );
            selectedComponents = [];
            updateComponentTags();
            return;
        }
        
        updateComponentTags();
        console.log('[ELL] ✅ 3 componentes selecionados');
        
        // 6. Definir tipo de cálculo
        const calcTypeSelect = document.getElementById('calcType');
        if (calcTypeSelect && preset.calc_type) {
            calcTypeSelect.value = preset.calc_type;
            console.log('[ELL] ✅ Tipo de cálculo:', preset.calc_type);
        }
        
        // 7. Atualizar campos dinâmicos
        updateFields();
        console.log('[ELL] ✅ updateFields() chamado');
        
        // 8. AGUARDAR campo de temperatura
        console.log('[ELL] ⏳ Aguardando campo temperature...');
        const tempInput = await waitForElement('temperature', 3000);
        if (!tempInput) {
            showNotification('Erro: Campo de temperatura não foi criado', 'error');
            return;
        }
        console.log('[ELL] ✅ Campo temperature encontrado');
        
        // 9. Preencher temperatura
        if (preset.temperature !== undefined) {
            tempInput.value = preset.temperature.toFixed(1);
            console.log('[ELL] ✅ Temperatura:', preset.temperature + '°C');
            
            const tempUnitSelect = document.getElementById('tempUnit');
            if (tempUnitSelect && preset.temperature_unit) {
                tempUnitSelect.value = preset.temperature_unit;
            }
        }
        
        // 10. PREENCHER CAMPOS ESPECÍFICOS POR TIPO DE CÁLCULO
        if (preset.calc_type === 'ternary_diagram' && preset.ntielines) {
            console.log('[ELL] ⏳ Preenchendo ntielines...');
            const el = await waitForElement('ntielines', 3000);
            if (el) {
                el.value = preset.ntielines;
                console.log('[ELL] ✅ ntielines:', preset.ntielines);
            } else {
                console.error('[ELL] ❌ Campo ntielines não encontrado!');
            }
        }
        
        // 11. Exibir banner informativo
        showPresetBanner(preset);
        
        console.log('═'.repeat(70));
        console.log('[ELL] ✅ PRESET CARREGADO COM SUCESSO!');
        console.log('═'.repeat(70));
        
        showNotification(`📚 Caso de estudo carregado: ${preset.title}`, 'success');
        
    } catch (error) {
        console.error('[ELL] ❌ ERRO ao carregar preset:', error);
        console.error(error.stack);
        showNotification(`Erro ao carregar preset: ${error.message}`, 'error');
    }
}

/**
 * Exibe banner informativo sobre o caso de estudo carregado
 */
function showPresetBanner(preset) {
    // Remove banner anterior se existir
    const existingBanner = document.getElementById('preset-banner');
    if (existingBanner) existingBanner.remove();
    
    const banner = document.createElement('div');
    banner.id = 'preset-banner';
    banner.className = 'alert alert-info alert-dismissible fade show';
    banner.style.cssText = `
        margin: 1rem 0;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(56, 189, 248, 0.1));
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-left: 4px solid #2563eb;
    `;
    
    banner.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="bi bi-book" style="font-size: 1.5rem; color: #2563eb;"></i>
            <div style="flex: 1;">
                <strong>📚 Caso de Estudo Validado:</strong> ${escapeHtml(preset.title)}<br>
                <small class="text-muted">
                    <i class="bi bi-check-circle"></i> Componentes: ${preset.components.join(' + ')} | 
                    <i class="bi bi-diagram-3"></i> Modelo: ${preset.model} | 
                    <i class="bi bi-thermometer-half"></i> ${preset.temperature}°C
                </small>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.calc-section') || document.querySelector('.container');
    if (container) {
        container.insertBefore(banner, container.firstChild);
    }
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
  const components = selectedComponents.map(c => c.name_en || c.name).join(' · ');
  const ranges = aiSuggestion.recommended_ranges || {};
  const T = ranges.temperature_C || {};
  const modelsForComps = aiSuggestion.recommended_models_for_components || [];
  const bestForModel = aiSuggestion.best_components_for_model || [];
  const detailText = aiSuggestion.details && aiSuggestion.details.reason
    ? aiSuggestion.details.reason
    : '';
  const tableRef = aiSuggestion.details && aiSuggestion.details.table_reference;
  const notes = aiSuggestion.details && aiSuggestion.details.notes;

  let html = `
    <div class="results-card">
      <div class="section-title-sm">
        <i class="bi bi-stars"></i> Recomendações da IA para este sistema ELL
      </div>

      <p class="text-muted-soft mb-2" style="font-size:0.85rem;">
        Sistema: <strong>${escapeHtml(components)}</strong><br>
        Tipo de cálculo: <strong>${escapeHtml(calcType)}</strong>
      </p>

      <div class="mb-2">
        <strong>Modelo recomendado principal:</strong>
        <span class="badge bg-info text-dark ms-1">
          ${escapeHtml(aiSuggestion.recommended_model)}
        </span>
      </div>
  `;

  if (modelsForComps.length) {
    html += `
      <div class="mb-2">
        <strong>Modelos adequados para estes componentes:</strong>
        <span class="text-muted-soft">
          ${modelsForComps.map(m => escapeHtml(m)).join(' · ')}
        </span>
      </div>
    `;
  }

  if (bestForModel.length) {
    html += `
      <div class="mb-2">
        <strong>Sistemas típicos para cada modelo:</strong>
        <ul class="text-muted-soft" style="font-size:0.82rem; margin-bottom:0;">
          ${bestForModel.map(
            item =>
              `<li><strong>${escapeHtml(item.model)}:</strong> ${escapeHtml(
                item.examples.join(', ')
              )}<br><em>${escapeHtml(item.notes || '')}</em></li>`
          ).join('')}
        </ul>
      </div>
    `;
  }

  if (T.min !== undefined) {
    html += `
      <div class="mb-2">
        <strong>Faixa recomendada de temperatura:</strong>
        <div class="text-muted-soft" style="font-size:0.82rem;">
          ${T.min.toFixed(1)} – ${T.max.toFixed(1)} °C
        </div>
      </div>
    `;
  }

  if (tableRef) {
    html += `
      <div class="mb-2">
        <strong>Referência:</strong>
        <span class="text-muted-soft" style="font-size:0.82rem;">
          Tabela ${escapeHtml(tableRef)} do Prausnitz et al. 
        </span>
      </div>
    `;
  }

  if (detailText) {
    html += `
      <div class="mb-2">
        <strong>Justificativa:</strong>
        <span class="text-muted-soft" style="font-size:0.82rem;">
          ${escapeHtml(detailText)}
        </span>
      </div>
    `;
  }

  if (notes) {
    html += `
      <div class="mb-2">
        <strong>Notas técnicas:</strong>
        <span class="text-muted-soft" style="font-size:0.82rem;">
          ${escapeHtml(notes)}
        </span>
      </div>
    `;
  }

  if (aiSuggestion.prefill) {
    html += `
      <div class="mt-3 d-flex gap-2">
        <button type="button" class="btn-sim btn-sim-primary btn-sm"
                onclick="applyAIParameters()">
          <i class="bi bi-magic"></i> Usar estes parâmetros
        </button>
      </div>
    `;
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

  if (Array.isArray(pre.z_feed) && pre.z_feed.length === 3) {
    for (let i = 0; i < 3; i++) {
      const el = document.getElementById('z' + (i + 1));
      if (el) el.value = pre.z_feed[i].toFixed(3);
    }
  }

  showNotification('Parâmetros recomendados aplicados ao formulário.', 'info');
}


// ============================================================================
// COMPARAÇÃO DE MODELOS
// ============================================================================


function showCompareModal() {
  if (selectedComponents.length !== 3) {
    alert('Selecione exatamente 3 componentes antes de comparar modelos.');
    return;
  }

  if (!lastFlashResults && !lastDiagramData) {
    alert('Faça primeiro um cálculo (flash ou diagrama) para comparar modelos.');
    return;
  }

  document.getElementById('compareModal').style.display = 'block';
}


function closeCompareModal() {
  document.getElementById('compareModal').style.display = 'none';
}


async function executeComparison() {
  closeCompareModal();

  const components = selectedComponents.map(c => c.name_en || c.name);
  const temperature = parseFloat(document.getElementById('temperature').value);
  const tempUnit = document.getElementById('tempUnit').value;
  const calcType = document.getElementById('calcType').value;

  let payload = {
    components,
    temperature,
    temperature_unit: tempUnit,
    calculation_type: 'flash'
  };

  if (calcType === 'ell_flash') {
    const z_feed = [];
    for (let i = 0; i < 3; i++) {
      const el = document.getElementById('z' + (i + 1));
      z_feed.push(parseFloat(el.value));
    }
    payload.z_feed = z_feed;
  }

  try {
    const res = await fetch('/ell/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      displayComparison(data.results);
    } else {
      alert('Erro na comparação: ' + (data.error || ''));
    }
  } catch (err) {
    alert('Erro na comparação: ' + err.message);
    console.error(err);
  }
}


function displayComparison(results) {
  const container = document.getElementById('comparison-diagram-container');
  if (!container) return;

  let html = '<div class="results-card">';
  html += '<h4 class="mb-3"><i class="bi bi-bar-chart"></i> Comparação de Modelos</h4>';

  ['NRTL', 'UNIQUAC'].forEach(modelName => {
    const res = results[modelName];

    if (res.error) {
      html += `
        <div class="alert alert-warning mb-3">
          Modelo <strong>${modelName}</strong>: ${escapeHtml(res.error)}
        </div>
      `;
      return;
    }

    html += `
      <div class="mt-3 mb-4 p-3" style="border-radius:8px;border:1px solid rgba(148,163,184,0.4);">
        <h6 class="mb-2"><i class="bi bi-diagram-3"></i> Modelo <strong>${modelName}</strong></h6>
        <div class="row g-3">
          <div class="col-md-6">
            <h6 class="section-title-sm">Frações de Fase</h6>
            <div class="results-grid">
              <div class="result-item">
                <span class="label">β (Fração L2)</span>
                <span class="value">${res.beta.toFixed(4)}</span>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <h6 class="section-title-sm">Composição L1</h6>
            <div class="results-grid">
    `;

    res.x_L1.forEach((x, i) => {
      html += `
        <div class="result-item">
          <span class="label">x<sub>L1,${i+1}</sub></span>
          <span class="value">${x.toFixed(4)}</span>
        </div>
      `;
    });

    html += `
            </div>
          </div>
        </div>
      </div>
    `;
  });

  html += '</div>';
  const compContent = document.getElementById('comparison-content');
  if (compContent) {
    compContent.innerHTML = html;
  }
  container.style.display = 'block';
}


// ============================================================================
// EXPORTAÇÃO
// ============================================================================

/**
 * Exporta resultados de ponto para CSV
 */
document.getElementById('export-csv-points-btn')?.addEventListener('click', function() {
  exportPointsCSV();
});

/**
 * Exporta resultados de ponto para PDF
 */
document.getElementById('export-pdf-points-btn')?.addEventListener('click', function() {
  if (!window.lastPointResults) {
    alert('Nenhum resultado disponível para exportar.');
    return;
  }

  const components = selectedComponents.map(c => c.name_en || c.name);
  let diagramType = 'flash';
  if (lastDiagramType === 'extraction') {
    diagramType = 'extraction';
  }

  console.log('[ELL] Exportando PDF de ponto:', diagramType);

  fetch('/ell/export/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      diagram_type: diagramType,
      components: components,
      model: lastModel,
      temperature: lastTemperature,
      results: window.lastPointResults,
      include_equations: true,
      include_methodology: true
    })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ell_${diagramType}_${lastModel}_${lastTemperature}C_${new Date().toISOString().slice(0,10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      console.log('[ELL] ✅ PDF de ponto exportado com sucesso');
    })
    .catch(err => {
      console.error('[ELL] ❌ Erro ao exportar PDF de ponto:', err);
      alert('Erro ao exportar PDF: ' + err.message);
    });
});

/**
 * Exporta diagrama ternário para CSV
 */
document.getElementById('export-csv-btn')?.addEventListener('click', function() {
  exportDiagramCSV();
});

/**
 * Exporta diagrama ternário para PDF
 * ✅ IMPLEMENTAÇÃO COMPLETA
 */
document.getElementById('export-pdf-btn')?.addEventListener('click', function() {
  if (!lastDiagramData || !lastDiagramData.results) {
    alert('Nenhum diagrama ternário disponível para exportar.');
    return;
  }

  const components = selectedComponents.map(c => c.name_en || c.name);
  
  console.log('[ELL] Exportando diagrama ternário para PDF...');
  console.log('[ELL] Componentes:', components);
  console.log('[ELL] Modelo:', lastModel);
  console.log('[ELL] Temperatura:', lastTemperature);

  fetch('/ell/export/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      diagram_type: 'ternary',
      components: components,
      model: lastModel,
      temperature: lastTemperature,
      results: lastDiagramData.results,
      include_equations: true,
      include_methodology: true
    })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const timestamp = new Date().toISOString().slice(0,10).replace(/-/g, '');
      a.download = `ell_ternary_${lastModel}_${lastTemperature}C_${timestamp}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      console.log('[ELL] ✅ PDF do diagrama ternário exportado com sucesso');
    })
    .catch(err => {
      console.error('[ELL] ❌ Erro ao exportar PDF do diagrama:', err);
      alert('Erro ao exportar PDF do diagrama ternário: ' + err.message);
    });
});

/**
 * Exporta diagrama ternário como imagem PNG
 */
document.getElementById('download-img-btn')?.addEventListener('click', function() {
  if (!currentDiagram) {
    alert('Nenhum diagrama ternário disponível para exportar.');
    return;
  }

  console.log('[ELL] Exportando diagrama como imagem PNG...');

  Plotly.downloadImage('ternaryDiagram', {
    format: 'png',
    width: 1200,
    height: 1200,
    filename: `ell_ternary_${lastModel}_${lastTemperature}C`
  }).then(() => {
    console.log('[ELL] ✅ Imagem PNG exportada com sucesso');
  }).catch(err => {
    console.error('[ELL] ❌ Erro ao exportar imagem:', err);
    alert('Erro ao exportar imagem: ' + err.message);
  });
});

// ============================================================================
// FUNÇÕES AUXILIARES DE EXPORTAÇÃO
// ============================================================================

/**
 * Exporta resultados de ponto para CSV
 */
function exportPointsCSV() {
  if (!window.lastPointResults) {
    alert('Nenhum resultado disponível para exportar.');
    return;
  }

  const components = selectedComponents.map(c => c.name_en || c.name);
  
  // Determinar tipo de diagrama
  let diagramType = 'flash';
  if (lastDiagramType === 'extraction') {
    diagramType = 'extraction';
  }

  console.log('[ELL] Exportando CSV de ponto:', diagramType);

  fetch('/ell/export/csv', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      diagram_type: diagramType,
      components: components,
      model: lastModel,
      temperature: lastTemperature,
      data: window.lastPointResults
    })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ell_${diagramType}_${lastModel}_${lastTemperature}C.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      console.log('[ELL] ✅ CSV de ponto exportado com sucesso');
    })
    .catch(err => {
      console.error('[ELL] ❌ Erro ao exportar CSV de ponto:', err);
      alert('Erro ao exportar CSV: ' + err.message);
    });
}

/**
 * Exporta diagrama ternário para CSV
 */
function exportDiagramCSV() {
  if (!lastDiagramData) {
    alert('Nenhum diagrama disponível para exportar.');
    return;
  }

  const components = selectedComponents.map(c => c.name_en || c.name);

  console.log('[ELL] Exportando diagrama ternário para CSV...');

  fetch('/ell/export/csv', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      diagram_type: 'ternary',
      components: components,
      model: lastModel,
      temperature: lastTemperature,
      data: lastDiagramData
    })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ell_ternary_${lastModel}_${lastTemperature}C.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      console.log('[ELL] ✅ CSV do diagrama exportado com sucesso');
    })
    .catch(err => {
      console.error('[ELL] ❌ Erro ao exportar CSV do diagrama:', err);
      alert('Erro ao exportar CSV: ' + err.message);
    });
}

/**
 * Exporta diagrama ternário como imagem PNG (via Plotly)
 */
function exportDiagramImage() {
  if (!currentDiagram) {
    alert('Nenhum diagrama ternário disponível para exportar.');
    return;
  }

  console.log('[ELL] Exportando imagem do diagrama...');

  Plotly.downloadImage('ternaryDiagram', {
    format: 'png',
    width: 1200,
    height: 1200,
    filename: `ell_ternary_${lastModel}_${lastTemperature}C`
  }).then(() => {
    console.log('[ELL] ✅ Imagem exportada com sucesso');
  }).catch(err => {
    console.error('[ELL] ❌ Erro ao exportar imagem:', err);
    alert('Erro ao exportar imagem: ' + err.message);
  });
}



// ============================================================================
// UTILITÁRIOS
// ============================================================================


function clearForm() {
  selectedComponents = [];
  updateComponentTags();
  updateFields();
  document.getElementById('results').innerHTML = `
    <div class="panel h-100 d-flex flex-column justify-content-center align-items-center">
      <div class="text-muted-soft mb-2">
        <i class="bi bi-graph-up"></i> Nenhum resultado ainda.
      </div>
      <div class="text-muted-soft" style="font-size: 0.85rem;">
        Configure o cálculo à esquerda e clique em <strong>Calcular</strong> para visualizar resultados numéricos ou diagramas.
      </div>
    </div>
  `;
  document.getElementById('ai-recommendation').innerHTML = '';

  const btnPts = document.getElementById('export-buttons-points');
  const btnDiag = document.getElementById('export-buttons');
  if (btnPts) btnPts.style.display = 'none';
  if (btnDiag) btnDiag.style.display = 'none';

  lastFlashResults = null;
  lastDiagramData = null;
  window.lastAiSuggestion = null;
  window.lastPointResults = null;

  const compContainer = document.getElementById('comparison-diagram-container');
  if (compContainer) compContainer.style.display = 'none';
}


function escapeHtml(text) {
  if (text === null || text === undefined) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}


function showNotification(message, type) {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.top = '20px';
  alertDiv.style.right = '20px';
  alertDiv.style.zIndex = 9999;
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  document.body.appendChild(alertDiv);
  setTimeout(() => alertDiv.remove(), 5000);
}

// ============================================================================
// ⭐ NOVO: RECARREGAR COMPONENTES AO MUDAR TIPO DE CÁLCULO
// ============================================================================

document.getElementById('calcType')?.addEventListener('change', async function () {
  console.log('[ELL] 🔄 Tipo de cálculo mudou, recarregando componentes...');
  
  // Recarregar componentes (filtra se for extração)
  await loadAllComponents();
  
  // Remover componentes que não estão mais disponíveis
  const validNames = new Set(allComponents.map(c => c.name_en || c.name));
  const removedComponents = selectedComponents.filter(
    c => !validNames.has(c.name_en || c.name)
  );
  
  if (removedComponents.length > 0) {
    console.log('[ELL] ⚠️ Componentes removidos:', removedComponents.map(c => c.name));
    selectedComponents = selectedComponents.filter(
      c => validNames.has(c.name_en || c.name)
    );
    updateComponentTags();
    
    showNotification(
      `⚠️ ${removedComponents.length} componente(s) removido(s) pois não têm parâmetros para este tipo de cálculo.`,
      'warning'
    );
  }
  
  // Atualizar campos dinâmicos
  updateFields();
});

// Recarregar componentes ao mudar modelo (JÁ EXISTENTE - DEIXAR COMO ESTÁ)


// Recarregar componentes ao mudar modelo
document.getElementById('model')?.addEventListener('change', async function () {
  await loadAllComponents();  // ✅ Já recarrega
  
  const validNames = new Set(allComponents.map(c => c.name_en || c.name));
  selectedComponents = selectedComponents.filter(
    c => validNames.has(c.name_en || c.name)
  );
  updateComponentTags();
  updateModelInfoPanel();
});

// Fechar modal ao clicar ESC
document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
    closeCompareModal();
    closeComponentModal();
    closePrausnitzModal();
  }
});