let moduleChart, modelChart;

document.addEventListener('DOMContentLoaded', async function() {
    await loadStatistics();
    await loadHistory();
});

async function loadStatistics() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;
            
            const total = stats.total_simulations || 0;
            const successful = stats.successful || 0;

            const successRate = total > 0 ? ((successful / total) * 100).toFixed(1) : '0.0';
            const avgTime = stats.avg_execution_time ? parseFloat(stats.avg_execution_time).toFixed(2) : '0.00';

            document.getElementById('totalSimulations').textContent = total;
            document.getElementById('successRate').textContent = successRate + '%';
            document.getElementById('avgTime').textContent = avgTime + 's';
            
            // FIX: Calcular "hoje" manualmente
            const hojeStr = new Date().toISOString().split('T')[0];
            fetch('/api/dashboard/simulations')
                .then(r => r.json())
                .then(d => {
                    if (d.success && d.simulations) {
                        const hojeCount = d.simulations.filter(s => 
                            s.timestamp && s.timestamp.startsWith(hojeStr)
                        ).length;
                        document.getElementById('todaySimulations').textContent = hojeCount;
                    }
                })
                .catch(() => {
                    document.getElementById('todaySimulations').textContent = 0;
                });

            // ✅ ADICIONAR ESTA LINHA - Renderizar gráficos!
            renderCharts(stats);
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

async function loadHistory() {
    try {
        const response = await fetch('/api/dashboard/simulations');
        const data = await response.json();

        if (data.success) {
            renderHistory(data.simulations || []);
        }
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
        document.getElementById('simulationHistory').innerHTML = 
            '<p class="text-muted-soft text-center py-4">Erro ao carregar histórico de simulações</p>';
    }
}

