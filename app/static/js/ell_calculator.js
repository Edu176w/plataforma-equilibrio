// Auto-ajustar composições
function updateCompositions() {
    const z1 = parseFloat(document.getElementById('z1').value) || 0;
    const z2 = parseFloat(document.getElementById('z2').value) || 0;
    const z3 = 1 - z1 - z2;
    document.getElementById('z3').value = z3.toFixed(3);
}

document.getElementById('z1').addEventListener('input', updateCompositions);
document.getElementById('z2').addEventListener('input', updateCompositions);

// Ajustar interface conforme tipo de cálculo
document.getElementById('calculationType').addEventListener('change', function() {
    const type = this.value;
    const compositionSection = document.getElementById('compositionSection');
    
    if (type === 'lle' || type === 'stability') {
        compositionSection.style.display = 'block';
    } else {
        compositionSection.style.display = 'none';
    }
});

// Submit do formulário
document.getElementById('ellForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const loadingOverlay = document.getElementById('loadingOverlay');
    loadingOverlay.style.display = 'flex';
    
    const type = document.getElementById('calculationType').value;
    const model = document.getElementById('model').value;
    
    const comp1 = document.getElementById('component1').value;
    const comp2 = document.getElementById('component2').value;
    const comp3 = document.getElementById('component3').value;
    
    const components = [comp1, comp2, comp3];
    
    const T = parseFloat(document.getElementById('temperature').value);
    const P = parseFloat(document.getElementById('pressure').value);
    
    let endpoint, data;
    
    if (type === 'lle') {
        endpoint = '/ell/calculate';
        const z1 = parseFloat(document.getElementById('z1').value);
        const z2 = parseFloat(document.getElementById('z2').value);
        const z3 = parseFloat(document.getElementById('z3').value);
        
        data = {
            components: components,
            z: [z1, z2, z3],
            temperature: T,
            pressure: P,
            model: model
        };
    } else if (type === 'stability') {
        endpoint = '/ell/stability';
        const z1 = parseFloat(document.getElementById('z1').value);
        const z2 = parseFloat(document.getElementById('z2').value);
        const z3 = parseFloat(document.getElementById('z3').value);
        
        data = {
            components: components,
            z: [z1, z2, z3],
            temperature: T,
            pressure: P,
            model: model
        };
    } else if (type === 'binodal') {
        endpoint = '/ell/binodal';
        data = {
            components: [comp1, comp2],
            temperature: T,
            pressure: P,
            model: model,
            n_points: 30
        };
    } else if (type === 'ternary') {
        endpoint = '/ell/ternary';
        data = {
            components: components,
            temperature: T,
            pressure: P,
            model: model,
            n_points: 20
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
            displayResultsELL(result.result, type, components);
        } else {
            alert('Erro: ' + result.error);
        }
    } catch (error) {
        alert('Erro na requisição: ' + error);
    } finally {
        loadingOverlay.style.display = 'none';
    }
});

function displayResultsELL(result, type, components) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');
    
    resultsSection.style.display = 'block';
    
    if (type === 'lle') {
        if (result.stable) {
            resultsContent.innerHTML = '<div class="alert alert-success-custom"><strong>Sistema Monofásico</strong></div>';
        } else {
            let html = '<div class="alert alert-info-custom"><strong>Sistema Bifásico</strong></div>';
            html += '<div class="row">';
            html += '<div class="col-md-6"><div class="result-item">';
            html += '<div class="result-label">Fase 1</div>';
            html += '<div class="result-value">' + result.phase1.map((x, i) => 'x' + (i+1) + '=' + x.toFixed(4)).join(', ') + '</div>';
            html += '</div></div>';
            html += '<div class="col-md-6"><div class="result-item">';
            html += '<div class="result-label">Fase 2</div>';
            html += '<div class="result-value">' + result.phase2.map((x, i) => 'x' + (i+1) + '=' + x.toFixed(4)).join(', ') + '</div>';
            html += '</div></div>';
            html += '</div>';
            resultsContent.innerHTML = html;
        }
    } else if (type === 'stability') {
        resultsContent.innerHTML = '<div class="alert alert-info-custom">' + result.message + '</div>';
    } else if (type === 'ternary') {
        resultsContent.innerHTML = '<div class="alert alert-info-custom">Diagrama ternário gerado</div>';
        plotTernaryDiagram(result, components);
    }
    
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function plotTernaryDiagram(result, components) {
    const stableX = result.stable_points.map(p => p[0] + 0.5 * p[2]);
    const stableY = result.stable_points.map(p => (Math.sqrt(3) / 2) * p[2]);
    
    const unstableX = result.unstable_points.map(p => p[0] + 0.5 * p[2]);
    const unstableY = result.unstable_points.map(p => (Math.sqrt(3) / 2) * p[2]);
    
    const trace1 = {
        x: stableX,
        y: stableY,
        mode: 'markers',
        name: 'Monofásico',
        marker: { size: 6, color: '#059669' }
    };
    
    const trace2 = {
        x: unstableX,
        y: unstableY,
        mode: 'markers',
        name: 'Bifásico',
        marker: { size: 6, color: '#dc2626' }
    };
    
    const triangle = {
        x: [0, 1, 0.5, 0],
        y: [0, 0, Math.sqrt(3)/2, 0],
        mode: 'lines',
        name: 'Limite',
        line: { color: 'black', width: 2 }
    };
    
    const layout = {
        title: 'Diagrama Ternário: ' + components.join(' - '),
        xaxis: { showgrid: false, zeroline: false, showticklabels: false },
        yaxis: { showgrid: false, zeroline: false, showticklabels: false, scaleanchor: 'x' },
        hovermode: 'closest'
    };
    
    Plotly.newPlot('plotDiv', [triangle, trace1, trace2], layout);
}

function resetFormELL() {
    document.getElementById('ellForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
}