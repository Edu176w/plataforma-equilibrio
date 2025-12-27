// Ajustar interface conforme tipo de cálculo
document.getElementById('calculationType').addEventListener('change', function() {
    const type = this.value;
    const tempSection = document.getElementById('tempSection');
    const tempRangeSection = document.getElementById('tempRangeSection');
    
    if (type === 'solubility') {
        tempSection.style.display = 'flex';
        tempRangeSection.style.display = 'none';
    } else if (type === 'eutectic') {
        tempSection.style.display = 'none';
        tempRangeSection.style.display = 'none';
    } else {
        tempSection.style.display = 'none';
        tempRangeSection.style.display = 'block';
    }
});

// Submit do formulário
document.getElementById('eslForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = 'flex';
    
    const type = document.getElementById('calculationType').value;
    const model = document.getElementById('model').value;
    const comp1 = document.getElementById('component1').value;
    const comp2 = document.getElementById('component2').value;
    const components = [comp1, comp2];
    
    let endpoint, data;
    
    if (type === 'solubility') {
        endpoint = '/esl/solubility';
        data = {
            components: components,
            temperature: parseFloat(document.getElementById('temperature').value),
            pressure: parseFloat(document.getElementById('pressure').value),
            solute_idx: 0,
            model: model
        };
    } else if (type === 'eutectic') {
        endpoint = '/esl/eutectic';
        data = {
            components: components,
            model: model
        };
    } else if (type === 'solubility-curve') {
        endpoint = '/esl/solubility-curve';
        data = {
            components: components,
            T_min: parseFloat(document.getElementById('tMin').value),
            T_max: parseFloat(document.getElementById('tMax').value),
            solute_idx: 0,
            n_points: parseInt(document.getElementById('nPoints').value),
            model: model
        };
    } else if (type === 'phase-diagram') {
        endpoint = '/esl/phase-diagram';
        data = {
            components: components,
            T_min: parseFloat(document.getElementById('tMin').value),
            T_max: parseFloat(document.getElementById('tMax').value),
            n_points: parseInt(document.getElementById('nPoints').value),
            model: model
        };
    }
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResultsESL(result.result, type, components);
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        alert('Erro na requisição: ' + error);
    } finally {
        loadingOverlay.style.display = 'none';
    }
});

function displayResultsESL(result, type, components) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');
    
    resultsSection.style.display = 'block';
    
    if (type === 'solubility') {
        let html = '<div class="row">';
        html += '<div class="col-md-4"><div class="result-item">';
        html += '<div class="result-label">Solubilidade</div>';
        html += '<div class="result-value">' + result.solubility.toFixed(6) + '</div>';
        html += '</div></div>';
        html += '<div class="col-md-4"><div class="result-item">';
        html += '<div class="result-label">Temperatura de Fusão</div>';
        html += '<div class="result-value">' + (result.Tm - 273.15).toFixed(2) + ' °C</div>';
        html += '</div></div>';
        html += '<div class="col-md-4"><div class="result-item">';
        html += '<div class="result-label">Entalpia de Fusão</div>';
        html += '<div class="result-value">' + (result.Hfus / 1000).toFixed(2) + ' kJ/mol</div>';
        html += '</div></div>';
        html += '</div>';
        resultsContent.innerHTML = html;
    } else if (type === 'eutectic') {
        let html = '<div class="row">';
        html += '<div class="col-md-6"><div class="result-item">';
        html += '<div class="result-label">Temperatura Eutética</div>';
        html += '<div class="result-value">' + (result.T - 273.15).toFixed(2) + ' °C</div>';
        html += '</div></div>';
        html += '<div class="col-md-6"><div class="result-item">';
        html += '<div class="result-label">Composição Eutética</div>';
        html += '<div class="result-value">x₁=' + result.composition[0].toFixed(4) + ', x₂=' + result.composition[1].toFixed(4) + '</div>';
        html += '</div></div>';
        html += '</div>';
        resultsContent.innerHTML = html;
    } else if (type === 'solubility-curve') {
        resultsContent.innerHTML = '<div class="alert alert-info-custom">Curva de solubilidade gerada com ' + result.T.length + ' pontos</div>';
        plotSolubilityCurve(result, components);
    } else if (type === 'phase-diagram') {
        resultsContent.innerHTML = '<div class="alert alert-info-custom">Diagrama de fases binário gerado</div>';
        plotPhaseDiagram(result, components);
    }
    
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function plotSolubilityCurve(result, components) {
    const trace = {
        x: result.T.map(t => t - 273.15),
        y: result.solubility,
        mode: 'lines+markers',
        name: 'Solubilidade de ' + result.solute,
        line: { color: '#059669', width: 3 }
    };
    
    const layout = {
        title: 'Curva de Solubilidade: ' + result.solute,
        xaxis: { title: 'Temperatura (°C)' },
        yaxis: { title: 'Fração Molar (x)' },
        hovermode: 'closest'
    };
    
    Plotly.newPlot('plotDiv', [trace], layout);
}

function plotPhaseDiagram(result, components) {
    const trace1 = {
        x: result.component1_curve.x,
        y: result.component1_curve.T.map(t => t - 273.15),
        mode: 'lines',
        name: 'Liquidus ' + components[0],
        line: { color: '#2563eb', width: 3 }
    };
    
    const trace2 = {
        x: result.component2_curve.x,
        y: result.component2_curve.T.map(t => t - 273.15),
        mode: 'lines',
        name: 'Liquidus ' + components[1],
        line: { color: '#7c3aed', width: 3 }
    };
    
    const layout = {
        title: 'Diagrama de Fases: ' + components.join(' - '),
        xaxis: { title: 'Fração Molar x₁ (' + components[0] + ')' },
        yaxis: { title: 'Temperatura (°C)' },
        hovermode: 'closest'
    };
    
    Plotly.newPlot('plotDiv', [trace1, trace2], layout);
}

function resetFormESL() {
    document.getElementById('eslForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
}