function renderHistory(simulations) {
    const container = document.getElementById('simulationHistory');

    if (!simulations || simulations.length === 0) {
        container.innerHTML = '<p class="text-muted-soft text-center py-4">Nenhuma simulação encontrada</p>';
        return;
    }

    container.innerHTML = simulations.map(sim => {
        const date = sim.timestamp ? new Date(sim.timestamp) : null;
        const moduleClass = 'module-' + (sim.module || 'elv').toLowerCase();
        const statusClass = sim.success ? 'success' : 'error';

        let componentsText = '';
        try {
            if (Array.isArray(sim.components)) {
                componentsText = sim.components.join(', ');
            } else if (typeof sim.components === 'string') {
                const parsed = JSON.parse(sim.components);
                componentsText = Array.isArray(parsed) ? parsed.join(', ') : String(sim.components);
            } else {
                componentsText = String(sim.components || '');
            }
        } catch {
            componentsText = String(sim.components || 'N/A');
        }

        const execTime = sim.execution_time != null && !isNaN(sim.execution_time)
            ? parseFloat(sim.execution_time).toFixed(3)
            : '0.000';

        return `
            <div class="simulation-item ${statusClass}" onclick="viewSimulation(${sim.id})">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="d-flex align-items-center gap-3">
                        <span class="module-badge ${moduleClass}">
                            ${(sim.module || 'ELV').toUpperCase()}
                        </span>
                        <div>
                            <div class="mb-1">
                                <strong style="color: #e5e7eb;">${sim.calculation_type || 'Cálculo'}</strong>
                                <span class="text-muted-soft ms-2">· ${sim.model || 'N/A'}</span>
                            </div>
                            <div class="text-muted-soft" style="font-size: 0.85rem;">
                                <i class="bi bi-flask"></i> ${componentsText}
                            </div>
                        </div>
                    </div>
                    <div class="text-end">
                        <div class="text-muted-soft" style="font-size: 0.8rem; margin-bottom: 0.3rem;">
                            ${date ? date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR') : 'N/A'}
                        </div>
                        <div>
                            <span class="${sim.success ? 'text-success' : 'text-danger'}" style="font-size: 0.85rem;">
                                <i class="bi bi-${sim.success ? 'check-circle-fill' : 'x-circle-fill'}"></i>
                                ${sim.success ? 'Sucesso' : 'Erro'}
                            </span>
                            <span class="text-muted-soft ms-2" style="font-size: 0.8rem;">
                                <i class="bi bi-stopwatch"></i> ${execTime}s
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderCharts(stats) {
    // Gráfico de módulos
    const ctxModule = document.getElementById('moduleChart');
    if (!ctxModule) return;
    
    const ctx = ctxModule.getContext('2d');
    if (moduleChart) moduleChart.destroy();

    const byModule = stats.by_module || {};

    moduleChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['ELV', 'ELL', 'ESL'],
            datasets: [{
                label: 'Simulações',
                data: [
                    byModule.elv || 0,
                    byModule.ell || 0,
                    byModule.esl || 0
                ],
                backgroundColor: [
                    'rgba(56, 189, 248, 0.7)',
                    'rgba(249, 115, 22, 0.7)',
                    'rgba(34, 197, 94, 0.7)'
                ],
                borderColor: [
                    '#38bdf8',
                    '#f97316',
                    '#22c55e'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e5e7eb',
                    bodyColor: '#e5e7eb',
                    borderColor: 'rgba(148, 163, 184, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Gráfico de modelos
    const ctxModel = document.getElementById('modelChart');
    if (!ctxModel) return;
    
    const ctx2 = ctxModel.getContext('2d');
    if (modelChart) modelChart.destroy();

    const byModel = stats.by_model || {};
    const modelLabels = Object.keys(byModel);
    const modelData = Object.values(byModel);

    modelChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: modelLabels,
            datasets: [{
                data: modelData,
                backgroundColor: [
                    'rgba(56, 189, 248, 0.7)',
                    'rgba(249, 115, 22, 0.7)',
                    'rgba(34, 197, 94, 0.7)',
                    'rgba(168, 85, 247, 0.7)',
                    'rgba(236, 72, 153, 0.7)'
                ],
                borderColor: [
                    '#38bdf8',
                    '#f97316',
                    '#22c55e',
                    '#a855f7',
                    '#ec4899'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e5e7eb',
                    bodyColor: '#e5e7eb',
                    borderColor: 'rgba(148, 163, 184, 0.3)',
                    borderWidth: 1,
                    padding: 12
                }
            }
        }
    });
}

// Variável global para armazenar o gráfico do modal
let simulationChart = null;

// Visualizar detalhes da simulação com GRÁFICO
// Visualizar detalhes da simulação com GRÁFICO
async function viewSimulation(id) {
    try {
        const res = await fetch('/api/dashboard/' + id);
        const data = await res.json();

        if (!data.success) {
            alert('Erro ao carregar simulação: ' + (data.error || 'Erro desconhecido'));
            return;
        }

        const sim = data.simulation || {};
        let results = {};

        try {
            if (typeof sim.results === 'string') {
                results = JSON.parse(sim.results);
            } else if (typeof sim.results === 'object' && sim.results !== null) {
                results = sim.results;
            }
        } catch {
            results = {};
        }

        const body = document.getElementById('simulationModalBody');
        if (!body) return;

        const componentsText = (() => {
            try {
                if (Array.isArray(sim.components)) return sim.components.join(', ');
                if (typeof sim.components === 'string') {
                    const p = JSON.parse(sim.components);
                    return Array.isArray(p) ? p.join(', ') : String(sim.components);
                }
                return String(sim.components || 'N/A');
            } catch {
                return String(sim.components || 'N/A');
            }
        })();

        const moduleClass = 'module-' + (sim.module || 'elv').toLowerCase();
        const moduleName = (sim.module || 'ELV').toUpperCase();

        // ✅ DETECÇÃO DE TIPO DE GRÁFICO
        const graphType = detectGraphType(results, moduleName);
        
        console.log('🔍 Módulo:', moduleName);
        console.log('🔍 Tipo de gráfico detectado:', graphType);
        console.log('🔍 Chaves de results:', Object.keys(results));

        let html = `
            <div class="mb-3">
                <div class="d-flex align-items-center gap-2 mb-2">
                    <span class="module-badge ${moduleClass}">
                        ${moduleName}
                    </span>
                    <h6 class="mb-0" style="color: #e5e7eb;">Simulação #${sim.id}</h6>
                </div>
                <p class="text-muted-soft mb-0" style="font-size: 0.9rem;">
                    <strong>Tipo:</strong> ${sim.calculation_type || 'N/A'} · 
                    <strong>Modelo:</strong> ${sim.model || 'N/A'}<br>
                    <strong>Componentes:</strong> ${componentsText}
                </p>
            </div>
        `;

        if (graphType !== 'none') {
            // MOSTRAR GRÁFICO PRIMEIRO
            html += `
                <div class="mb-3">
                    <div class="panel-title mb-2">
                        <i class="bi bi-graph-up"></i> ${getGraphTitle(graphType)}
                    </div>
                    <div style="background: rgba(30, 41, 59, 0.5); border-radius: 8px; padding: 1rem;">
                        <canvas id="simulationChartCanvas" style="height: 400px;"></canvas>
                    </div>
                </div>
                
                <details style="margin-top: 1rem;">
                    <summary class="text-muted-soft" style="cursor: pointer; padding: 0.5rem; font-size: 0.9rem;">
                        <i class="bi bi-table"></i> Ver dados numéricos
                    </summary>
                    <div class="results-grid mt-3" style="grid-template-columns: 1fr;">
            `;

            // Renderizar dados numéricos formatados
            for (const [key, value] of Object.entries(results)) {
                let displayValue = formatValue(value);
                html += `
                    <div class="result-item">
                        <span class="label">${key}</span>
                        <span class="value" style="word-break: break-word; font-size: 0.85rem;">${displayValue}</span>
                    </div>
                `;
            }

            html += `
                    </div>
                </details>
            `;
        } else {
            // Sem gráfico - apenas tabela
            html += `<div class="results-grid">`;

            for (const [key, value] of Object.entries(results)) {
                let displayValue = formatValue(value);
                html += `
                    <div class="result-item">
                        <span class="label">${key}</span>
                        <span class="value">${displayValue}</span>
                    </div>
                `;
            }

            html += `</div>`;
        }

        body.innerHTML = html;

        // Abrir modal Bootstrap 5
        const modalEl = document.getElementById('simulationModal');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        // Se tem gráfico, renderizar após o modal abrir
        if (graphType !== 'none') {
            setTimeout(() => {
                renderGraphByType(results, graphType);
            }, 300);
        }
    } catch (error) {
        console.error('Erro ao visualizar simulação:', error);
        alert('Erro ao visualizar simulação');
    }
}

function detectGraphType(results, module) {
    const keys = Object.keys(results);
    
    // ELV - Diagrama P-xy ou T-xy
    if (module === 'ELV') {
        const hasPBubble = keys.some(k => k.toLowerCase().includes('p_bubble') || k === 'P');
        const hasTBubble = keys.some(k => k.toLowerCase().includes('t_bubble') || k === 'T_C' || k === 'T');
        const hasX = keys.some(k => k.toLowerCase().includes('x_bubble') || k === 'x' || k === 'x1');
        
        for (const key of keys) {
            if (Array.isArray(results[key]) && results[key].length > 5) {
                if (hasTBubble && hasX) return 'txy';
                if (hasPBubble && hasX) return 'pxy';
            }
        }
    }
    
    // ELL - Diagrama ternário
    if (module === 'ELL') {
        const hasBinodal = keys.some(k => k.toLowerCase().includes('binodal'));
        const hasTieLines = keys.some(k => k.toLowerCase().includes('tie'));
        if (hasBinodal || hasTieLines) return 'ternary';
    }
    
    // ✅ ESL - Diagrama T-x binário (CORRIGIDO!)
    if (module === 'ESL') {
        // Verificar T_left_C ou T_right_C (não T_liquidus!)
        const hasTLeft = keys.some(k => k === 'T_left_C' || k === 'T_LEFT_C');
        const hasTRight = keys.some(k => k === 'T_right_C' || k === 'T_RIGHT_C');
        const hasX1Left = keys.some(k => k === 'x1_left' || k === 'X1_LEFT');
        const hasX1Right = keys.some(k => k === 'x1_right' || k === 'X1_RIGHT');
        
        // Se tem T_left_C/T_right_C e x1_left/x1_right, é diagrama T-x
        if ((hasTLeft || hasTRight) && (hasX1Left || hasX1Right)) {
            // Verificar se são arrays
            for (const key of keys) {
                if (Array.isArray(results[key]) && results[key].length > 3) {
                    return 'esl-tx';
                }
            }
        }
        
        // ✅ ESL - Diagrama ternário
        const hasPoints = keys.some(k => k === 'points');
        if (hasPoints && Array.isArray(results.points) && results.points.length > 0) {
            return 'esl-ternary';
        }
    }
    
    return 'none';
}


function getGraphTitle(graphType) {
    const titles = {
        'pxy': 'Diagrama P-x-y',
        'txy': 'Diagrama T-x-y',
        'ternary': 'Diagrama Ternário (ELL)',
        'esl-tx': 'Diagrama T-x (Liquidus)',
        'esl-ternary': 'Diagrama Ternário (ESL)'
    };
    return titles[graphType] || 'Diagrama de Fases';
}


function formatValue(value) {
    if (Array.isArray(value)) {
        return value.map(v => 
            typeof v === 'number' ? v.toFixed(4) : String(v)
        ).join(', ');
    } else if (typeof value === 'number') {
        return value.toFixed(4);
    } else {
        return String(value);
    }
}

function renderGraphByType(results, graphType) {
    switch (graphType) {
        case 'pxy':
        case 'txy':
            renderELVChart(results, graphType);
            break;
        case 'ternary':
            renderELLTernaryChart(results);
            break;
        case 'esl-tx':
            renderESLTxChart(results);
            break;
        case 'esl-ternary':
            renderESLTernaryChart(results);
            break;
        default:
            console.error('Tipo de gráfico desconhecido:', graphType);
    }
}

function renderSimulationChart(results) {
    const canvas = document.getElementById('simulationChartCanvas');
    if (!canvas) {
        console.error('❌ Canvas não encontrado!');
        return;
    }

    if (simulationChart) {
        simulationChart.destroy();
    }

    console.log('📊 Results recebidos:', results);

    // CORREÇÃO COMPLETA: Buscar todos os formatos possíveis
    let pBubble = results.P_bubble || results.P_BUBBLE || results.p_bubble || results.P;
    let pDew = results.P_dew || results.P_DEW || results.p_dew;
    
    // ✅ ADICIONAR DETECÇÃO DE T_bubble e T_dew para diagrama T-xy
    let tBubble = results.T_bubble || results.T_BUBBLE || results.t_bubble;
    let tDew = results.T_dew || results.T_DEW || results.t_dew;
    let tData = tBubble || tDew || results.T_C || results.T || results.t;
    
    let xBubble = results.x_bubble || results.X_BUBBLE || results.x1 || results.x;
    let yBubble = results.y_bubble || results.Y_BUBBLE || results.y1 || results.y;
    let xDew = results.x_dew || results.X_DEW;
    let yDew = results.y_dew || results.Y_DEW;

    const toArray = (val) => {
        if (!val) return [];
        return Array.isArray(val) ? val : [val];
    };
    
    pBubble = toArray(pBubble);
    pDew = toArray(pDew);
    tBubble = toArray(tBubble);
    tDew = toArray(tDew);
    tData = toArray(tData);
    xBubble = toArray(xBubble);
    yBubble = toArray(yBubble);
    xDew = toArray(xDew);
    yDew = toArray(yDew);

    console.log('📈 Arrays convertidos:');
    console.log('  P_bubble:', pBubble.length, 'valores -', pBubble.slice(0, 3));
    console.log('  P_dew:', pDew.length, 'valores -', pDew.slice(0, 3));
    console.log('  T_bubble:', tBubble.length, 'valores -', tBubble.slice(0, 3));
    console.log('  T_dew:', tDew.length, 'valores -', tDew.slice(0, 3));
    console.log('  x_bubble:', xBubble.length, 'valores -', xBubble.slice(0, 3));
    console.log('  y_bubble:', yBubble.length, 'valores -', yBubble.slice(0, 3));

    // ✅ LÓGICA CORRIGIDA: Detectar tipo de diagrama
    let yAxisData = [];
    let yAxisLabel = '';
    let isTxyDiagram = false;

    // Prioridade 1: Diagrama T-xy (T_bubble e T_dew)
    if (tBubble.length > 1 || tDew.length > 1) {
        yAxisData = tBubble.length > 1 ? tBubble : tDew;
        yAxisLabel = 'Temperatura (°C)';
        isTxyDiagram = true;
        console.log('✅ DETECTADO: Diagrama T-xy');
    }
    // Prioridade 2: Diagrama P-xy (P_bubble e P_dew)
    else if (pBubble.length > 1 || pDew.length > 1) {
        yAxisData = pBubble.length > 1 ? pBubble : pDew;
        yAxisLabel = 'Pressão (kPa)';
        console.log('✅ DETECTADO: Diagrama P-xy');
    }
    // Fallback: Usar o que tiver disponível
    else if (tData.length > 1) {
        yAxisData = tData;
        yAxisLabel = 'Temperatura (°C)';
        isTxyDiagram = true;
        console.log('⚠️ USANDO T_C genérico');
    } else if (pBubble.length > 0) {
        yAxisData = pBubble;
        yAxisLabel = 'Pressão (kPa)';
    } else if (tData.length > 0) {
        yAxisData = tData;
        yAxisLabel = 'Temperatura (°C)';
        isTxyDiagram = true;
    }

    console.log('🎯 Eixo Y escolhido:', yAxisLabel);
    console.log('🎯 Dados do eixo Y:', yAxisData.slice(0, 5));

    const datasets = [];

    // ✅ CORRIGIDO: Curva de bolha
    if (isTxyDiagram) {
        // Diagrama T-xy: x_bubble vs T_bubble
        if (xBubble.length > 0 && tBubble.length > 0) {
            const bubbleData = xBubble.map((x, i) => ({
                x: parseFloat(x),
                y: parseFloat(tBubble[Math.min(i, tBubble.length - 1)])
            })).filter(point => !isNaN(point.x) && !isNaN(point.y));

            bubbleData.sort((a, b) => a.x - b.x);

            datasets.push({
                label: 'Ponto de Bolha (x)',
                data: bubbleData,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                pointBackgroundColor: '#38bdf8',
                pointRadius: 4,
                pointHoverRadius: 6,
                borderWidth: 2,
                showLine: true,
                tension: 0.3
            });

            console.log('✓ Dataset Bolha (T-xy) criado:', bubbleData.length, 'pontos');
        }

        // Diagrama T-xy: y_bubble vs T_bubble (ou y_dew vs T_dew)
        const yData = yBubble.length > 0 ? yBubble : yDew;
        const tDataForDew = tBubble.length > 0 ? tBubble : tDew;
        
        if (yData.length > 0 && tDataForDew.length > 0) {
            const dewData = yData.map((y, i) => ({
                x: parseFloat(y),
                y: parseFloat(tDataForDew[Math.min(i, tDataForDew.length - 1)])
            })).filter(point => !isNaN(point.x) && !isNaN(point.y));

            dewData.sort((a, b) => a.x - b.x);

            datasets.push({
                label: 'Ponto de Orvalho (y)',
                data: dewData,
                borderColor: '#f97316',
                backgroundColor: 'rgba(249, 115, 22, 0.1)',
                pointBackgroundColor: '#f97316',
                pointRadius: 4,
                pointHoverRadius: 6,
                borderWidth: 2,
                showLine: true,
                tension: 0.3
            });

            console.log('✓ Dataset Orvalho (T-xy) criado:', dewData.length, 'pontos');
        }
    } else {
        // Diagrama P-xy: x_bubble vs P_bubble
        if (xBubble.length > 0 && pBubble.length > 0) {
            const bubbleData = xBubble.map((x, i) => ({
                x: parseFloat(x),
                y: parseFloat(pBubble[Math.min(i, pBubble.length - 1)])
            })).filter(point => !isNaN(point.x) && !isNaN(point.y));

            bubbleData.sort((a, b) => a.x - b.x);

            datasets.push({
                label: 'Ponto de Bolha (x)',
                data: bubbleData,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                pointBackgroundColor: '#38bdf8',
                pointRadius: 4,
                pointHoverRadius: 6,
                borderWidth: 2,
                showLine: true,
                tension: 0.3
            });

            console.log('✓ Dataset Bolha (P-xy) criado:', bubbleData.length, 'pontos');
        }

        // Diagrama P-xy: y_bubble vs P_bubble
        if (yBubble.length > 0 && pBubble.length > 0) {
            const dewData = yBubble.map((y, i) => ({
                x: parseFloat(y),
                y: parseFloat(pBubble[Math.min(i, pBubble.length - 1)])
            })).filter(point => !isNaN(point.x) && !isNaN(point.y));

            dewData.sort((a, b) => a.x - b.x);

            datasets.push({
                label: 'Ponto de Orvalho (y)',
                data: dewData,
                borderColor: '#f97316',
                backgroundColor: 'rgba(249, 115, 22, 0.1)',
                pointBackgroundColor: '#f97316',
                pointRadius: 4,
                pointHoverRadius: 6,
                borderWidth: 2,
                showLine: true,
                tension: 0.3
            });

            console.log('✓ Dataset Orvalho (P-xy) criado:', dewData.length, 'pontos');
        }
    }

    if (datasets.length === 0) {
        console.error('❌ NENHUM DATASET CRIADO!');
        return;
    }

    const ctx = canvas.getContext('2d');

    simulationChart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { size: 13 },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e5e7eb',
                    bodyColor: '#e5e7eb',
                    borderColor: 'rgba(148, 163, 184, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const comp = context.dataset.label.includes('Bolha') ? 'x' : 'y';
                            return `${comp} = ${context.parsed.x.toFixed(4)}, ${yAxisLabel.split(' ')[0]} = ${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Fração Molar (x, y)',
                        color: '#94a3b8',
                        font: { size: 13, weight: 'bold' }
                    },
                    ticks: { 
                        color: '#94a3b8',
                        stepSize: 0.1
                    },
                    grid: { 
                        color: 'rgba(148, 163, 184, 0.15)',
                        lineWidth: 1
                    },
                    min: 0,
                    max: 1
                },
                y: {
                    title: {
                        display: true,
                        text: yAxisLabel,
                        color: '#94a3b8',
                        font: { size: 13, weight: 'bold' }
                    },
                    ticks: { 
                        color: '#94a3b8'
                    },
                    grid: { 
                        color: 'rgba(148, 163, 184, 0.15)',
                        lineWidth: 1
                    }
                }
            }
        }
    });

    console.log('✅ Gráfico renderizado com sucesso!');
    console.log('📊 Label do eixo Y:', yAxisLabel);
}

