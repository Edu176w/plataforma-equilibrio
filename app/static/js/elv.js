// VARIÁVEIS GLOBAIS
let selectedComponents = [];
let allComponents = [];
let currentChart = null;

// NOVAS VARIÁVEIS PARA EXPORTAÇÃO
let lastDiagramData = null;      // dados do último diagrama (pxy ou txy)
let lastDiagramType = null;      // 'pxy' ou 'txy'
let lastModel = null;
let lastPressure = null;         // kPa
let lastTemperature = null;      // °C

// RESULTADOS PONTUAIS
window.lastPointResults = null;

// SUGESTÃO DE IA
window.lastAiSuggestion = null;

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', async function () {
  await loadAllComponents();
  loadComponentsFromURL();
  updateFields();
  initializeTooltips();
  updateDiagramOptions();

  const btnDiag = document.getElementById('export-buttons');
  const btnPts = document.getElementById('export-buttons-points');
  if (btnDiag) btnDiag.style.display = 'none';
  if (btnPts) btnPts.style.display = 'none';
});

// ==================== CARREGAMENTO DE COMPONENTES ====================

async function loadAllComponents() {
  try {
    const response = await fetch('/api/components/list');
    const data = await response.json();
    if (data.success) {
      allComponents = data.components;
    }
  } catch (err) {
    console.error('Erro ao carregar componentes:', err);
  }
}

function loadComponentsFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  for (let i = 1; i <= 4; i++) {
    const comp = urlParams.get('comp' + i);
    if (comp) {
      const c = allComponents.find(
        x => x.name_en === comp || x.name === comp
      );
      if (c && selectedComponents.length < 4) {
        selectedComponents.push(c);
      }
    }
  }
  updateComponentTags();
  updateDiagramOptions();
}

// ==================== GERENCIAMENTO DE COMPONENTES ====================

function updateComponentTags() {
  const container = document.getElementById('selectedComponentsTags');
  const countSpan = document.getElementById('componentCount');
  if (!container) return;

  let html = '';
  selectedComponents.forEach((comp, i) => {
    html += `
      <span class="component-tag">
        ${escapeHtml(comp.name)}
        <i class="bi bi-x-circle" onclick="removeComponent(${i})"></i>
      </span>
    `;
  });

  if (selectedComponents.length < 4) {
    html += `
      <button class="add-component-btn" type="button" onclick="showComponentModal()">
        <i class="bi bi-plus-circle"></i> Adicionar componente
      </button>
    `;
  }

  container.innerHTML = html;
  if (countSpan) countSpan.textContent = selectedComponents.length;
  updateDiagramOptions();
}

function removeComponent(index) {
  selectedComponents.splice(index, 1);
  updateComponentTags();
  updateFields();
}

function showComponentModal() {
  if (selectedComponents.length >= 4) {
    alert('Máximo de 4 componentes atingido.');
    return;
  }
  document.getElementById('componentModal').style.display = 'block';
  renderComponentList('');
}

function closeComponentModal() {
  document.getElementById('componentModal').style.display = 'none';
}

function renderComponentList(filter) {
  const listDiv = document.getElementById('componentList');
  const term = (filter || '').toLowerCase();
  let filtered = allComponents;

  if (term) {
    filtered = allComponents.filter(c =>
      c.name.toLowerCase().includes(term) ||
      (c.name_en && c.name_en.toLowerCase().includes(term)) ||
      (c.formula && c.formula.toLowerCase().includes(term)) ||
      (c.cas && c.cas.toLowerCase().includes(term))
    );
  }

  let html = '<ul class="list-group list-group-flush">';
  filtered.forEach((comp, idx) => {
    html += `
      <li class="list-group-item" style="cursor:pointer"
          onclick="selectComponent(${idx}, '${term.replace(/'/g, '')}')">
        <div>
          <strong>${escapeHtml(comp.name)}</strong><br>
          <small class="text-muted-soft">
            ${escapeHtml(comp.name_en || '')} · ${escapeHtml(comp.formula || '')} · ${escapeHtml(comp.cas || '')}
          </small>
        </div>
      </li>
    `;
  });
  html += '</ul>';
  listDiv.innerHTML = html;
}

function selectComponent(indexInFiltered, term) {
  let filtered = allComponents;
  if (term) {
    const t = term.toLowerCase();
    filtered = allComponents.filter(c =>
      c.name.toLowerCase().includes(t) ||
      (c.name_en && c.name_en.toLowerCase().includes(t)) ||
      (c.formula && c.formula.toLowerCase().includes(t)) ||
      (c.cas && c.cas.toLowerCase().includes(t))
    );
  }

  const comp = filtered[indexInFiltered];
  if (!comp) return;

  if (selectedComponents.length >= 4) {
    alert('Máximo de 4 componentes atingido.');
    return;
  }

  if (!selectedComponents.find(c => c.cas === comp.cas)) {
    selectedComponents.push(comp);
  }

  updateComponentTags();
  updateFields();
  closeComponentModal();
}

// ==================== CAMPOS DINÂMICOS / TIPOS DE CÁLCULO ====================

