/* =============================================================================
   EDUCATIONAL.JS - Seção Educacional da Plataforma
   Funcionalidades: glossário interativo, visualizações didáticas, navegação,
                    casos de estudo e carregamento de presets
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    initEducationalPage();
});

function initEducationalPage() {
    console.log('📚 Seção educacional carregada');
    
    // Adicionar animações de entrada nos cards
    animateCards();
    
    // Inicializar tooltips se houver
    initTooltips();
}

/**
 * Anima a entrada dos cards da página
 */
function animateCards() {
    const cards = document.querySelectorAll('.panel, .learning-step, .resource-card');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 80);
    });
}

/**
 * Inicializa tooltips do Bootstrap se disponíveis
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== 'undefined' && tooltipTriggerList.length > 0) {
        [...tooltipTriggerList].map(el => new bootstrap.Tooltip(el));
    }
}

/* =============================================================================
   GLOSSÁRIO INTERATIVO
   ========================================================================== */

const glossaryTerms = {
    'atividade': {
        term: 'Atividade',
        symbol: 'a_i',
        definition: 'Medida da "concentração efetiva" de uma espécie química em uma mistura não-ideal.',
        formula: 'a_i = γ_i · x_i',
        explanation: 'Para sistemas ideais, γ_i = 1 e a atividade é igual à fração molar. Em sistemas não-ideais, o coeficiente de atividade γ_i corrige os desvios da idealidade.',
        applications: ['Cálculos de equilíbrio químico', 'Equilíbrio de fases', 'Eletroquímica'],
        relatedTerms: ['coeficiente-atividade', 'fugacidade', 'fracao-molar']
    },
    'coeficiente-atividade': {
        term: 'Coeficiente de Atividade',
        symbol: 'γ_i',
        definition: 'Fator de correção que quantifica o desvio do comportamento ideal em uma mistura líquida.',
        formula: 'γ_i = a_i / x_i',
        explanation: 'Valores de γ_i > 1 indicam repulsão molecular (desvio positivo), enquanto γ_i < 1 indica atração (desvio negativo). Modelos como NRTL, UNIQUAC e UNIFAC calculam esses coeficientes.',
        applications: ['Destilação de misturas não-ideais', 'Extração líquido-líquido', 'Predição de azeotropia'],
        relatedTerms: ['atividade', 'nrtl', 'uniquac', 'unifac']
    },
    'fugacidade': {
        term: 'Fugacidade',
        symbol: 'f_i',
        definition: 'Medida da "tendência de escape" de uma espécie de uma fase termodinâmica.',
        formula: 'f_i = φ_i · y_i · P (vapor) ou f_i = γ_i · x_i · f_i^sat (líquido)',
        explanation: 'A condição de equilíbrio entre fases é dada pela igualdade das fugacidades: f_i^V = f_i^L. Para gases ideais, a fugacidade é igual à pressão parcial.',
        applications: ['Equilíbrio líquido-vapor', 'Equilíbrio em altas pressões', 'Sistemas supercríticos'],
        relatedTerms: ['atividade', 'coeficiente-fugacidade', 'equilibrio']
    },
    'azeotropia': {
        term: 'Azeotropia',
        symbol: '-',
        definition: 'Fenômeno onde uma mistura líquida evapora sem mudança de composição, formando um azeótropo.',
        formula: 'x_i = y_i para todos os componentes',
        explanation: 'Azeótropos podem ser de mínimo (mais comum) ou máximo ponto de ebulição. Impedem separação completa por destilação simples. Surgem devido a fortes desvios da idealidade.',
        applications: ['Limite de destilação', 'Desidratação azeotrópica', 'Separação por membranas'],
        relatedTerms: ['coeficiente-atividade', 'destilacao', 'diagrama-txy']
    },
    'binodal': {
        term: 'Curva Binodal',
        symbol: '-',
        definition: 'Curva que delimita a região de imiscibilidade em um diagrama de fases líquido-líquido.',
        formula: 'Calculada pela condição: γ_i^I · x_i^I = γ_i^II · x_i^II',
        explanation: 'Dentro da binodal, o sistema separa em duas fases líquidas. Fora dela, há uma única fase líquida homogênea. O topo da binodal é o ponto crítico (plait point).',
        applications: ['Extração líquido-líquido', 'Sistemas ternários', 'Separação de fases'],
        relatedTerms: ['tie-line', 'plait-point', 'ell']
    },
    'tie-line': {
        term: 'Linha de Amarração (Tie-line)',
        symbol: '-',
        definition: 'Linha que conecta as composições de duas fases líquidas em equilíbrio dentro da região binodal.',
        formula: 'Material balance: F = L_I + L_II e z_i · F = x_i^I · L_I + x_i^II · L_II',
        explanation: 'Cada tie-line representa um estado de equilíbrio a uma temperatura específica. A inclinação e comprimento das tie-lines fornecem informações sobre a seletividade da extração.',
        applications: ['Projeto de extratores', 'Diagramas ternários', 'Cálculo de estágios de separação'],
        relatedTerms: ['binodal', 'extracao', 'ell']
    },
    'plait-point': {
        term: 'Ponto Crítico (Plait Point)',
        symbol: '-',
        definition: 'Ponto no topo da curva binodal onde as duas fases líquidas se tornam idênticas.',
        formula: 'x_i^I = x_i^II (composições das duas fases convergem)',
        explanation: 'Também chamado de ponto de consolução. Acima deste ponto (em diagramas de temperatura), o sistema é completamente miscível. É análogo ao ponto crítico vapor-líquido.',
        applications: ['Limite de extração', 'Estudos de miscibilidade', 'Temperatura crítica de solução'],
        relatedTerms: ['binodal', 'temperatura-critica', 'miscibilidade']
    },
    'eutético': {
        term: 'Ponto Eutético',
        symbol: '-',
        definition: 'Composição onde uma mistura solidifica a uma temperatura mínima única, formando um sólido homogêneo.',
        formula: 'T_eutético < T_fusão de qualquer componente puro',
        explanation: 'No ponto eutético, líquido e múltiplas fases sólidas coexistem em equilíbrio. Muito usado em metalurgia, farmacêutica e formação de gelo com sais.',
        applications: ['Cristalização fracionada', 'Formulação de medicamentos', 'Ligas metálicas'],
        relatedTerms: ['esl', 'solubilidade', 'cristalizacao']
    },
    'nrtl': {
        term: 'Modelo NRTL',
        symbol: '-',
        definition: 'Non-Random Two-Liquid - Modelo de composição local para coeficientes de atividade.',
        formula: 'Complexa (veja seção de modelos)',
        explanation: 'Desenvolvido por Renon e Prausnitz (1968). Usa 3 parâmetros binários: τ₁₂, τ₂₁ e α. Excelente para sistemas com LLE devido ao parâmetro de não-aleatoriedade α.',
        applications: ['Sistemas polares', 'Equilíbrio LLE', 'Misturas água-orgânicos'],
        relatedTerms: ['uniquac', 'unifac', 'coeficiente-atividade']
    },
    'uniquac': {
        term: 'Modelo UNIQUAC',
        symbol: '-',
        definition: 'UNIversal QUAsi-Chemical - Modelo semi-empírico baseado em teoria quasi-química.',
        formula: 'ln γ_i = ln γ_i^combinatorial + ln γ_i^residual',
        explanation: 'Desenvolvido por Abrams e Prausnitz (1975). Separa efeitos de tamanho/forma (combinatorial) e energéticos (residual). Usa parâmetros r_i, q_i e τ_ij.',
        applications: ['Misturas com moléculas de tamanhos muito diferentes', 'Sistemas poliméricos', 'VLE e LLE'],
        relatedTerms: ['nrtl', 'unifac', 'coeficiente-atividade']
    },
    'unifac': {
        term: 'Modelo UNIFAC',
        symbol: '-',
        definition: 'UNIQUAC Functional-group Activity Coefficients - Método preditivo de contribuição de grupos.',
        formula: 'Baseado em UNIQUAC, mas usa grupos funcionais',
        explanation: 'Desenvolvido por Fredenslund et al. (1975). Permite estimar propriedades sem dados experimentais, usando tabelas de parâmetros de grupos (CH₃, OH, COOH, etc.).',
        applications: ['Predição de propriedades', 'Screening inicial de solventes', 'Sistemas sem dados experimentais'],
        relatedTerms: ['uniquac', 'grupos-funcionais', 'metodo-preditivo']
    }
};