// ========================================================================
// RENDERIZADOR ESL - DIAGRAMA T-x (LIQUIDUS)
// ========================================================================

function renderESLTxChart(results) {
    const canvas = document.getElementById('simulationChartCanvas');
    if (!canvas) return;

    if (simulationChart) {
        simulationChart.destroy();
    }

    // ✅ BUSCAR NOMES CORRETOS (minúsculas com underscore)
    const x1_left = results.x1_left || results.X1_LEFT || [];
    const x1_right = results.x1_right || results.X1_RIGHT || [];
    const t_left = results.T_left_C || results.T_LEFT_C || [];
    const t_right = results.T_right_C || results.T_RIGHT_C || [];
    
    // Ponto eutético
    const T_eutectic = results.T_eutectic_C || results.T_EUTECTIC_C || null;
    const x_eutectic = results.x1_eutectic || results.X1_EUTECTIC || null;

    console.log('📊 ESL T-x - x1_left:', x1_left.length, 'pontos', x1_left.slice(0, 3));
    console.log('📊 ESL T-x - x1_right:', x1_right.length, 'pontos', x1_right.slice(0, 3));
    console.log('📊 ESL T-x - T_left_C:', t_left.length, 'pontos', t_left.slice(0, 3));
    console.log('📊 ESL T-x - T_right_C:', t_right.length, 'pontos', t_right.slice(0, 3));
    console.log('📊 ESL T-x - T_eutectic_C:', T_eutectic);
    console.log('📊 ESL T-x - x1_eutectic:', x_eutectic);

    // ✅ VERIFICAR SE TEM DADOS SUFICIENTES
    if ((x1_left.length === 0 && x1_right.length === 0) || 
        (t_left.length === 0 && t_right.length === 0)) {
        console.error('❌ Dados do diagrama T-x não disponíveis!');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = '16px Arial';
        ctx.fillStyle = '#ef4444';
        ctx.textAlign = 'center';
        ctx.fillText('⚠️ Dados do diagrama T-x não disponíveis', canvas.width / 2, canvas.height / 2);
        return;
    }

    const datasets = [];

    // ✅ CURVA ESQUERDA (Liquidus do componente 1)
    if (x1_left.length > 0 && t_left.length > 0) {
        const leftData = x1_left.map((x, i) => ({
            x: parseFloat(x),
            y: parseFloat(t_left[Math.min(i, t_left.length - 1)])
        })).filter(p => !isNaN(p.x) && !isNaN(p.y));

        leftData.sort((a, b) => a.x - b.x);

        datasets.push({
            label: 'Liquidus (rico em Comp. 1)',
            data: leftData,
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.1)',
            pointRadius: 3,
            pointHoverRadius: 5,
            showLine: true,
            tension: 0.3,
            borderWidth: 2
        });
        
        console.log('✓ Curva esquerda criada:', leftData.length, 'pontos');
    }

    // ✅ CURVA DIREITA (Liquidus do componente 2)
    if (x1_right.length > 0 && t_right.length > 0) {
        const rightData = x1_right.map((x, i) => ({
            x: parseFloat(x),
            y: parseFloat(t_right[Math.min(i, t_right.length - 1)])
        })).filter(p => !isNaN(p.x) && !isNaN(p.y));

        rightData.sort((a, b) => a.x - b.x);

        datasets.push({
            label: 'Liquidus (rico em Comp. 2)',
            data: rightData,
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            pointRadius: 3,
            pointHoverRadius: 5,
            showLine: true,
            tension: 0.3,
            borderWidth: 2
        });
        
        console.log('✓ Curva direita criada:', rightData.length, 'pontos');
    }

    // ✅ PONTO EUTÉTICO
    if (T_eutectic !== null && T_eutectic !== undefined && 
        x_eutectic !== null && x_eutectic !== undefined &&
        !isNaN(T_eutectic) && !isNaN(x_eutectic)) {
        datasets.push({
            label: 'Ponto Eutético',
            data: [{
                x: parseFloat(x_eutectic),
                y: parseFloat(T_eutectic)
            }],
            borderColor: '#f97316',
            backgroundColor: '#f97316',
            pointRadius: 8,
            pointStyle: 'star',
            pointHoverRadius: 10,
            showLine: false
        });
        
        console.log('✅ Ponto eutético adicionado:', x_eutectic, T_eutectic);
    } else {
        console.log('⚠️ Ponto eutético não disponível ou inválido');
    }

    if (datasets.length === 0) {
        console.error('❌ Nenhum dataset criado!');
        return;
    }

    const ctx = canvas.getContext('2d');
    simulationChart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { size: 13 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e5e7eb',
                    bodyColor: '#e5e7eb',
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label === 'Ponto Eutético') {
                                return `Eutético: x₁ = ${context.parsed.x.toFixed(4)}, T = ${context.parsed.y.toFixed(2)} °C`;
                            }
                            return `x₁ = ${context.parsed.x.toFixed(4)}, T = ${context.parsed.y.toFixed(2)} °C`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Fração Molar (x₁)',
                        color: '#94a3b8',
                        font: { size: 13, weight: 'bold' }
                    },
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.15)' },
                    min: 0,
                    max: 1
                },
                y: {
                    title: {
                        display: true,
                        text: 'Temperatura (°C)',
                        color: '#94a3b8',
                        font: { size: 13, weight: 'bold' }
                    },
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.15)' }
                }
            }
        }
    });

    console.log('✅ Gráfico T-x ESL renderizado com', datasets.length, 'curvas');
}