function updateFields() {
  const calcType = document.getElementById('calcType').value;
  const container = document.getElementById('dynamicFields');
  if (!container) return;

  let html = '';

  if (calcType === 'bubble' || calcType === 'dew' || calcType === 'pxy') {
    html += `
      <div class="row mb-3">
        <div class="col-md-6">
          <label class="form-label">Temperatura</label>
          <div class="input-group-compact">
            <input type="number" class="form-control" id="temperature" value="80" step="0.1">
            <select class="form-select" id="tempUnit">
              <option value="C">°C</option>
              <option value="K">K</option>
            </select>
          </div>
        </div>
      </div>
    `;
  }

  if (calcType === 'bubble_t' || calcType === 'dew_t' || calcType === 'txy') {
    html += `
      <div class="row mb-3">
        <div class="col-md-6">
          <label class="form-label">Pressão</label>
          <div class="input-group-compact">
            <input type="number" class="form-control" id="pressure" value="101.325" step="0.1">
            <select class="form-select" id="pressUnit">
              <option value="kPa">kPa</option>
              <option value="Pa">Pa</option>
              <option value="bar">bar</option>
              <option value="atm">atm</option>
            </select>
          </div>
        </div>
      </div>
    `;
  }

  if (calcType === 'flash') {
    html += `
      <div class="row mb-3">
        <div class="col-md-6">
          <label class="form-label">Temperatura</label>
          <div class="input-group-compact">
            <input type="number" class="form-control" id="temperature" value="80" step="0.1">
            <select class="form-select" id="tempUnit">
              <option value="C">°C</option>
              <option value="K">K</option>
            </select>
          </div>
        </div>
        <div class="col-md-6">
          <label class="form-label">Pressão</label>
          <div class="input-group-compact">
            <input type="number" class="form-control" id="pressure" value="101.325" step="0.1">
            <select class="form-select" id="pressUnit">
              <option value="kPa">kPa</option>
              <option value="Pa">Pa</option>
              <option value="bar">bar</option>
              <option value="atm">atm</option>
            </select>
          </div>
        </div>
      </div>
    `;
  }

  if (calcType !== 'pxy' && calcType !== 'txy') {
    html += `
      <div class="row mb-3">
        <div class="col-12">
          <label class="form-label">Frações molares na fase líquida</label>
          <div class="row">
    `;

    const n = Math.max(1, selectedComponents.length);
    selectedComponents.forEach((comp, i) => {
      html += `
        <div class="col-md-3 mb-2">
          <div class="input-group input-group-sm">
            <span class="input-group-text">x${i + 1}</span>
            <input type="number" class="form-control" id="x${i + 1}"
                   value="${(1 / n).toFixed(3)}" step="0.001">
          </div>
          <small class="text-muted-soft">${escapeHtml(comp.name_en || comp.name)}</small>
        </div>
      `;
    });

    html += `
          </div>
          <small class="text-muted-soft">
            A soma das frações deve ser 1,0.
          </small>
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

function updateDiagramOptions() {
  const calcType = document.getElementById('calcType');
  if (!calcType) return;

  const pxyOption = calcType.querySelector('option[value="pxy"]');
  const txyOption = calcType.querySelector('option[value="txy"]');

  if (!pxyOption || !txyOption) return;

  if (selectedComponents.length === 2) {
    pxyOption.disabled = false;
    txyOption.disabled = false;
  } else {
    pxyOption.disabled = true;
    txyOption.disabled = true;
    if (calcType.value === 'pxy' || calcType.value === 'txy') {
      calcType.value = 'bubble';
      updateFields();
    }
  }
}

// ==================== CÁLCULO PRINCIPAL ====================

async function calculate() {
  if (selectedComponents.length < 2) {
    alert('Selecione pelo menos 2 componentes.');
    return;
  }

  const calcType = document.getElementById('calcType').value;
  const model = document.getElementById('model').value;

  if (calcType === 'pxy' || calcType === 'txy') {
    await generateDiagram(calcType, model);
  } else {
    await calculatePoint(calcType, model);
  }
}

// CORREÇÃO na função calculatePoint
async function calculatePoint(calcType, model) {
  clearComparison();
  const components = selectedComponents.map(c => c.name_en || c.name);
  const payload = { components, model };

  if (calcType === 'bubble' || calcType === 'dew') {
    payload.temperature = parseFloat(document.getElementById('temperature').value);
    payload.temperature_unit = document.getElementById('tempUnit').value;
  } else if (calcType === 'bubble_t' || calcType === 'dew_t') {
    payload.pressure = parseFloat(document.getElementById('pressure').value);
    payload.pressure_unit = document.getElementById('pressUnit').value;
  } else if (calcType === 'flash') {
    payload.temperature = parseFloat(document.getElementById('temperature').value);
    payload.temperature_unit = document.getElementById('tempUnit').value;
    payload.pressure = parseFloat(document.getElementById('pressure').value);
    payload.pressure_unit = document.getElementById('pressUnit').value;
  }

  const compositions = [];
  for (let i = 0; i < selectedComponents.length; i++) {
    const el = document.getElementById('x' + (i + 1));
    const val = parseFloat(el ? el.value : NaN);
    compositions.push(isNaN(val) ? 0 : val);
  }
  const sumX = compositions.reduce((a, b) => a + b, 0);
  if (sumX < 0.999 || sumX > 1.001) {
    alert('A soma das frações molares na fase líquida deve ser igual a 1,0.');
    return;
  }
  payload.compositions = compositions;

  let endpoint;
  if (calcType === 'bubble') endpoint = '/elv/calculate/bubble';
  else if (calcType === 'bubble_t') endpoint = '/elv/calculate/bubble_t';
  else if (calcType === 'dew') endpoint = '/elv/calculate/dew';
  else if (calcType === 'dew_t') endpoint = '/elv/calculate/dew_t';
  else if (calcType === 'flash') endpoint = '/elv/calculate/flash';

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

      // CORREÇÃO: Limpa dados de diagrama ao fazer cálculo pontual
      lastDiagramData = null;
      lastDiagramType = null;
      lastModel = null;
      lastPressure = null;
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
    } else {
      alert('Erro no cálculo: ' + (data.error || ''));
    }
  } catch (err) {
    alert('Erro no cálculo: ' + err.message);
    console.error(err);
  }
}

// ==================== DIAGRAMAS P-xy / T-xy ====================

// CORREÇÃO na função generateDiagram
async function generateDiagram(calcType, model) {
  clearComparison();
  const components = selectedComponents.map(c => c.name_en || c.name);
  const payload = { components, model };

  if (calcType === 'pxy') {
    payload.temperature = parseFloat(document.getElementById('temperature').value);
    payload.temperature_unit = document.getElementById('tempUnit').value;
  } else {
    payload.pressure = parseFloat(document.getElementById('pressure').value);
    payload.pressure_unit = document.getElementById('pressUnit').value;
  }

  const endpoint = calcType === 'pxy'
    ? '/elv/diagram/pxy'
    : '/elv/diagram/txy';

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

      // CORREÇÃO: Limpa dados de ponto ao gerar diagrama
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

      // CORREÇÃO: Atualiza os dados do diagrama DEPOIS de limpar
      lastDiagramData = data.results;
      lastDiagramType = calcType;
      lastModel = model;
      if (calcType === 'pxy') {
        lastTemperature = data.results.T_C;
        lastPressure = null;
      } else {
        lastPressure = data.results.P_kPa;
        lastTemperature = null;
      }
    } else {
      alert('Erro ao gerar diagrama: ' + (data.error || ''));
    }
  } catch (err) {
    alert('Erro ao gerar diagrama: ' + err.message);
    console.error(err);
  }
}

// ==================== FORMATAÇÃO DE RÓTULOS (x¹, λ¹, P¹sat) =================

function formatLabel(key) {
  // λ_i: lambda1 -> λ¹
  if (key.startsWith('lambda')) {
    const i = key.replace('lambda', '');
    return 'λ<sup>' + i + '</sup>';
  }

  // P_i,sat: "P1_sat (kPa)" -> P¹_sat (kPa)
  if (key.startsWith('P') && key.includes('_sat')) {
    const match = key.match(/^P(\d+)_sat\s*\((.+)\)$/);
    if (match) {
      const i = match[1];
      const unit = match[2];
      return 'P<sup>' + i + '</sup><sub>sat</sub> (' + unit + ')';
    }
  }

  // x1 (ethanol), y2 (benzene), z1, K1 -> x¹ (ethanol) etc.
  if (/^[xyzK]\d/.test(key)) {
    const base = key[0];
    const rest = key.slice(1);
    const m = rest.match(/^(\d+)(.*)$/);
    if (m) {
      const i = m[1];
      const tail = m[2] || '';
      return base + '<sup>' + i + '</sup>' + tail;
    }
  }

  return key;
}

// ==================== EXIBIÇÃO DE RESULTADOS PONTUAIS ====================

function displayResults(results, aiSuggestion = null) {
  const resultsDiv = document.getElementById('results');
  if (!resultsDiv) return;

  const conditionKeys = [
    'T (C)', 'T (K)',
    'P (kPa)', 'P (bar)', 'P (atm)',
    'model',
    'Fracao vapor (beta)',
    'Fracao liquido (1-beta)'
  ];

  const lambdaKeys = [];
  const psatKeys = [];
  const kKeys = [];
  const xKeys = [];
  const yKeys = [];
  const zKeys = [];

  for (const key of Object.keys(results)) {
    if (key.startsWith('lambda')) {
      lambdaKeys.push(key);
    } else if (key.includes('_sat')) {
      psatKeys.push(key);
    } else if (key.toLowerCase().startsWith('k')) {
      kKeys.push(key);
    } else if (key.startsWith('x')) {
      xKeys.push(key);
    } else if (key.startsWith('y')) {
      yKeys.push(key);
    } else if (key.startsWith('z')) {
      zKeys.push(key);
    }
  }

  lambdaKeys.sort();
  psatKeys.sort();
  kKeys.sort();
  xKeys.sort();
  yKeys.sort();
  zKeys.sort();

  let html = '<div class="results-card">';
  html += '<h4 class="mb-3"><i class="bi bi-graph-up"></i> Resultados</h4>';

  // bloco de recomendação da IA
  renderAIRecommendation(aiSuggestion);
  // (o bloco da IA aparece em outro container; aqui só os resultados)

  html += `
    <div class="row g-3">
      <div class="col-md-4">
        <h6 class="section-title-sm">Condições do cálculo</h6>
        <div class="results-grid">
  `;

  conditionKeys.forEach(k => {
    if (results[k] === undefined) return;
    const v = results[k];
    html += `
      <div class="result-item">
        <span class="label">${escapeHtml(k)}</span>
        <span class="value">${typeof v === 'number' ? v.toFixed(4) : escapeHtml(String(v))}</span>
      </div>`;
  });

  html += `
        </div>
      </div>

      <div class="col-md-4">
        <h6 class="section-title-sm">Composição</h6>
        <div class="results-grid">
  `;

  zKeys.forEach(k => {
    const v = results[k];
    html += `
      <div class="result-item">
        <span class="label">${formatLabel(k)}</span>
        <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
      </div>`;
  });

  xKeys.forEach(k => {
    const v = results[k];
    html += `
      <div class="result-item">
        <span class="label">${formatLabel(k)}</span>
        <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
      </div>`;
  });

  yKeys.forEach(k => {
    const v = results[k];
    html += `
      <div class="result-item">
        <span class="label">${formatLabel(k)}</span>
        <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
      </div>`;
  });

  html += `
        </div>
      </div>

      <div class="col-md-4">
        <h6 class="section-title-sm">Propriedades de fase</h6>
        <div class="results-grid">
  `;

  psatKeys.forEach(k => {
    const v = results[k];
    html += `
      <div class="result-item">
        <span class="label">${formatLabel(k)}</span>
        <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
      </div>`;
  });

  kKeys.forEach(k => {
    const v = results[k];
    html += `
      <div class="result-item">
        <span class="label">${formatLabel(k)}</span>
        <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
      </div>`;
  });

  lambdaKeys.forEach(k => {
    const v = results[k];
    html += `
      <div class="result-item">
        <span class="label">${formatLabel(k)}</span>
        <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
      </div>`;
  });

  html += `
        </div>
      </div>
    </div>

    <div class="mt-3 small text-muted-soft">
      Dica: utilize exportação em CSV/PDF para documentar estes resultados ou comparar modelos.
    </div>
  </div>
  `;

  resultsDiv.innerHTML = html;
}

// ==================== BLOCO DE RECOMENDAÇÃO DA IA ===========================

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
  const P = ranges.pressure_kPa || {};
  const modelsForComps = aiSuggestion.recommended_models_for_components || [];
  const bestForModel = aiSuggestion.best_components_for_model || [];
  const detailText = aiSuggestion.details && aiSuggestion.details.reason
    ? aiSuggestion.details.reason
    : '';

  let html = `
    <div class="results-card">
      <div class="section-title-sm">
        <i class="bi bi-stars"></i> Recomendações da IA para este sistema
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
              )}</li>`
          ).join('')}
        </ul>
      </div>
    `;
  }

  if (T.min !== undefined || P.min !== undefined) {
    html += `
      <div class="mb-2">
        <strong>Faixas recomendadas de operação:</strong>
        <div class="text-muted-soft" style="font-size:0.82rem;">
          ${T.min !== undefined ? `Temperatura: ${T.min.toFixed(1)} – ${T.max.toFixed(1)} °C<br>` : ''}
          ${P.min !== undefined ? `Pressão: ${P.min.toFixed(2)} – ${P.max.toFixed(2)} kPa` : ''}
        </div>
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
  if (pre.pressure_kPa !== undefined) {
    const pInput = document.getElementById('pressure');
    const pUnit = document.getElementById('pressUnit');
    if (pInput) pInput.value = pre.pressure_kPa.toFixed(3);
    if (pUnit) pUnit.value = 'kPa';
  }

  if (Array.isArray(pre.liquid_compositions)) {
    const n = Math.min(pre.liquid_compositions.length, selectedComponents.length);
    for (let i = 0; i < n; i++) {
      const el = document.getElementById('x' + (i + 1));
      if (el) el.value = pre.liquid_compositions[i].toFixed(3);
    }
  }

  showNotification('Parâmetros recomendados aplicados ao formulário.', 'info');
}

// ==================== GRÁFICOS (Chart.js) ==================================

function renderChart(results, type) {
  const resultsDiv = document.getElementById('results');

  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }

  let html = '<div class="results-card">';
  html += `<h4 class="mb-3"><i class="bi bi-graph-up"></i> Diagrama ${
    type === 'pxy' ? 'P-x-y' : 'T-x-y'
  }</h4>`;
  html +=
    '<div style="position:relative;height:520px;width:100%;"><canvas id="diagramChart"></canvas></div></div>';
  resultsDiv.innerHTML = html;

  setTimeout(() => {
    const canvas = document.getElementById('diagramChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    Chart.defaults.color = '#e5e7eb';
    Chart.defaults.font.size = 12;

    if (type === 'pxy') {
      const xBubble = results.x_bubble;
      const pBubble = results.P_bubble;
      const yDew = results.y_dew;
      const pDew = results.P_dew;

      currentChart = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [
            {
              label: 'Curva de bolha (x)',
              data: xBubble.map((x, i) => ({ x, y: pBubble[i] })),
              borderColor: '#38bdf8',
              backgroundColor: 'rgba(56,189,248,0.2)',
              tension: 0.18
            },
            {
              label: 'Curva de orvalho (y)',
              data: yDew.map((y, i) => ({ x: y, y: pDew[i] })),
              borderColor: '#22c55e',
              backgroundColor: 'rgba(34,197,94,0.2)',
              tension: 0.18
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top' },
            title: {
              display: true,
              text: `Diagrama P-x-y a ${results.T_C.toFixed(2)} °C`
            }
          },
          scales: {
            x: {
              type: 'linear',
              title: {
                display: true,
                text: 'Fração molar (x, y)'
              },
              min: 0,
              max: 1
            },
            y: {
              title: {
                display: true,
                text: 'Pressão (kPa)'
              }
            }
          }
        }
      });

      lastDiagramData = results;
      lastDiagramType = 'pxy';
      lastTemperature = results.T_C;
      lastPressure = null;
    } else {
      const xBubble = results.x_bubble;
      const tBubble = results.T_bubble;
      const yDew = results.y_dew;
      const tDew = results.T_dew;

      currentChart = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [
            {
              label: 'Curva de bolha (líquido)',
              data: xBubble.map((x, i) => ({ x, y: tBubble[i] })),
              borderColor: '#38bdf8',
              backgroundColor: 'rgba(56,189,248,0.2)',
              tension: 0.18,
              pointRadius: 2
            },
            {
              label: 'Curva de orvalho (vapor)',
              data: yDew.map((y, i) => ({ x: y, y: tDew[i] })),
              borderColor: '#22c55e',
              backgroundColor: 'rgba(34,197,94,0.2)',
              tension: 0.18,
              pointRadius: 2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top' },
            title: {
              display: true,
              text: `Diagrama T-x-y a ${results.P_kPa.toFixed(2)} kPa`
            }
          },
          scales: {
            x: {
              type: 'linear',
              title: {
                display: true,
                text: 'Fração molar (x, y)'
              },
              min: 0,
              max: 1
            },
            y: {
              title: {
                display: true,
                text: 'Temperatura (°C)'
              }
            }
          }
        }
      });

      lastDiagramData = results;
      lastDiagramType = 'txy';
      lastPressure = results.P_kPa;
      lastTemperature = null;
    }
  }, 50);
}

// ==================== EXPORTAÇÃO (já existia, mantido) ====================
// ... (mantém seu bloco de exportação CSV/PDF para diagramas e pontos)

// ==================== COMPARAÇÃO DE MODELOS (trechos relevantes) =========
// No displayPointComparison, use formatLabel para x,y,z,K,lambda,Psat.
// Aqui apenas o padrão da chamada foi adaptado.

function displayPointComparison(results, calcType, components) {
  const container = document.getElementById('comparison-diagram-container');
  if (!container) return;

  const canvas = document.getElementById('comparison-diagram');
  if (canvas && window.comparisonChart) {
    window.comparisonChart.destroy();
    window.comparisonChart = null;
  }

  let html = `
    <div class="results-card">
      <h4 class="mb-3"><i class="bi bi-graph-up"></i> Comparação de Modelos Termodinâmicos</h4>
      <h6 class="section-title-sm mb-3">
        Comparação de Modelos - ${calcType.replace('_', ' ').toUpperCase()}
      </h6>
  `;

  for (const [modelName, res] of Object.entries(results || {})) {
    if (res.error) {
      html += `
        <div class="alert alert-warning mb-3">
          Modelo <strong>${escapeHtml(modelName)}</strong>: ${escapeHtml(res.error)}
        </div>
      `;
      continue;
    }

    const conditionKeys = [
      'T (C)', 'T (K)',
      'P (kPa)', 'P (bar)', 'P (atm)',
      'Fracao vapor (beta)',
      'Fracao liquido (1-beta)'
    ];

    const lambdaKeys = [];
    const psatKeys = [];
    const kKeys = [];
    const xKeys = [];
    const yKeys = [];
    const zKeys = [];

    Object.keys(res).forEach(k => {
      if (k.startsWith('lambda')) lambdaKeys.push(k);
      else if (k.includes('_sat')) psatKeys.push(k);
      else if (k.toLowerCase().startsWith('k')) kKeys.push(k);
      else if (k.startsWith('x')) xKeys.push(k);
      else if (k.startsWith('y')) yKeys.push(k);
      else if (k.startsWith('z')) zKeys.push(k);
    });

    lambdaKeys.sort();
    psatKeys.sort();
    kKeys.sort();
    xKeys.sort();
    yKeys.sort();
    zKeys.sort();

    html += `
      <div class="mt-3 mb-4 p-3" style="border-radius:8px;border:1px solid rgba(148,163,184,0.4);">
        <h6 class="mb-2"><i class="bi bi-diagram-3"></i> Modelo <strong>${escapeHtml(modelName)}</strong></h6>
        <div class="row g-3">
          <div class="col-md-4">
            <h6 class="section-title-sm">Condições do cálculo</h6>
            <div class="results-grid">
    `;

    conditionKeys.forEach(k => {
      if (res[k] === undefined) return;
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${escapeHtml(k)}</span>
          <span class="value">${typeof v === 'number' ? v.toFixed(4) : escapeHtml(String(v))}</span>
        </div>`;
    });

    html += `
            </div>
          </div>
          <div class="col-md-4">
            <h6 class="section-title-sm">Composição</h6>
            <div class="results-grid">
    `;

    zKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${formatLabel(k)}</span>
          <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    xKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${formatLabel(k)}</span>
          <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    yKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${formatLabel(k)}</span>
          <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    html += `
            </div>
          </div>
          <div class="col-md-4">
            <h6 class="section-title-sm">Propriedades de fase</h6>
            <div class="results-grid">
    `;

    psatKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${formatLabel(k)}</span>
          <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    kKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${formatLabel(k)}</span>
          <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    lambdaKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${formatLabel(k)}</span>
          <span class="value">${v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    html += `
            </div>
          </div>
        </div>
      </div>
    `;
  }

  html += '</div>';
  container.innerHTML = html;
  container.style.display = 'block';
}