/**
 * Busca termos do glossário
 */
function searchGlossary(query) {
    const results = [];
    query = query.toLowerCase().trim();
    
    if (!query) return results;
    
    for (const [key, data] of Object.entries(glossaryTerms)) {
        if (data.term.toLowerCase().includes(query) || 
            key.includes(query) ||
            data.definition.toLowerCase().includes(query)) {
            results.push({ key, ...data });
        }
    }
    
    return results;
}

/**
 * Renderiza detalhes de um termo do glossário
 */
function renderGlossaryTerm(termKey) {
    const term = glossaryTerms[termKey];
    if (!term) return '';
    
    return `
        <div class="glossary-term-detail">
            <h4>${term.term} ${term.symbol ? `<span class="term-symbol">(${term.symbol})</span>` : ''}</h4>
            
            <div class="term-section">
                <strong>Definição:</strong>
                <p>${term.definition}</p>
            </div>
            
            <div class="term-section">
                <strong>Formulação:</strong>
                <p class="formula">${term.formula}</p>
            </div>
            
            <div class="term-section">
                <strong>Explicação:</strong>
                <p>${term.explanation}</p>
            </div>
            
            <div class="term-section">
                <strong>Aplicações:</strong>
                <ul>
                    ${term.applications.map(app => `<li>${app}</li>`).join('')}
                </ul>
            </div>
            
            ${term.relatedTerms.length > 0 ? `
                <div class="term-section">
                    <strong>Termos relacionados:</strong>
                    <div class="related-terms">
                        ${term.relatedTerms.map(rel => 
                            `<span class="related-term-badge" onclick="showGlossaryTerm('${rel}')">${glossaryTerms[rel]?.term || rel}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Mostra termo do glossário em modal
 */
function showGlossaryTerm(termKey) {
    const content = renderGlossaryTerm(termKey);
    console.log('Exibindo termo:', termKey);
}

/* =============================================================================
   CASOS DE ESTUDO - DADOS COMPLETOS
   ========================================================================== */

const caseDetails = {
    // ==================== CASOS ELV ====================
    'ethanol-water': {
        id: 'ethanol-water',
        title: 'Etanol-Água',
        module: 'ELV',
        difficulty: 'Intermediário',
        components: ['Ethanol', 'Water'],
        description: 'Sistema azeotrópico clássico usado em destilação de bebidas alcoólicas e bioetanol.',
        objectives: [
            'Identificar azeótropo de mínimo ponto de ebulição',
            'Comparar modelos Ideal vs. UNIQUAC',
            'Entender limitações da destilação simples'
        ],
        conditions: {
            pressure: '107.57 kPa',
            temperature: '80°C (azeótropo)',
            composition: 'x_etanol = 0.894 (azeótropo)'
        },
        model: 'NRTL',
        parameters: {
            'τ₁₂': 0.8009,
            'τ₂₁': 0.50,
            'α': 0.3009
        },
        theory: 'Desvios positivos da idealidade devido a diferenças de polaridade. Ligações de hidrogênio entre moléculas iguais são mais fortes que entre moléculas diferentes.',
        applications: [
            'Destilação de bioetanol',
            'Produção de bebidas destiladas',
            'Destilação azeotrópica',
            'Desidratação com peneiras moleculares'
        ],
        references: [
            'Smith, Van Ness & Abbott - Termodinâmica Química',
            'Perry\'s Chemical Engineers\' Handbook',
            'NIST Chemistry WebBook'
        ]
    },
    
    'benzene-toluene': {
        id: 'benzene-toluene',
        title: 'Benzeno-Tolueno',
        module: 'ELV',
        difficulty: 'Básico',
        components: ['Benzene', 'Toluene'],
        description: 'Sistema ideal clássico usado para introdução à destilação.',
        objectives: [
            'Compreender comportamento ideal (Lei de Raoult)',
            'Calcular volatilidade relativa constante',
            'Desenhar diagrama T-x-y ideal'
        ],
        conditions: {
            pressure: '101.325 kPa',
            temperature: '80-110°C',
            composition: 'Qualquer composição'
        },
        model: 'Ideal',
        parameters: null,
        theory: 'Moléculas quimicamente similares (hidrocarbonetos aromáticos) apresentam comportamento próximo ao ideal. Interações benzeno-benzeno ≈ benzeno-tolueno ≈ tolueno-tolueno.',
        applications: [
            'Separação na indústria petroquímica',
            'Exemplo didático de destilação',
            'Cálculo de estágios teóricos',
            'Validação de métodos numéricos'
        ],
        references: [
            'McCabe-Smith-Harriott - Unit Operations',
            'Seader & Henley - Separation Process Principles'
        ]
    },
    
    'acetone-water': {
        id: 'acetone-water',
        title: 'Acetona-Água',
        module: 'ELV',
        difficulty: 'Intermediário',
        components: ['Acetone', 'Water'],
        description: 'Sistema polar com desvios negativos da idealidade.',
        objectives: [
            'Observar desvios negativos (γ < 1)',
            'Avaliar modelo NRTL para sistemas polares',
            'Analisar miscibilidade completa'
        ],
        conditions: {
            pressure: '101.325 kPa',
            temperature: '56-100°C',
            composition: 'Completamente miscível'
        },
        model: 'NRTL',
        parameters: {
            'τ₁₂': 230.99,
            'τ₂₁': -100.71,
            'α': 0.3020
        },
        theory: 'Ligações de hidrogênio entre acetona (aceitador) e água (doador) são mais fortes que interações entre moléculas iguais, causando desvios negativos.',
        applications: [
            'Recuperação de acetona em processos químicos',
            'Solvente em indústria farmacêutica',
            'Síntese orgânica'
        ],
        references: [
            'Gmehling & Kolbe - Thermodynamik',
            'DECHEMA Data Series'
        ]
    },
    
    'methanol-benzene': {
        id: 'methanol-benzene',
        title: 'Metanol-Benzeno',
        module: 'ELV',
        difficulty: 'Avançado',
        components: ['Methanol', 'Benzene'],
        description: 'Sistema com azeótropo e forte não-idealidade devido a diferenças de polaridade.',
        objectives: [
            'Identificar azeótropo em x = 0.395',
            'Analisar desvios positivos extremos',
            'Comparar modelos NRTL vs. UNIQUAC'
        ],
        conditions: {
            pressure: '215.59 kPa',
            temperature: '80°C (azeótropo)',
            composition: 'x_metanol = 0.714 (azeótropo)'
        },
        model: 'NRTL',
        parameters: {
            'τ₁₂': 523.71,
            'τ₂₁': 151.83,
            'α': 0.2987
        },
        theory: 'Interação polar-apolar resulta em forte repulsão. Metanol forma auto-associações por ligações H, enquanto benzeno é completamente apolar.',
        applications: [
            'Separação em refinarias',
            'Processos de purificação',
            'Exemplo de separação complexa'
        ],
        references: [
            'Prausnitz et al. - Molecular Thermodynamics',
            'Industrial & Engineering Chemistry Research'
        ]
    },
    
    // ==================== CASOS ELL ====================
    'water-butanol-acetone': {
        id: 'water-butanol-acetone',
        title: 'Água-1-Butanol-Acetona',
        module: 'ELL',
        difficulty: 'Intermediário',
        components: ['Water', '1-Butanol', 'Acetone'],
        description: 'Sistema ternário com imiscibilidade parcial. Acetona atua como co-solvente.',
        objectives: [
            'Traçar diagrama ternário com binodal',
            'Calcular tie-lines',
            'Entender papel do co-solvente'
        ],
        conditions: {
            temperature: '25°C (298.15 K)',
            composition: 'Região de duas fases',
            feedComposition: '[0.4, 0.3, 0.3]'
        },
        model: 'NRTL',
        parameters: {
            'τ₁₂ (H₂O-BuOH)': '4.514',
            'τ₂₁ (BuOH-H₂O)': '0.158',
            'τ₁₃ (H₂O-Acetone)': '1.674',
            'τ₃₁ (Acetone-H₂O)': '0.783',
            'τ₂₃ (BuOH-Acetone)': '-0.236',
            'τ₃₂ (Acetone-BuOH)': '0.289',
            'α (não-aleatoriedade)': '0.20-0.30'
        },
        theory: 'Água e butanol são parcialmente miscíveis. Acetona aumenta a miscibilidade atuando como co-solvente, reduzindo a região de duas fases.',
        applications: [
            'Extração líquido-líquido',
            'Recuperação de solventes',
            'Purificação de produtos químicos'
        ],
        references: [
            'Santos et al. (2001) - Fluid Phase Equilibria 187, 265-274',
            'Treybal (1963) - Liquid Extraction',
            'J. Chem. Eng. Data (2022) 67(6), 1495-1504'
        ]
    },

    'water-chloroform-aceticacid': {
        id: 'water-chloroform-aceticacid',
        title: 'Água-Clorofórmio-Ácido Acético',
        module: 'ELL',
        difficulty: 'Avançado',
        components: ['Water', 'Chloroform', 'Acetic Acid'],
        description: 'Sistema com distribuição de ácido acético entre fases aquosa e orgânica.',
        objectives: [
            'Calcular coeficientes de distribuição',
            'Avaliar seletividade da extração',
            'Aplicar modelo UNIQUAC'
        ],
        conditions: {
            temperature: '25°C (298.15 K)',
            composition: 'Tie-lines a 25°C',
            feedComposition: '[0.5, 0.3, 0.2]'
        },
        model: 'UNIQUAC',
        parameters: {
            'u₁₂ (H₂O-CHCl₃)': '548.31 K',
            'u₂₁ (CHCl₃-H₂O)': '86.54 K',
            'u₁₃ (H₂O-AcOH)': '-45.12 K',
            'u₃₁ (AcOH-H₂O)': '234.67 K',
            'u₂₃ (CHCl₃-AcOH)': '-112.34 K',
            'u₃₂ (AcOH-CHCl₃)': '98.23 K'
        },
        theory: 'Ácido acético se distribui entre as fases. Dimerização na fase orgânica complica o equilíbrio. UNIQUAC é preferível devido a diferenças de tamanho molecular.',
        applications: [
            'Extração de ácidos orgânicos',
            'Processos de purificação',
            'Recuperação de produtos fermentativos'
        ],
        references: [
            'Moura & Santos (2012) - Am. J. Phys. Chem. 1(5), 96-101',
            'Robbins (1997) - Liquid-Liquid Extraction',
            'AIChE Journal 53(8), 2112-2121'
        ]
    },

    'water-toluene-aniline': {
        id: 'water-toluene-aniline',
        title: 'Água-Tolueno-Anilina',
        module: 'ELL',
        difficulty: 'Avançado',
        components: ['Water', 'Toluene', 'Aniline'],
        description: 'Sistema ternário complexo com plait point bem definido.',
        objectives: [
            'Localizar plait point',
            'Calcular múltiplas tie-lines',
            'Analisar efeito da temperatura'
        ],
        conditions: {
            temperature: '25°C (298.15 K)',
            composition: 'Região binodal ampla',
            feedComposition: '[0.45, 0.35, 0.2]'
        },
        model: 'NRTL',
        parameters: {
            'τ₁₂ (H₂O-Toluene)': '8.432',
            'τ₂₁ (Toluene-H₂O)': '5.678',
            'τ₁₃ (H₂O-Aniline)': '2.891',
            'τ₃₁ (Aniline-H₂O)': '1.234',
            'τ₂₃ (Toluene-Aniline)': '-0.156',
            'τ₃₂ (Aniline-Toluene)': '0.423',
            'α (não-aleatoriedade)': '0.20-0.47'
        },
        theory: 'Anilina é anfifílica (grupo NH₂ polar + anel aromático apolar), tendo afinidade por ambas as fases.',
        applications: [
            'Extração de anilina',
            'Processos de síntese orgânica',
            'Purificação de aromáticos'
        ],
        references: [
            'Grenner et al. (2006) - J. Chem. Eng. Data 51(3), 1009-1014',
            'Null (1970) - Phase Equilibrium in Process Design',
            'Fluid Phase Equilibria 260(2), 279-294'
        ]
    },

    
    // ==================== CASOS ESL ====================
    'naphthalene-benzene': {
        id: 'naphthalene-benzene',
        title: 'Naftaleno-Benzeno',
        module: 'ESL',
        difficulty: 'Básico',
        components: ['Naphthalene', 'Benzene'],
        description: 'Sistema ideal sólido-líquido com ponto eutético simples.',
        objectives: [
            'Identificar ponto eutético',
            'Aplicar equação de solubilidade ideal',
            'Calcular curvas de liquidus'
        ],
        conditions: {
            temperature: '0°C',
            composition: 'x_naftaleno ≈ 0.3 (eutético)',
            pressure: 'Atmosférica'
        },
        model: 'Ideal',
        parameters: null,
        theory: 'Compostos aromáticos similares formam solução sólida ideal. Ponto eutético ocorre onde ambos os sólidos cristalizam simultaneamente.',
        applications: [
            'Purificação por cristalização',
            'Separação de aromáticos',
            'Produção de naftaleno puro'
        ],
        references: [
            'Findlay - Phase Rule',
            'CRC Handbook of Chemistry and Physics'
        ]
    },
    
    'water-nacl': {
        id: 'water-nacl',
        title: 'Água-Cloreto de Sódio',
        module: 'ESL',
        difficulty: 'Intermediário',
        components: ['Water', 'Sodium Chloride'],
        description: 'Solubilidade de sal em água. Importante para cristalização e evaporação.',
        objectives: [
            'Calcular solubilidade em função da temperatura',
            'Aplicar equação de van\'t Hoff',
            'Desenhar curva de solubilidade'
        ],
        conditions: {
            temperature: '25°C',
            composition: '23.3% massa (saturação)',
            pressure: 'Atmosférica'
        },
        model: 'Ideal',
        parameters: null,
        theory: 'Solubilidade de NaCl varia pouco com temperatura. Cristaliza como NaCl·2H₂O a baixas temperaturas.',
        applications: [
            'Produção de sal por evaporação',
            'Salmouras industriais',
            'Processos de dessalinização'
        ],
        references: [
            'Mullin - Crystallization',
            'Solubility Data Series - IUPAC'
        ]
    },
    
    'phenol-water': {
        id: 'phenol-water',
        title: 'Fenol-Água',
        module: 'ESL',
        difficulty: 'Avançado',
        components: ['Phenol', 'Water'],
        description: 'Sistema com miscibilidade parcial no estado líquido e sólido-líquido.',
        objectives: [
            'Analisar solubilidade mútua',
            'Identificar temperatura crítica de solução',
            'Aplicar NRTL para fase sólida'
        ],
        conditions: {
            temperature: '20°C',
            composition: 'Parcialmente miscível',
            pressure: 'Atmosférica'
        },
        model: 'NRTL',
        parameters: {
            'τ₁₂': 3.4567,
            'τ₂₁': 1.2345,
            'α': 0.3
        },
        theory: 'Fenol e água formam sistema com UCST (Upper Critical Solution Temperature) ≈ 66°C. Abaixo disso, há imiscibilidade parcial.',
        applications: [
            'Purificação de fenol',
            'Processos de extração',
            'Recuperação de fenol de efluentes'
        ],
        references: [
            'Walas - Phase Equilibria in Chemical Engineering',
            'Industrial & Engineering Chemistry'
        ]
    }
};

/* =============================================================================
   FUNÇÕES DE CASOS DE ESTUDO
   ========================================================================== */

/**
 * Abre modal com detalhes completos do caso de estudo
 */
function viewCaseDetails(caseId) {
    const caseData = caseDetails[caseId];
    
    if (!caseData) {
        console.error('Caso não encontrado:', caseId);
        showNotification('Caso de estudo não encontrado', 'error');
        return;
    }
    
    console.log('📖 Exibindo detalhes do caso:', caseData.title);
    
    // Construir HTML do modal COM Z-INDEX MAIOR
    const modalHTML = `
        <div class="case-detail-modal-backdrop" id="caseDetailBackdrop" onclick="closeCaseDetails()" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(8px); z-index: 999999; display: flex; align-items: center; justify-content: center; padding: 2rem; opacity: 0; transition: opacity 0.3s ease;">
            <div class="case-detail-modal" onclick="event.stopPropagation()" style="background: #1e293b; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 16px; max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5); animation: modalSlideIn 0.3s ease;">
                <!-- Cabeçalho -->
                <div class="case-modal-header" style="display: flex; justify-content: space-between; align-items: flex-start; padding: 1.5rem; border-bottom: 1px solid rgba(148, 163, 184, 0.2); background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(56, 189, 248, 0.05));">
                    <div>
                        <h3 style="font-size: 1.5rem; font-weight: 700; color: #e5e7eb; margin: 0 0 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="bi bi-book"></i>
                            ${caseData.title}
                        </h3>
                        <div class="case-modal-badges" style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                            <span class="badge" style="display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; background: rgba(37, 99, 235, 0.2); color: #60a5fa;">${caseData.module}</span>
                            <span class="badge" style="display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; background: rgba(245, 158, 11, 0.2); color: #fcd34d;">${caseData.difficulty}</span>
                        </div>
                    </div>
                    <button class="btn-close-modal" onclick="closeCaseDetails()" style="background: transparent; border: none; color: #94a3b8; font-size: 1.5rem; cursor: pointer; padding: 0.5rem; transition: color 0.2s ease; line-height: 1;">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                
                <!-- Corpo -->
                <div class="case-modal-body" style="padding: 1.5rem;">
                    <!-- Descrição -->
                    <div class="case-section" style="margin-bottom: 1.5rem;">
                        <h5 style="font-size: 1.1rem; font-weight: 700; color: #e5e7eb; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;"><i class="bi bi-info-circle"></i> Descrição</h5>
                        <p style="color: #cbd5e1; line-height: 1.6; margin-bottom: 0.5rem;">${caseData.description}</p>
                    </div>
                    
                    <!-- Objetivos -->
                    <div class="case-section" style="margin-bottom: 1.5rem;">
                        <h5 style="font-size: 1.1rem; font-weight: 700; color: #e5e7eb; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;"><i class="bi bi-bullseye"></i> Objetivos de Aprendizagem</h5>
                        <ul class="objectives-list" style="list-style: none; padding: 0; margin: 0;">
                            ${caseData.objectives.map(obj => `<li style="padding: 0.5rem 0 0.5rem 1.5rem; color: #cbd5e1; position: relative; border-bottom: 1px solid rgba(148, 163, 184, 0.1);"><span style="position: absolute; left: 0; color: #22c55e; font-weight: bold;">✓</span>${obj}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <!-- Condições -->
                    <div class="case-section" style="margin-bottom: 1.5rem;">
                        <h5 style="font-size: 1.1rem; font-weight: 700; color: #e5e7eb; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;"><i class="bi bi-thermometer-half"></i> Condições Operacionais</h5>
                        <div class="conditions-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 0.8rem;">
                            ${Object.entries(caseData.conditions).map(([key, value]) => `
                                <div class="condition-item" style="background: rgba(15, 23, 42, 0.5); padding: 0.8rem; border-radius: 8px; border-left: 3px solid #38bdf8;">
                                    <span class="condition-label" style="display: block; font-size: 0.8rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem;">${key.replace(/([A-Z])/g, ' $1').trim()}:</span>
                                    <span class="condition-value" style="display: block; font-size: 1rem; color: #e5e7eb; font-weight: 500;">${value}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <!-- Modelo e Parâmetros -->
                    <div class="case-section" style="margin-bottom: 1.5rem;">
                        <h5 style="font-size: 1.1rem; font-weight: 700; color: #e5e7eb; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;"><i class="bi bi-gear"></i> Modelo Termodinâmico</h5>
                        <p style="color: #cbd5e1;"><strong>Modelo:</strong> ${caseData.model}</p>
                        ${caseData.parameters ? `
                            <div class="parameters-box" style="background: rgba(15, 23, 42, 0.5); border-radius: 8px; padding: 1rem; border: 1px solid rgba(148, 163, 184, 0.2);">
                                <strong style="color: #e5e7eb;">Parâmetros:</strong>
                                <ul class="parameters-list" style="list-style: none; padding: 0; margin: 0.5rem 0 0 0;">
                                    ${Object.entries(caseData.parameters).map(([key, value]) => `
                                        <li style="padding: 0.4rem 0; color: #cbd5e1; font-size: 0.9rem;"><code style="background: rgba(56, 189, 248, 0.15); color: #7dd3fc; padding: 0.2rem 0.5rem; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.85rem;">${key}</code> = ${value}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : '<p style="color: #94a3b8;"><em>Modelo não requer parâmetros binários</em></p>'}
                    </div>
                    
                    <!-- Teoria -->
                    <div class="case-section" style="margin-bottom: 1.5rem;">
                        <h5 style="font-size: 1.1rem; font-weight: 700; color: #e5e7eb; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;"><i class="bi bi-lightbulb"></i> Fundamentação Teórica</h5>
                        <p style="color: #cbd5e1; line-height: 1.6;">${caseData.theory}</p>
                    </div>
                    
                    <!-- Aplicações -->
                    <div class="case-section" style="margin-bottom: 1.5rem;">
                        <h5 style="font-size: 1.1rem; font-weight: 700; color: #e5e7eb; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;"><i class="bi bi-briefcase"></i> Aplicações Industriais</h5>
                        <ul class="applications-list" style="list-style: none; padding: 0; margin: 0;">
                            ${caseData.applications.map(app => `<li style="padding: 0.5rem 0 0.5rem 1.5rem; color: #cbd5e1; position: relative; border-bottom: 1px solid rgba(148, 163, 184, 0.1);"><span style="position: absolute; left: 0; color: #38bdf8;">→</span>${app}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <!-- Referências -->
                    <div class="case-section">
                        <h5 style="font-size: 1.1rem; font-weight: 700; color: #e5e7eb; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;"><i class="bi bi-journal-text"></i> Referências</h5>
                        <ul class="references-list" style="list-style: none; padding: 0; margin: 0;">
                            ${caseData.references.map(ref => `<li style="padding: 0.5rem 0 0.5rem 1.5rem; color: #cbd5e1; position: relative; border-bottom: 1px solid rgba(148, 163, 184, 0.1);"><span style="position: absolute; left: 0;">📚</span>${ref}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                
                <!-- Rodapé com ações -->
                <div class="case-modal-footer" style="padding: 1.2rem 1.5rem; border-top: 1px solid rgba(148, 163, 184, 0.2); display: flex; justify-content: flex-end; gap: 0.8rem; background: rgba(15, 23, 42, 0.3);">
                    <button class="btn-modal btn-secondary" onclick="closeCaseDetails()" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.7rem 1.5rem; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; background: rgba(148, 163, 184, 0.2); color: #cbd5e1;">
                        <i class="bi bi-x-circle"></i> Fechar
                    </button>
                    <button class="btn-modal btn-primary" onclick="loadCase('${caseId}')" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.7rem 1.5rem; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; background: linear-gradient(135deg, #2563eb, #3b82f6); color: white;">
                        <i class="bi bi-play-fill"></i> Simular no ${caseData.module}
                    </button>
                </div>
            </div>
        </div>
        
        <style>
            @keyframes modalSlideIn {
                from {
                    transform: translateY(-30px) scale(0.95);
                    opacity: 0;
                }
                to {
                    transform: translateY(0) scale(1);
                    opacity: 1;
                }
            }
            
            .case-detail-modal::-webkit-scrollbar {
                width: 8px;
            }
            
            .case-detail-modal::-webkit-scrollbar-track {
                background: rgba(15, 23, 42, 0.5);
                border-radius: 10px;
            }
            
            .case-detail-modal::-webkit-scrollbar-thumb {
                background: rgba(56, 189, 248, 0.5);
                border-radius: 10px;
            }
            
            .case-detail-modal::-webkit-scrollbar-thumb:hover {
                background: rgba(56, 189, 248, 0.7);
            }
            
            .btn-modal:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
            }
        </style>
    `;
    
    // Inserir modal DIRETAMENTE NO BODY (não em container)
    const existingModal = document.getElementById('caseDetailBackdrop');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Inserir no body (garantindo que está no topo da hierarquia)
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Animação de entrada
    setTimeout(() => {
        const backdrop = document.getElementById('caseDetailBackdrop');
        if (backdrop) {
            backdrop.style.opacity = '1';
        }
    }, 10);
}


/**
 * Fecha modal de detalhes do caso
 */
function closeCaseDetails() {
    const backdrop = document.getElementById('caseDetailBackdrop');
    if (backdrop) {
        backdrop.style.opacity = '0';
        setTimeout(() => backdrop.remove(), 300);
    }
}

/**
 * Carrega um caso de estudo no módulo apropriado
 */
function loadCase(caseId) {
    console.log('🚀 Carregando caso de estudo:', caseId);
    
    const caseData = caseDetails[caseId];
    if (!caseData) {
        console.error('Caso não encontrado:', caseId);
        showNotification('Caso de estudo não encontrado', 'error');
        return;
    }
    
    // Fechar modal de detalhes
    closeCaseDetails();
    
    // Mapear caso para módulo
    const moduleRoutes = {
        'ELV': '/elv/calculator',
        'ELL': '/ell/calculator',
        'ESL': '/esl/calculator'
    };
    
    const baseUrl = moduleRoutes[caseData.module];
    if (!baseUrl) {
        console.error('Módulo não encontrado:', caseData.module);
        return;
    }
    
    // Redirecionar com preset
    window.location.href = `${baseUrl}?preset=${caseId}`;
}


/* =============================================================================
   NAVEGAÇÃO E UTILIDADES
   ========================================================================== */

/**
 * Navega para uma seção específica com scroll suave
 */
function navigateToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Copia equação para clipboard
 */
function copyEquation(equation) {
    navigator.clipboard.writeText(equation).then(() => {
        showNotification('Equação copiada!', 'success');
    }).catch(err => {
        console.error('Erro ao copiar:', err);
    });
}

/**
 * Mostra notificação temporária
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `educational-notification ${type}`;
    notification.textContent = message;
    
    const bgColor = type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#38bdf8';
    
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 12px 20px;
        background: ${bgColor};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        font-weight: 500;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 2500);
}

// Fechar modal ao pressionar ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeCaseDetails();
    }
});

// Exportar funções globais
window.educationalJS = {
    searchGlossary,
    renderGlossaryTerm,
    showGlossaryTerm,
    navigateToSection,
    copyEquation,
    glossaryTerms,
    caseDetails,
    viewCaseDetails,
    closeCaseDetails,
    loadCase
};