// ========================================================================
// RENDERIZADOR ESL - DIAGRAMA TERNÁRIO (COORDENADAS TRIANGULARES)
// ========================================================================

function renderESLTernaryChart(results) {
    const canvas = document.getElementById('simulationChartCanvas');
    if (!canvas) return;

    if (simulationChart) {
        simulationChart.destroy();
    }

    const points = results.points || [];

    console.log('📊 ESL Ternary - pontos:', points.length);

    if (points.length === 0) {
        console.error('❌ Nenhum ponto encontrado!');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = '16px Arial';
        ctx.fillStyle = '#ef4444';
        ctx.textAlign = 'center';
        ctx.fillText('⚠️ Dados do diagrama ternário não disponíveis', canvas.width / 2, canvas.height / 2);
        return;
    }

    // Conversão para coordenadas triangulares
    const ternaryToCartesian = (x1, x2, x3) => ({
        x: x2 + 0.5 * x3,
        y: (Math.sqrt(3) / 2) * x3
    });

    // Separar pontos por fase
    const liquidPoints = [];
    const solidLiquidPoints = [];

    points.forEach(pt => {
        const cartesian = ternaryToCartesian(pt.x1, pt.x2, pt.x3);
        if (pt.phase === 'liquid') {
            liquidPoints.push(cartesian);
        } else {
            solidLiquidPoints.push(cartesian);
        }
    });

    const datasets = [];

    // Triângulo de fundo
    const triangleVertices = [
        { x: 0, y: 0 },
        { x: 1, y: 0 },
        { x: 0.5, y: Math.sqrt(3)/2 },
        { x: 0, y: 0 }
    ];

    datasets.push({
        label: 'Triângulo',
        data: triangleVertices,
        borderColor: 'rgba(148, 163, 184, 0.5)',
        backgroundColor: 'rgba(148, 163, 184, 0.05)',
        pointRadius: 0,
        showLine: true,
        fill: true,
        borderWidth: 1,
        tension: 0
    });

    // Pontos líquidos
    if (liquidPoints.length > 0) {
        datasets.push({
            label: 'Fase Líquida',
            data: liquidPoints,
            backgroundColor: 'rgba(56, 189, 248, 0.6)',
            pointRadius: 4,
            pointHoverRadius: 6,
            showLine: false
        });
    }

    // Pontos sólido-líquido
    if (solidLiquidPoints.length > 0) {
        datasets.push({
            label: 'Sólido-Líquido',
            data: solidLiquidPoints,
            backgroundColor: 'rgba(249, 115, 22, 0.6)',
            pointRadius: 4,
            pointHoverRadius: 6,
            showLine: false
        });
    }

    const ctx = canvas.getContext('2d');
    simulationChart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { size: 12 },
                        filter: (item) => item.text !== 'Triângulo'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e5e7eb',
                    bodyColor: '#e5e7eb'
                }
            },
            scales: {
                x: {
                    ticks: { display: false },
                    grid: { display: false },
                    min: -0.1,
                    max: 1.1
                },
                y: {
                    ticks: { display: false },
                    grid: { display: false },
                    min: -0.1,
                    max: 1.0
                }
            }
        }
    });

    console.log('✅ Gráfico ternário ESL renderizado');
}