// ==================== UTILITÁRIOS ====================

function clearForm() {
  selectedComponents = [];
  updateComponentTags();
  updateFields();
  document.getElementById('results').innerHTML = '';

  const btnPts = document.getElementById('export-buttons-points');
  const btnDiag = document.getElementById('export-buttons');
  if (btnPts) btnPts.style.display = 'none';
  if (btnDiag) btnDiag.style.display = 'none';

  window.lastPointResults = null;
  window.lastAiSuggestion = null;
  lastDiagramData = null;
  lastDiagramType = null;

  const compContainer = document.getElementById('comparison-diagram-container');
  if (compContainer) compContainer.style.display = 'none';
  if (window.comparisonChart) {
    window.comparisonChart.destroy();
    window.comparisonChart = null;
  }
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

document.getElementById('model')?.addEventListener('change', async function () {
  const model = this.value;
  await loadComponentsByModel(model);
});

async function loadComponentsByModel(model) {
  try {
    const res = await fetch('/api/components/by-model/' + model);
    const data = await res.json();
    if (!data.success) return;

    allComponents = data.components;
    const validNames = new Set(allComponents.map(c => c.name_en || c.name));
    selectedComponents = selectedComponents.filter(
      c => validNames.has(c.name_en || c.name)
    );
    updateComponentTags();

    if (model !== 'Ideal' && data.count < 60) {
      showInfo(
        `Modelo ${model}: ${data.count} componentes disponíveis com parâmetros.`
      );
    }
  } catch (err) {
    console.error('Erro ao filtrar componentes:', err);
  }
}

function showInfo(message) {
  const alertDiv = document.createElement('div');
  alertDiv.className = 'alert alert-info alert-dismissible fade show mt-2';
  alertDiv.innerHTML = `
    <i class="bi bi-info-circle"></i> ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  const container = document.querySelector('.calc-panel') || document.querySelector('.calc-section');
  if (container) {
    container.insertBefore(alertDiv, container.firstChild);
    setTimeout(() => alertDiv.remove(), 6000);
  }
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

function initializeTooltips() {
  if (typeof bootstrap !== 'undefined') {
    const tooltipTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
}

// modal de comparação
function showCompareModal() {
  if (!lastDiagramType && !window.lastPointResults) {
    alert('Faça primeiro um cálculo pontual ou gere um diagrama P-x-y / T-x-y para comparar modelos.');
    return;
  }
  document.getElementById('compareModal').style.display = 'block';
}

// ==================== FILTRO POR MODELO ====================================

document.getElementById('model')?.addEventListener('change', async function () {
  const model = this.value;
  await loadComponentsByModel(model);
});

// REMOVA a segunda declaração da função e mantenha apenas esta versão corrigida:
async function loadComponentsByModel(model) {
  try {
    const res = await fetch('/api/components/by-model/' + model);
    const data = await res.json();
    if (!data.success) return;

    allComponents = data.components;
    const validNames = new Set(allComponents.map(c => c.name_en || c.name));
    selectedComponents = selectedComponents.filter(
      c => validNames.has(c.name_en || c.name)
    );
    updateComponentTags();

    if (model !== 'Ideal' && data.count < 60) {
      // CORREÇÃO: Verifica se já existe uma mensagem antes de adicionar
      const existingAlert = document.querySelector('.alert.alert-info');
      if (existingAlert) {
        existingAlert.remove();
      }
      
      showInfo(
        `Modelo ${model}: ${data.count} componentes disponíveis com parâmetros.`
      );
    }
  } catch (err) {
    console.error('Erro ao filtrar componentes:', err);
  }
}



// ============================================================================
// ==================== EXPORTAÇÃO E COMPARAÇÃO DE MODELOS ===================
// ============================================================================

// ---------- EXPORTAÇÃO CSV DIAGRAMA ----------
document
  .getElementById('export-csv-btn')
  ?.addEventListener('click', function () {
    if (!lastDiagramData) {
      alert('Nenhum diagrama gerado ainda!');
      return;
    }

    const components = selectedComponents.map(c => c.name_en);

    const payload = {
      diagram_type: lastDiagramType,
      components: components,
      model: lastModel,
      pressure: lastPressure,
      temperature: lastTemperature,
      data: lastDiagramData
    };

    fetch('/elv/export/csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${lastDiagramType.toUpperCase()}_${components[0]}_${components[1]}_${lastModel}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        showNotification('CSV exportado com sucesso!', 'success');
      })
      .catch(error => {
        console.error('Erro ao exportar CSV:', error);
        showNotification('Erro ao exportar CSV', 'danger');
      });
  });

// ---------- EXPORTAÇÃO PDF DIAGRAMA ----------
document
  .getElementById('export-pdf-btn')
  ?.addEventListener('click', function () {
    if (!lastDiagramData) {
      alert('Nenhum diagrama gerado ainda!');
      return;
    }

    const components = selectedComponents.map(c => c.name_en);

    const payload = {
      diagram_type: lastDiagramType,
      components: components,
      model: lastModel,
      pressure: lastPressure,
      temperature: lastTemperature,
      data: lastDiagramData
    };

    fetch('/elv/export/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${lastDiagramType.toUpperCase()}_${components[0]}_${components[1]}_${lastModel}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        showNotification('PDF exportado com sucesso!', 'success');
      })
      .catch(error => {
        console.error('Erro ao exportar PDF:', error);
        showNotification('Erro ao exportar PDF', 'danger');
      });
  });

// ---------- EXPORTAÇÃO CSV RESULTADO PONTUAL ----------
document
  .getElementById('export-csv-points-btn')
  ?.addEventListener('click', function () {
    if (!window.lastPointResults) {
      alert('Nenhum resultado para exportar.');
      return;
    }

    const calcType = document.getElementById('calcType').value;
    const lines = [];
    lines.push('# Módulo ELV - Resultado pontual');
    lines.push('# Tipo de cálculo: ' + calcType);
    lines.push('# Data: ' + new Date().toISOString());
    lines.push('');
    lines.push('Parametro,Valor');

    Object.entries(window.lastPointResults).forEach(([k, v]) => {
      lines.push(`"${k}","${v}"`);
    });

    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url  = window.URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = `ELV_${calcType}_ponto.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    showNotification('CSV exportado com sucesso!', 'success');
  });

