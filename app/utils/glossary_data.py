"""
Dados do glossário termodinâmico
Centraliza todos os termos técnicos usados na plataforma
"""

GLOSSARY_TERMS = {
    'atividade': {
        'term': 'Atividade',
        'symbol': 'a_i',
        'category': 'Propriedades Termodinâmicas',
        'definition': 'Medida da "concentração efetiva" de uma espécie química em uma mistura não-ideal.',
        'formula': 'a_i = γ_i · x_i',
        'explanation': 'Para sistemas ideais, γ_i = 1 e a atividade é igual à fração molar. Em sistemas não-ideais, o coeficiente de atividade γ_i corrige os desvios da idealidade causados por interações moleculares específicas.',
        'applications': [
            'Cálculos de equilíbrio químico',
            'Equilíbrio de fases líquido-vapor',
            'Eletroquímica e potencial químico'
        ],
        'related_terms': ['coeficiente-atividade', 'fugacidade', 'fracao-molar'],
        'reference': 'Smith et al. (2007), Cap. 11'
    },
    
    'coeficiente-atividade': {
        'term': 'Coeficiente de Atividade',
        'symbol': 'γ_i',
        'category': 'Propriedades Termodinâmicas',
        'definition': 'Fator de correção que quantifica o desvio do comportamento ideal em uma mistura líquida.',
        'formula': 'γ_i = a_i / x_i = f_i / (x_i · f_i°)',
        'explanation': 'Valores de γ_i > 1 indicam repulsão molecular (desvio positivo da Lei de Raoult), enquanto γ_i < 1 indica atração entre moléculas diferentes (desvio negativo). Modelos como NRTL, UNIQUAC e UNIFAC são usados para calcular esses coeficientes.',
        'applications': [
            'Destilação de misturas não-ideais',
            'Predição de azeotropia',
            'Extração líquido-líquido',
            'Cálculos de solubilidade'
        ],
        'related_terms': ['atividade', 'nrtl', 'uniquac', 'unifac', 'azeotropia'],
        'reference': 'Prausnitz et al. (1999), Cap. 6'
    },
    
    'fugacidade': {
        'term': 'Fugacidade',
        'symbol': 'f_i',
        'category': 'Propriedades Termodinâmicas',
        'definition': 'Medida da "tendência de escape" de uma espécie de uma fase termodinâmica. Generalização termodinâmica da pressão parcial.',
        'formula': 'f_i^V = φ_i · y_i · P (vapor)\nf_i^L = γ_i · x_i · f_i^sat (líquido)',
        'explanation': 'A condição de equilíbrio entre fases é expressa pela igualdade das fugacidades: f_i^V = f_i^L. Para gases ideais a baixa pressão, a fugacidade é numericamente igual à pressão parcial. O coeficiente de fugacidade φ_i corrige desvios da fase vapor.',
        'applications': [
            'Equilíbrio líquido-vapor (ELV)',
            'Equilíbrio em altas pressões',
            'Sistemas supercríticos',
            'Flash isotérmico e adiabático'
        ],
        'related_terms': ['atividade', 'coeficiente-fugacidade', 'equilibrio', 'pressao-vapor'],
        'reference': 'Smith et al. (2007), Cap. 10-11'
    },
    
    'azeotropia': {
        'term': 'Azeotropia',
        'symbol': '-',
        'category': 'Fenômenos de Fase',
        'definition': 'Fenômeno onde uma mistura líquida evapora sem mudança de composição, formando um azeótropo que se comporta como pseudo-componente puro.',
        'formula': 'x_i = y_i para todos os componentes\nγ_1 · P_1^sat = γ_2 · P_2^sat',
        'explanation': 'Azeótropos podem ser de mínimo (mais comum, ex: etanol-água a 78.2°C) ou máximo ponto de ebulição. Surgem devido a fortes desvios da idealidade (γ_i muito diferente de 1). Impedem separação completa por destilação simples convencional.',
        'applications': [
            'Limite teórico de destilação',
            'Desidratação azeotrópica',
            'Destilação extrativa',
            'Separação por membranas'
        ],
        'related_terms': ['coeficiente-atividade', 'destilacao', 'diagrama-txy', 'desvio-idealidade'],
        'reference': 'Seider et al. (2017), Cap. 4'
    },
    
    'binodal': {
        'term': 'Curva Binodal',
        'symbol': '-',
        'category': 'Equilíbrio Líquido-Líquido',
        'definition': 'Curva que delimita a região de imiscibilidade (separação de fases) em um diagrama de equilíbrio líquido-líquido.',
        'formula': 'Calculada pela condição de iso-atividade:\nγ_i^I · x_i^I = γ_i^II · x_i^II',
        'explanation': 'Dentro da região binodal, o sistema termodinamicamente favorável é bifsico (duas fases líquidas em equilíbrio). Fora dela, existe uma única fase líquida homogênea. O topo da binodal é o ponto crítico de solução (plait point), onde as duas fases se tornam idênticas.',
        'applications': [
            'Projeto de extratores líquido-líquido',
            'Diagramas ternários de extração',
            'Determinação de regiões de miscibilidade',
            'Separação de fases imiscíveis'
        ],
        'related_terms': ['tie-line', 'plait-point', 'ell', 'extracao', 'miscibilidade'],
        'reference': 'Treybal (1980), Cap. 8'
    },
    
    'tie-line': {
        'term': 'Linha de Amarração (Tie-line)',
        'symbol': '-',
        'category': 'Equilíbrio Líquido-Líquido',
        'definition': 'Linha reta que conecta as composições de duas fases líquidas em equilíbrio dentro da região binodal de um diagrama ternário.',
        'formula': 'Balanço material:\nF = L^I + L^II\nz_i · F = x_i^I · L^I + x_i^II · L^II',
        'explanation': 'Cada tie-line representa um estado de equilíbrio a temperatura e pressão fixas. A inclinação da tie-line fornece informação sobre seletividade da extração. Tie-lines mais inclinadas indicam maior seletividade. O comprimento está relacionado à diferença de composição entre as fases.',
        'applications': [
            'Projeto de colunas de extração',
            'Cálculo de número de estágios teóricos',
            'Determinação de seletividade',
            'Balanço material em extratores'
        ],
        'related_terms': ['binodal', 'extracao', 'ell', 'seletividade', 'diagrama-ternario'],
        'reference': 'Treybal (1980), Cap. 8'
    },
    
    'plait-point': {
        'term': 'Ponto Crítico de Solução (Plait Point)',
        'symbol': '-',
        'category': 'Equilíbrio Líquido-Líquido',
        'definition': 'Ponto no topo da curva binodal onde as duas fases líquidas em equilíbrio se tornam idênticas em composição.',
        'formula': 'No plait point:\nx_i^I = x_i^II (todas as composições)\nγ_i^I = γ_i^II (todos os coeficientes)',
        'explanation': 'Também chamado de ponto de consolução superior ou inferior. Acima da temperatura do plait point superior, o sistema torna-se completamente miscível (fase única). É análogo ao ponto crítico no equilíbrio líquido-vapor. A tie-line no plait point tem comprimento zero.',
        'applications': [
            'Limite superior de operação de extratores',
            'Estudos de miscibilidade parcial',
            'Determinação de temperatura crítica de solução',
            'Fenômenos de separação de fases'
        ],
        'related_terms': ['binodal', 'temperatura-critica', 'miscibilidade', 'ell'],
        'reference': 'Sandler (2006), Cap. 9'
    },
    
    'eutético': {
        'term': 'Ponto Eutético',
        'symbol': '-',
        'category': 'Equilíbrio Sólido-Líquido',
        'definition': 'Composição e temperatura onde uma mistura solidifica completamente a uma temperatura mínima única, formando uma mistura eutética de sólidos.',
        'formula': 'T_eutético < T_fusão_i (qualquer componente puro)\nNo eutético: 1 líquido ⇌ n sólidos',
        'explanation': 'No ponto eutético, uma fase líquida coexiste em equilíbrio com múltiplas fases sólidas. A composição eutética solidifica como se fosse um composto puro (temperatura constante). Muito importante em metalurgia, farmacêutica, e formação de misturas de gelo com sais.',
        'applications': [
            'Cristalização fracionada',
            'Formulação de excipientes farmacêuticos',
            'Ligas metálicas de baixo ponto de fusão',
            'Misturas refrigerantes'
        ],
        'related_terms': ['esl', 'solubilidade', 'cristalizacao', 'diagrama-fases'],
        'reference': 'Mullin (2001), Cap. 6'
    },
    
    'nrtl': {
        'term': 'Modelo NRTL',
        'symbol': '-',
        'category': 'Modelos Termodinâmicos',
        'definition': 'Non-Random Two-Liquid - Modelo de composição local para cálculo de coeficientes de atividade baseado no conceito de não-aleatoriedade molecular.',
        'formula': 'ln γ_i = [Σ(x_j·τ_ji·G_ji) / Σ(x_k·G_ki)] + Σ[x_j·G_ij / Σ(x_k·G_kj)] · [τ_ij - Σ(x_m·τ_mj·G_mj) / Σ(x_k·G_kj)]',
        'explanation': 'Desenvolvido por Renon e Prausnitz (1968). Usa 3 parâmetros binários ajustáveis: τ₁₂, τ₂₁ (energia) e α (não-aleatoriedade, tipicamente 0.2-0.47). Excelente para representar sistemas com equilíbrio líquido-líquido devido ao parâmetro α que captura assimetria local.',
        'applications': [
            'Sistemas altamente não-ideais',
            'Equilíbrio LLE (líquido-líquido)',
            'Misturas água-compostos orgânicos',
            'Sistemas polares e associativos'
        ],
        'related_terms': ['uniquac', 'unifac', 'coeficiente-atividade', 'composicao-local'],
        'reference': 'Renon & Prausnitz (1968), AIChE J.'
    },
    
    'uniquac': {
        'term': 'Modelo UNIQUAC',
        'symbol': '-',
        'category': 'Modelos Termodinâmicos',
        'definition': 'UNIversal QUAsi-Chemical - Modelo semi-empírico de coeficiente de atividade baseado em teoria quasi-química e conceito de composição local.',
        'formula': 'ln γ_i = ln γ_i^C + ln γ_i^R\n(termo combinatorial + termo residual)',
        'explanation': 'Desenvolvido por Abrams e Prausnitz (1975). Separa contribuições de tamanho/forma molecular (combinatorial) e interações energéticas (residual). Requer parâmetros de substância pura (r_i, q_i - volume e área molecular relativos) e parâmetros binários (τ_ij). Base do modelo UNIFAC.',
        'applications': [
            'Misturas com moléculas de tamanhos muito diferentes',
            'Sistemas poliméricos e com solventes',
            'VLE e LLE com boa precisão',
            'Multicomponentes complexos'
        ],
        'related_terms': ['nrtl', 'unifac', 'coeficiente-atividade', 'composicao-local'],
        'reference': 'Abrams & Prausnitz (1975), AIChE J.'
    },
    
    'unifac': {
        'term': 'Modelo UNIFAC',
        'symbol': '-',
        'category': 'Modelos Termodinâmicos',
        'definition': 'UNIQUAC Functional-group Activity Coefficients - Método preditivo de contribuição de grupos funcionais para estimar coeficientes de atividade.',
        'formula': 'Estrutura = UNIQUAC\nParâmetros calculados por:\nr_i = Σ ν_k^(i) · R_k\nq_i = Σ ν_k^(i) · Q_k',
        'explanation': 'Desenvolvido por Fredenslund, Jones e Prausnitz (1975). Divide moléculas em grupos funcionais (CH₃, CH₂, OH, COOH, etc.) e usa tabelas de parâmetros de interação entre grupos. Permite estimar propriedades de misturas sem dados experimentais, usando apenas estrutura molecular.',
        'applications': [
            'Predição de propriedades sem dados experimentais',
            'Screening inicial de solventes',
            'Sistemas com componentes novos ou raros',
            'Estimativa rápida em projetos preliminares'
        ],
        'related_terms': ['uniquac', 'grupos-funcionais', 'metodo-preditivo', 'contribuicao-grupos'],
        'reference': 'Fredenslund et al. (1975), AIChE J.'
    },
    
    'ponto-bolha': {
        'term': 'Ponto de Bolha',
        'symbol': 'T_bubble ou P_bubble',
        'category': 'Cálculos de Equilíbrio',
        'definition': 'Condição termodinâmica onde a primeira bolha de vapor se forma quando um líquido é aquecido (a P fixo) ou despressurizado (a T fixo).',
        'formula': 'Σ (γ_i · x_i · P_i^sat / P) = 1 (a T fixa)\nΣ (γ_i · x_i · P_i^sat) = P (a P fixa)',
        'explanation': 'Cálculo iterativo que determina T ou P onde o líquido de composição conhecida (x_i) começa a vaporizar. A composição do vapor inicial (y_i) é calculada pela equação de equilíbrio. Fundamental para projeto de destilação e evaporadores.',
        'applications': [
            'Início de destilação',
            'Especificação de temperatura de topo',
            'Flash parcial',
            'Diagramas T-x-y e P-x-y'
        ],
        'related_terms': ['ponto-orvalho', 'flash', 'diagrama-pxy', 'elv'],
        'reference': 'Smith et al. (2007), Cap. 10'
    },
    
    'ponto-orvalho': {
        'term': 'Ponto de Orvalho',
        'symbol': 'T_dew ou P_dew',
        'category': 'Cálculos de Equilíbrio',
        'definition': 'Condição termodinâmica onde a primeira gota de líquido se forma quando um vapor é resfriado (a P fixo) ou pressurizado (a T fixo).',
        'formula': 'Σ (y_i / (γ_i · P_i^sat / P)) = 1 (a T fixa)\n1 / Σ (y_i / (γ_i · P_i^sat)) = P (a P fixa)',
        'explanation': 'Cálculo iterativo que determina T ou P onde o vapor de composição conhecida (y_i) começa a condensar. A composição do líquido inicial (x_i) é obtida pela equação de equilíbrio. Fundamental para especificação de condensadores.',
        'applications': [
            'Projeto de condensadores',
            'Especificação de temperatura de fundo',
            'Prevenção de condensação indesejada',
            'Diagramas T-x-y e P-x-y'
        ],
        'related_terms': ['ponto-bolha', 'flash', 'diagrama-txy', 'elv'],
        'reference': 'Smith et al. (2007), Cap. 10'
    },
    
    'flash': {
        'term': 'Flash Isotérmico',
        'symbol': '-',
        'category': 'Cálculos de Equilíbrio',
        'definition': 'Separação parcial instantânea de uma alimentação em fases vapor e líquido em equilíbrio a temperatura e pressão especificadas.',
        'formula': 'z_i = x_i · (1-β) + y_i · β\nΣ [z_i · (K_i - 1) / (1 + β·(K_i - 1))] = 0',
        'explanation': 'Resolve simultaneamente balanço material e equilíbrio de fases para encontrar β (fração vaporizada) e composições x_i, y_i. Algoritmo de Rachford-Rice é usado. K_i = y_i/x_i é a razão de equilíbrio. Fundamental em processos de separação.',
        'applications': [
            'Vasos separadores bifásicos',
            'Torres de destilação (estágios)',
            'Válvulas de expansão',
            'Processos de descompressão'
        ],
        'related_terms': ['ponto-bolha', 'ponto-orvalho', 'rachford-rice', 'elv'],
        'reference': 'Henley & Seader (2011), Cap. 2'
    },
    
    'solubilidade': {
        'term': 'Solubilidade',
        'symbol': 'x_i^sat',
        'category': 'Equilíbrio Sólido-Líquido',
        'definition': 'Concentração máxima de um soluto que pode ser dissolvido em um solvente a uma temperatura e pressão especificadas, em equilíbrio com fase sólida.',
        'formula': 'ln(x_i · γ_i) = (ΔH_fus / R) · [1/T_m - 1/T] - (ΔCp/R) · [ln(T_m/T) - (T_m/T) + 1]',
        'explanation': 'A solubilidade depende da energia de fusão (ΔH_fus), temperatura de fusão (T_m) do soluto, temperatura do sistema (T), e das interações soluto-solvente (γ_i). Solutos com alta ΔH_fus geralmente têm baixa solubilidade.',
        'applications': [
            'Cristalização industrial',
            'Formulação farmacêutica',
            'Purificação por recristalização',
            'Processamento de minerais'
        ],
        'related_terms': ['esl', 'cristalizacao', 'eutético', 'supersaturacao'],
        'reference': 'Prausnitz et al. (1999), Cap. 11'
    },
    
    'cristalizacao': {
        'term': 'Cristalização',
        'symbol': '-',
        'category': 'Equilíbrio Sólido-Líquido',
        'definition': 'Processo de formação de fase sólida cristalina a partir de uma solução supersaturada, fundido ou vapor.',
        'formula': 'Supersaturação: S = C / C_sat\nΔC = C - C_sat (força motriz)',
        'explanation': 'Ocorre quando a concentração excede a solubilidade (supersaturação). Envolve nucleação (formação de núcleos críticos) e crescimento cristalino. Controlada por termodinâmica (equilíbrio) e cinética (taxa). Usada para purificação e obtenção de sólidos.',
        'applications': [
            'Purificação de produtos químicos',
            'Produção de APIs farmacêuticas',
            'Obtenção de sais inorgânicos',
            'Recuperação de solutos valiosos'
        ],
        'related_terms': ['solubilidade', 'supersaturacao', 'esl', 'nucleacao'],
        'reference': 'Mullin (2001), Cap. 5-6'
    }
}


def get_all_terms():
    """Retorna todos os termos do glossário"""
    return [
        {
            'key': key,
            **data
        }
        for key, data in GLOSSARY_TERMS.items()
    ]


def search_terms(query):
    """Busca termos que correspondem à query"""
    query = query.lower().strip()
    results = []
    
    for key, data in GLOSSARY_TERMS.items():
        # Busca no termo, definição, categoria
        if (query in data['term'].lower() or 
            query in key or
            query in data['definition'].lower() or
            query in data['category'].lower()):
            results.append({
                'key': key,
                **data
            })
    
    return results


def get_term(term_key):
    """Retorna um termo específico"""
    return GLOSSARY_TERMS.get(term_key)


def get_terms_by_category(category):
    """Retorna termos de uma categoria específica"""
    return [
        {
            'key': key,
            **data
        }
        for key, data in GLOSSARY_TERMS.items()
        if data['category'] == category
    ]