// Exportar histórico
async function exportHistory() {
    try {
        const response = await fetch('/api/dashboard/export');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'historico_simulacoes_' + new Date().toISOString().split('T')[0] + '.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Erro ao exportar:', error);
        alert('Erro ao exportar histórico');
    }
}

// ========================================================================
// RENDERIZADORES DE GRÁFICOS POR MÓDULO
// ========================================================================

function renderELVChart(results, type) {
    // Código existente de renderSimulationChart() - já está funcionando
    renderSimulationChart(results);
}

function renderELLTernaryChart(results) {
    const canvas = document.getElementById('simulationChartCanvas');
    if (!canvas) return;

    if (simulationChart) {
        simulationChart.destroy();
    }

    const binodal_L1 = results.binodal_L1 || [];
    const binodal_L2 = results.binodal_L2 || [];
    const tie_lines = results.tie_lines || [];

    console.log('📊 ELL Ternary - binodal_L1:', binodal_L1.length, 'pontos');
    console.log('📊 ELL Ternary - binodal_L2:', binodal_L2.length, 'pontos');
    console.log('📊 ELL Ternary - tie_lines:', tie_lines.length, 'linhas');

    if (binodal_L1.length === 0 && binodal_L2.length === 0) {
        console.error('❌ Nenhum dado de binodal encontrado!');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = '16px Arial';
        ctx.fillStyle = '#ef4444';
        ctx.textAlign = 'center';
        ctx.fillText('⚠️ Dados de binodal não disponíveis nesta simulação', canvas.width / 2, canvas.height / 2 - 20);
        ctx.fillText('Faça uma nova simulação para gerar o gráfico', canvas.width / 2, canvas.height / 2 + 20);
        return;
    }

    // ✅ FUNÇÃO DE CONVERSÃO: Coordenadas ternárias → Triangulares
    const ternaryToCartesian = (x1, x2, x3) => {
        // Projeção no triângulo equilátero
        return {
            x: x2 + 0.5 * x3,
            y: (Math.sqrt(3) / 2) * x3
        };
    };

    const datasets = [];

    // Binodal L1
    if (Array.isArray(binodal_L1) && binodal_L1.length > 0) {
        const data = binodal_L1.map(point => {
            const [x1, x2, x3] = point;
            return ternaryToCartesian(x1, x2, x3);
        });

        datasets.push({
            label: 'Binodal L1',
            data: data,
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.2)',
            pointRadius: 3,
            pointHoverRadius: 5,
            showLine: true,
            tension: 0.3,
            borderWidth: 2
        });
    }

    // Binodal L2
    if (Array.isArray(binodal_L2) && binodal_L2.length > 0) {
        const data = binodal_L2.map(point => {
            const [x1, x2, x3] = point;
            return ternaryToCartesian(x1, x2, x3);
        });

        datasets.push({
            label: 'Binodal L2',
            data: data,
            borderColor: '#f97316',
            backgroundColor: 'rgba(249, 115, 22, 0.2)',
            pointRadius: 3,
            pointHoverRadius: 5,
            showLine: true,
            tension: 0.3,
            borderWidth: 2
        });
    }

    // Tie-lines
    if (Array.isArray(tie_lines)) {
        tie_lines.forEach((tie, idx) => {
            const [x1_L1, x2_L1, x3_L1] = tie.x_L1;
            const [x1_L2, x2_L2, x3_L2] = tie.x_L2;

            const p1 = ternaryToCartesian(x1_L1, x2_L1, x3_L1);
            const p2 = ternaryToCartesian(x1_L2, x2_L2, x3_L2);

            datasets.push({
                label: `Tie-line ${idx + 1}`,
                data: [p1, p2],
                borderColor: '#a855f7',
                borderDash: [5, 5],
                pointRadius: 4,
                pointHoverRadius: 6,
                showLine: true,
                borderWidth: 2
            });
        });
    }

    // ✅ ADICIONAR TRIÂNGULO DE FUNDO
    const triangleVertices = [
        { x: 0, y: 0 },      // Vértice inferior esquerdo (100% comp 1)
        { x: 1, y: 0 },      // Vértice inferior direito (100% comp 2)
        { x: 0.5, y: Math.sqrt(3)/2 }  // Vértice superior (100% comp 3)
    ];

    datasets.unshift({
        label: 'Triângulo',
        data: [...triangleVertices, triangleVertices[0]], // Fechar o triângulo
        borderColor: 'rgba(148, 163, 184, 0.5)',
        backgroundColor: 'rgba(148, 163, 184, 0.05)',
        pointRadius: 0,
        showLine: true,
        fill: true,
        borderWidth: 1,
        tension: 0
    });

    const ctx = canvas.getContext('2d');
    simulationChart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { size: 12 },
                        filter: (item) => item.text !== 'Triângulo' // Ocultar triângulo da legenda
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#e5e7eb',
                    bodyColor: '#e5e7eb',
                    callbacks: {
                        label: (context) => {
                            if (context.dataset.label === 'Triângulo') return '';
                            return `${context.dataset.label}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: false
                    },
                    ticks: { display: false },
                    grid: { display: false },
                    min: -0.1,
                    max: 1.1
                },
                y: {
                    title: {
                        display: false
                    },
                    ticks: { display: false },
                    grid: { display: false },
                    min: -0.1,
                    max: 1.0
                }
            }
        }
    });

    console.log('✅ Gráfico ternário ELL renderizado (coordenadas triangulares)');
}