// ---------- EXPORTAÇÃO PDF RESULTADO PONTUAL ----------
document
  .getElementById('export-pdf-points-btn')
  ?.addEventListener('click', function () {
    if (!window.lastPointResults) {
      alert('Nenhum resultado para exportar.');
      return;
    }

    const calcType   = document.getElementById('calcType').value;
    const components = selectedComponents.map(c => c.name_en);
    const model      = document.getElementById('model').value;

    const payload = {
      calc_type: calcType,
      results: window.lastPointResults,
      components,
      model
    };

    fetch('/elv/export/point_pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ELV_${calcType}_resultado.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        showNotification('PDF exportado com sucesso!', 'success');
      })
      .catch(error => {
        console.error('Erro ao exportar PDF:', error);
        showNotification('Erro ao exportar PDF', 'danger');
      });
  });

// ---------- COMPARAÇÃO DE MODELOS (PONTO + DIAGRAMA) ----------
// CORREÇÃO no evento do botão de comparação - seção de diagramas
document
  .getElementById('compare-models-btn')
  ?.addEventListener('click', function () {
    const checkboxes = document.querySelectorAll(
      '.model-compare-checkbox:checked'
    );
    const selectedModels = Array.from(checkboxes).map(cb => cb.value);

    if (selectedModels.length < 2) {
      alert('Selecione pelo menos 2 modelos para comparar!');
      return;
    }

    // CORREÇÃO: Melhor detecção do tipo de comparação
    const hasValidDiagram = lastDiagramData && lastDiagramType && (lastPressure !== null || lastTemperature !== null);
    const hasValidPoint = window.lastPointResults && !hasValidDiagram;

    console.log('Estado da comparação:', {
      hasValidDiagram,
      hasValidPoint,
      lastDiagramType,
      lastPressure,
      lastTemperature,
      lastPointResults: !!window.lastPointResults
    });

    // 1) Comparação de cálculo pontual
    if (hasValidPoint) {
      const calcType   = document.getElementById('calcType').value;
      const components = selectedComponents.map(c => c.name_en);

      const payload = {
        calc_type: calcType,
        components,
        models: selectedModels,
        compositions: []
      };

      for (let i = 0; i < selectedComponents.length; i++) {
        const el = document.getElementById('x' + (i + 1));
        const val = parseFloat(el ? el.value : NaN);
        payload.compositions.push(isNaN(val) ? 0 : val);
      }

      if (calcType === 'bubble' || calcType === 'dew') {
        payload.temperature = parseFloat(document.getElementById('temperature').value);
        payload.temperature_unit = document.getElementById('tempUnit').value;
      } else if (calcType === 'bubble_t' || calcType === 'dew_t') {
        payload.pressure = parseFloat(document.getElementById('pressure').value);
        payload.pressure_unit = document.getElementById('pressUnit').value;
      } else if (calcType === 'flash') {
        payload.temperature = parseFloat(document.getElementById('temperature').value);
        payload.temperature_unit = document.getElementById('tempUnit').value;
        payload.pressure = parseFloat(document.getElementById('pressure').value);
        payload.pressure_unit = document.getElementById('pressUnit').value;
      }

      const spinner = document.getElementById('comparison-spinner');
      if (spinner) spinner.style.display = 'block';

      fetch('/elv/calculate/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(response => response.json())
        .then(data => {
          if (spinner) spinner.style.display = 'none';
          document.getElementById('compareModal').style.display = 'none';

          if (data.success) {
            displayPointComparison(data.results, calcType, components);
            const container = document.getElementById('comparison-diagram-container');
            if (container) {
              container.style.display = 'block';
              container.scrollIntoView({ behavior: 'smooth' });
            }
          } else {
            showNotification(
              'Erro ao comparar modelos: ' + data.error,
              'danger'
            );
          }
        })
        .catch(error => {
          if (spinner) spinner.style.display = 'none';
          console.error('Erro:', error);
          showNotification('Erro ao comparar modelos', 'danger');
        });

      return;
    }

    // 2) Comparação de diagramas
    if (hasValidDiagram) {
      if (selectedComponents.length !== 2) {
        alert('A comparação de diagramas só está disponível para sistemas binários!');
        return;
      }

      const spinner = document.getElementById('comparison-spinner');
      if (spinner) spinner.style.display = 'block';

      const components = selectedComponents.map(c => c.name_en);
      const diagramType = lastDiagramType;

      const payload = {
        diagram_type: diagramType,
        components,
        models: selectedModels
      };

      // CORREÇÃO: Adiciona os parâmetros corretos baseado no tipo
      if (diagramType === 'txy') {
        payload.pressure = lastPressure;
        payload.pressure_unit = 'kPa';
      } else if (diagramType === 'pxy') {
        payload.temperature = lastTemperature;
        payload.temperature_unit = 'C';
      }

      console.log('Enviando requisição de comparação de diagrama:', payload);

      fetch('/elv/diagram/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
        .then(response => response.json())
        .then(data => {
          if (spinner) spinner.style.display = 'none';
          document.getElementById('compareModal').style.display = 'none';

          console.log('Resposta da comparação de diagrama:', data);

          if (data.success) {
            // CORREÇÃO: Limpa o container antes de plotar
            const container = document.getElementById('comparison-diagram-container');
            if (container) {
              container.innerHTML = '';
              container.style.display = 'none';
            }

            // Plota o novo diagrama
            plotComparisonDiagram(data.results, diagramType, components);
            
            // Mostra o container
            if (container) {
              container.style.display = 'block';
              setTimeout(() => {
                container.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }, 150);
            }
          } else {
            showNotification(
              'Erro ao comparar modelos: ' + (data.error || 'Erro desconhecido'),
              'danger'
            );
          }
        })
        .catch(error => {
          if (spinner) spinner.style.display = 'none';
          console.error('Erro na comparação:', error);
          showNotification('Erro ao comparar modelos: ' + error.message, 'danger');
        });

      return;
    }

    // Se chegou aqui, não há dados válidos
    alert('Faça primeiro um cálculo pontual ou gere um diagrama P-x-y / T-x-y para comparar modelos.');
  });


// ---------- PLOTAR DIAGRAMA DE COMPARAÇÃO ----------
// CORREÇÃO COMPLETA da função plotComparisonDiagram
function plotComparisonDiagram(results, diagramType, components) {
  const container = document.getElementById('comparison-diagram-container');
  if (!container) return;

  // CORREÇÃO: Limpa completamente o container antes de renderizar
  if (window.comparisonChart) {
    window.comparisonChart.destroy();
    window.comparisonChart = null;
  }

  // CORREÇÃO: Recria o HTML do container com o canvas
  container.innerHTML = `
    <div class="results-card">
      <h4 class="mb-3">
        <i class="bi bi-graph-up"></i> 
        Comparação de Modelos Termodinâmicos
      </h4>
      <h6 class="section-title-sm mb-3">
        Comparação de Diagramas ${diagramType.toUpperCase()} - ${components[0].toUpperCase()} / ${components[1].toUpperCase()}
      </h6>
      <div style="position:relative;height:520px;width:100%;">
        <canvas id="comparison-diagram"></canvas>
      </div>
    </div>
  `;

  // CORREÇÃO: Aguarda o DOM ser atualizado antes de criar o gráfico
  setTimeout(() => {
    const canvas = document.getElementById('comparison-diagram');
    if (!canvas) {
      console.error('Canvas não encontrado após recriar');
      return;
    }

    const ctx = canvas.getContext('2d');
    const datasets = [];

    const colors = [
      { bubble: '#38bdf8', dew: '#0ea5e9' },
      { bubble: '#22c55e', dew: '#16a34a' },
      { bubble: '#f59e0b', dew: '#d97706' },
      { bubble: '#ef4444', dew: '#dc2626' },
      { bubble: '#8b5cf6', dew: '#7c3aed' },
      { bubble: '#ec4899', dew: '#db2777' }
    ];

    let colorIndex = 0;

    for (const [model, data] of Object.entries(results)) {
      if (data.error) {
        console.warn(`Modelo ${model} falhou: ${data.error}`);
        continue;
      }

      const color = colors[colorIndex % colors.length];

      if (diagramType === 'pxy') {
        // Curva de bolha
        datasets.push({
          label: `${model} (Bolha)`,
          data: data.x_bubble.map((x, i) => ({ x, y: data.P_bubble[i] })),
          borderColor: color.bubble,
          backgroundColor: 'transparent',
          tension: 0.18,
          pointRadius: 1,
          pointHoverRadius: 4,
          borderWidth: 2
        });

        // Curva de orvalho
        datasets.push({
          label: `${model} (Orvalho)`,
          data: data.y_dew.map((y, i) => ({ x: y, y: data.P_dew[i] })),
          borderColor: color.dew,
          backgroundColor: 'transparent',
          tension: 0.18,
          pointRadius: 1,
          pointHoverRadius: 4,
          borderWidth: 2,
          borderDash: [5, 5]
        });
      } else if (diagramType === 'txy') {
        // Curva de bolha
        datasets.push({
          label: `${model} (Bolha)`,
          data: data.x_bubble.map((x, i) => ({ x, y: data.T_bubble[i] })),
          borderColor: color.bubble,
          backgroundColor: 'transparent',
          tension: 0.18,
          pointRadius: 1,
          pointHoverRadius: 4,
          borderWidth: 2
        });

        // Curva de orvalho
        datasets.push({
          label: `${model} (Orvalho)`,
          data: data.y_dew.map((y, i) => ({ x: y, y: data.T_dew[i] })),
          borderColor: color.dew,
          backgroundColor: 'transparent',
          tension: 0.18,
          pointRadius: 1,
          pointHoverRadius: 4,
          borderWidth: 2,
          borderDash: [5, 5]
        });
      }

      colorIndex++;
    }

    if (datasets.length === 0) {
      container.innerHTML += '<div class="alert alert-warning mt-3">Nenhum modelo retornou dados válidos para comparação.</div>';
      return;
    }

    Chart.defaults.color = '#e5e7eb';
    Chart.defaults.font.size = 12;

    window.comparisonChart = new Chart(ctx, {
      type: 'line',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 15,
              font: {
                size: 11
              }
            }
          },
          title: {
            display: true,
            text: `Comparação de Modelos - Diagrama ${diagramType.toUpperCase()}`,
            font: {
              size: 14,
              weight: 'bold'
            }
          },
          tooltip: {
            mode: 'nearest',
            intersect: false
          }
        },
        scales: {
          x: {
            type: 'linear',
            title: {
              display: true,
              text: `Fração molar (x, y) - ${components[0]}`
            },
            min: 0,
            max: 1,
            ticks: {
              stepSize: 0.1
            }
          },
          y: {
            title: {
              display: true,
              text: diagramType === 'txy' ? 'Temperatura (°C)' : 'Pressão (kPa)'
            }
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        }
      }
    });

    console.log('Gráfico de comparação criado com sucesso');
  }, 100);
}

function clearComparison() {
  const container = document.getElementById('comparison-diagram-container');
  if (container) {
    container.innerHTML = '';
    container.style.display = 'none';
  }
  if (window.comparisonChart) {
    window.comparisonChart.destroy();
    window.comparisonChart = null;
  }
}

// ---------- TABELA DE COMPARAÇÃO DE RESULTADOS PONTUAIS ----------
function displayPointComparison(results, calcType, components) {
  const container = document.getElementById('comparison-diagram-container');
  if (!container) return;

  // limpa gráfico anterior, se houver
  const canvas = document.getElementById('comparison-diagram');
  if (canvas && window.comparisonChart) {
    window.comparisonChart.destroy();
    window.comparisonChart = null;
  }

  let html = `
    <div class="results-card">
      <h4 class="mb-3">
        <i class="bi bi-graph-up"></i>
        Comparação de Modelos Termodinâmicos
      </h4>
      <h6 class="section-title-sm mb-3">
        Comparação de Modelos - ${calcType.replace('_', ' ').toUpperCase()}
      </h6>
  `;

  // para cada modelo, monta um "card" no mesmo padrão do displayResults
  for (const [modelName, res] of Object.entries(results)) {
    if (res.error) {
      html += `
        <div class="alert alert-warning mb-3">
          Modelo <strong>${escapeHtml(modelName)}</strong>: ${escapeHtml(res.error)}
        </div>`;
      continue;
    }

    const conditionKeys = [
      'T (C)', 'T (K)', 'P (kPa)', 'P (bar)', 'P (atm)',
      'Fracao vapor (beta)', 'Fracao liquido (1-beta)'
    ];
    const gammaKeys = [];
    const psatKeys  = [];
    const kKeys     = [];
    const xKeys     = [];
    const yKeys     = [];
    const zKeys     = [];

    Object.keys(res).forEach(k => {
      if (k.startsWith('gamma')) gammaKeys.push(k);
      else if (k.includes('_sat')) psatKeys.push(k);
      else if (k.toLowerCase().startsWith('k')) kKeys.push(k);
      else if (k.startsWith('x')) xKeys.push(k);
      else if (k.startsWith('y')) yKeys.push(k);
      else if (k.startsWith('z')) zKeys.push(k);
    });

    gammaKeys.sort();
    psatKeys.sort();
    kKeys.sort();
    xKeys.sort();
    yKeys.sort();
    zKeys.sort();

    html += `
      <div class="mt-3 mb-4 p-3" style="border-radius:8px;border:1px solid rgba(148,163,184,0.4);">
        <h6 class="mb-2">
          <i class="bi bi-diagram-3"></i>
          Modelo: <strong>${escapeHtml(modelName)}</strong>
        </h6>
        <div class="row g-3">
          <div class="col-md-4">
            <h6 class="section-title-sm">Condições do cálculo</h6>
            <div class="results-grid">
    `;

    // condições
    conditionKeys.forEach(k => {
      if (res[k] !== undefined) {
        const v = res[k];
        html += `
          <div class="result-item">
            <span class="label">${escapeHtml(k)}</span>
            <span class="value">${typeof v === 'number'
              ? v.toFixed(4)
              : escapeHtml(String(v))}</span>
          </div>`;
      }
    });

    // modelo
    html += `
          <div class="result-item">
            <span class="label">model</span>
            <span class="value">${escapeHtml(modelName)}</span>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <h6 class="section-title-sm">Composição</h6>
        <div class="results-grid">
    `;

    zKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${escapeHtml(k)}</span>
          <span class="value">${v && v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    xKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${escapeHtml(k)}</span>
          <span class="value">${v && v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    yKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${escapeHtml(k)}</span>
          <span class="value">${v && v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    html += `
        </div>
      </div>

      <div class="col-md-4">
        <h6 class="section-title-sm">Propriedades de fase</h6>
        <div class="results-grid">
    `;

    psatKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${escapeHtml(k)}</span>
          <span class="value">${v && v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    kKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${escapeHtml(k)}</span>
          <span class="value">${v && v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    gammaKeys.forEach(k => {
      const v = res[k];
      html += `
        <div class="result-item">
          <span class="label">${escapeHtml(k)}</span>
          <span class="value">${v && v.toFixed ? v.toFixed(4) : v}</span>
        </div>`;
    });

    html += `
            </div>
          </div>
        </div>
      </div>
    `;
  }

  html += '</div>'; // fecha results-card

  container.innerHTML = html;
}

// ========== NOTIFICAÇÕES ==========
function showNotification(message, type) {
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.top = '20px';
  alertDiv.style.right = '20px';
  alertDiv.style.zIndex = '9999';
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
  document.body.appendChild(alertDiv);

  setTimeout(() => {
    alertDiv.remove();
  }, 5000);
}

// ========== INICIALIZAR TOOLTIPS ==========
function initializeTooltips() {
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
}

// ========== FUNÇÃO GLOBAL PARA MODAL DE COMPARAÇÃO (USADA NO HTML) ==========
function showCompareModal() {
  if (!lastDiagramType && !window.lastPointResults) {
    alert('Faça primeiro um cálculo pontual ou gere um diagrama P-x-y / T-x-y para comparar modelos.');
    return;
  }
  document.getElementById('compareModal').style.display = 'block';
}
