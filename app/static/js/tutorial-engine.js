/* =============================================================================
   TUTORIAL-ENGINE.JS v11.0 - UNIVERSAL (ELV + ELL + ESL)
   ========================================================================== */


class TutorialEngine {
    constructor(tutorialData) {
        this.tutorial = tutorialData;
        this.currentStep = 0;
        this.completed = false;
        this.paused = false;
        
        this.overlay = null;
        this.spotlight = null;
        this.instructionCard = null;
        this.navigationBar = null;
        
        this.initialComponentCount = 0;
        
        this.init();
    }
    
    async init() {
        console.log('🎓 [TUTORIAL] Iniciando:', this.tutorial.title);
        
        await this.waitForComponents();
        
        this.initialComponentCount = document.querySelectorAll('.component-tag').length;
        
        this.createOverlay();
        this.createSpotlight();
        this.createInstructionCard();
        this.createNavigationBar();
        this.injectGlobalStyles();
        
        this.showStep(0);
        this.saveProgress();
    }
    
    async waitForComponents() {
        console.log('[TUTORIAL] ⏳ Aguardando componentes...');
        let attempts = 0;
        
        while (attempts < 50) {
            if ((window.allComponents && window.allComponents.length > 0) || 
                (typeof allComponents !== 'undefined' && allComponents.length > 0)) {
                console.log('[TUTORIAL] ✅ Componentes carregados!');
                return;
            }
            
            const modalList = document.getElementById('componentList');
            if (modalList && modalList.children.length > 0) {
                console.log('[TUTORIAL] ✅ Lista detectada');
                return;
            }
            
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        console.warn('[TUTORIAL] ⚠️ Timeout');
    }
    
    injectGlobalStyles() {
        const style = document.createElement('style');
        style.id = 'tutorial-global-styles';
        style.textContent = `
            @keyframes spotlightPulse {
                0%, 100% { 
                    border-color: #f59e0b; 
                    box-shadow: 0 0 30px rgba(245, 158, 11, 0.8),
                                inset 0 0 20px rgba(245, 158, 11, 0.4); 
                }
                50% { 
                    border-color: #fcd34d; 
                    box-shadow: 0 0 50px rgba(245, 158, 11, 1),
                                inset 0 0 30px rgba(245, 158, 11, 0.6); 
                }
            }
            
            @keyframes cardSlideIn {
                from { transform: translateY(20px) scale(0.95); opacity: 0; }
                to { transform: translateY(0) scale(1); opacity: 1; }
            }
            
            @keyframes successPop {
                0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0; }
                50% { transform: translate(-50%, -50%) scale(1.1); }
                100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
            }
            
            body.tutorial-active { overflow-x: hidden; }
            
            #tutorial-overlay {
                pointer-events: none !important;
            }
            
            #componentModal {
                z-index: 100001 !important;
            }
            
            #componentModal,
            #componentModal *,
            #componentModal .list-group-item {
                opacity: 1 !important;
                pointer-events: auto !important;
                cursor: pointer !important;
            }
            
            #tutorial-spotlight {
                z-index: 100004 !important;
                pointer-events: none !important;
            }
            
            #tutorial-instruction-card {
                z-index: 100003 !important;
            }
            
            #tutorial-navigation-bar {
                z-index: 100007 !important;
            }
            
            body.tutorial-active .tutorial-highlighted {
                z-index: 100005 !important;
                position: relative !important;
                pointer-events: auto !important;
            }
        `;
        document.head.appendChild(style);
        document.body.classList.add('tutorial-active');
    }
    
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.id = 'tutorial-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: transparent;
            z-index: 100000;
            opacity: 0;
            transition: opacity 0.3s ease, box-shadow 0.3s ease;
            pointer-events: none;
        `;
        document.body.appendChild(this.overlay);
        
        setTimeout(() => { 
            this.overlay.style.boxShadow = 'inset 0 0 0 9999px rgba(0, 0, 0, 0.85)';
            this.overlay.style.opacity = '1'; 
        }, 10);
    }
    
    createSpotlight() {
        this.spotlight = document.createElement('div');
        this.spotlight.id = 'tutorial-spotlight';
        this.spotlight.style.cssText = `
            position: absolute;
            border: 5px solid #f59e0b;
            border-radius: 14px;
            background: transparent;
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.8),
                        inset 0 0 20px rgba(245, 158, 11, 0.4);
            z-index: 100004;
            pointer-events: none;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            animation: spotlightPulse 2s ease-in-out infinite;
        `;
        document.body.appendChild(this.spotlight);
    }
    
    createInstructionCard() {
        this.instructionCard = document.createElement('div');
        this.instructionCard.id = 'tutorial-instruction-card';
        this.instructionCard.style.cssText = `
            position: fixed;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 2px solid #f59e0b;
            border-radius: 16px;
            padding: 24px;
            max-width: 450px;
            z-index: 100003;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8),
                        0 0 40px rgba(245, 158, 11, 0.5);
            animation: cardSlideIn 0.4s ease;
        `;
        document.body.appendChild(this.instructionCard);
    }
    
    createNavigationBar() {
        this.navigationBar = document.createElement('div');
        this.navigationBar.id = 'tutorial-navigation-bar';
        this.navigationBar.style.cssText = `
            position: fixed;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid rgba(245, 158, 11, 0.4);
            border-radius: 30px;
            padding: 12px 24px;
            z-index: 100007;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            animation: cardSlideIn 0.4s ease;
        `;
        document.body.appendChild(this.navigationBar);
    }
    
    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.tutorial.steps.length) {
            return this.complete();
        }
        
        this.currentStep = stepIndex;
        const step = this.tutorial.steps[stepIndex];
        
        console.log(`🎯 [TUTORIAL] Step ${stepIndex + 1}/${this.tutorial.steps.length}: ${step.title}`);
        
        document.querySelectorAll('.tutorial-highlighted').forEach(el => {
            el.classList.remove('tutorial-highlighted');
        });
        
        if (step.target === '#componentSearch') {
            const modal = document.getElementById('componentModal');
            
            if (!modal || modal.style.display !== 'flex') {
                console.log('🔓 [TUTORIAL] Abrindo modal...');
                
                this.initialComponentCount = document.querySelectorAll('.component-tag').length;
                
                if (typeof showComponentModal === 'function') {
                    showComponentModal();
                }
                
                setTimeout(() => {
                    if (typeof renderComponentList === 'function') {
                        renderComponentList('');
                    }
                    
                    const modal = document.getElementById('componentModal');
                    if (modal) modal.classList.add('tutorial-active');
                    
                    this.updateSpotlight(step.target);
                    this.updateInstructionCard(step);
                    this.updateNavigationBar();
                    this.setupValidation(step);
                    this.saveProgress();
                }, 600);
                
                return;
            } else {
                if (typeof renderComponentList === 'function') {
                    renderComponentList('');
                }
                modal.classList.add('tutorial-active');
                this.initialComponentCount = document.querySelectorAll('.component-tag').length;
            }
        } else {
            const modal = document.getElementById('componentModal');
            if (modal) modal.classList.remove('tutorial-active');
        }
        
        this.updateSpotlight(step.target);
        this.updateInstructionCard(step);
        this.updateNavigationBar();
        this.scrollToElement(step.target);
        this.setupValidation(step);
        this.saveProgress();
    }
    
    updateSpotlight(targetSelector) {
        let element = document.querySelector(targetSelector);
        
        if (!element) {
            console.warn('[TUTORIAL] ⚠️ Elemento não encontrado:', targetSelector);
            
            // ✅ FALLBACK UNIVERSAL: tenta encontrar em #dynamicFields
            const fallbackSelectors = {
                '#pressure': ['#dynamicFields input[id="pressure"]', '#dynamicFields input[name="pressure"]'],
                '#temperature': ['#dynamicFields input[id="temperature"]', '#dynamicFields input[name="temperature"]'],
                '#solventRatio': ['#dynamicFields input[id="solventRatio"]', '#dynamicFields input[name="solventRatio"]'],
                '#tempStart': ['#dynamicFields input[id="tempStart"]', '#dynamicFields input[name="tempStart"]'],
                '#tempEnd': ['#dynamicFields input[id="tempEnd"]', '#dynamicFields input[name="tempEnd"]']
            };
            
            if (fallbackSelectors[targetSelector]) {
                for (const fallback of fallbackSelectors[targetSelector]) {
                    element = document.querySelector(fallback);
                    if (element) {
                        console.log('[TUTORIAL] ✅ Usando fallback:', fallback);
                        break;
                    }
                }
            }
            
            // ✅ Se ainda não encontrou, usa container pai
            if (!element) {
                element = document.querySelector('#dynamicFields') || 
                          document.querySelector('.calc-panel');
                
                if (element) {
                    console.log('[TUTORIAL] ✅ Usando container pai');
                }
            }
            
            if (!element) {
                console.error('[TUTORIAL] ❌ Nenhum elemento encontrado');
                return;
            }
        }
        
        const rect = element.getBoundingClientRect();
        
        let padding = 12;
        if (element.tagName === 'BUTTON' || element.classList.contains('btn')) padding = 20;
        if (element.tagName === 'INPUT' || element.tagName === 'SELECT') padding = 16;
        if (element.id === 'componentSearch') padding = 18;
        if (element.id === 'dynamicFields' || element.id === 'results') padding = 24;
        
        const top = rect.top - padding + window.scrollY;
        const left = rect.left - padding;
        const width = rect.width + padding * 2;
        const height = rect.height + padding * 2;
        
        this.spotlight.style.top = `${top}px`;
        this.spotlight.style.left = `${left}px`;
        this.spotlight.style.width = `${width}px`;
        this.spotlight.style.height = `${height}px`;
        
        element.classList.add('tutorial-highlighted');
        
        const overlayBoxShadow = `
            0 0 0 ${top}px rgba(0, 0, 0, 0.85),
            0 ${top + height}px 0 9999px rgba(0, 0, 0, 0.85),
            ${left + width}px ${top}px 0 9999px rgba(0, 0, 0, 0.85),
            ${left - 9999}px ${top}px 0 9999px rgba(0, 0, 0, 0.85)
        `;
        
        this.overlay.style.boxShadow = overlayBoxShadow;
        
        console.log('✨ [TUTORIAL] Elemento destacado:', element.id || element.className);
    }
    
    updateInstructionCard(step) {
        const stepNum = this.currentStep + 1;
        const totalSteps = this.tutorial.steps.length;
        
        this.instructionCard.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px;">
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #f59e0b, #d97706); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700; color: white; flex-shrink: 0;">
                    ${stepNum}
                </div>
                <div style="flex: 1;">
                    <h4 style="color: #fcd34d; font-size: 1.1rem; font-weight: 700; margin: 0 0 8px 0;">${step.title}</h4>
                    <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; margin: 0;">${step.content}</p>
                </div>
            </div>
            
            <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
                <div style="font-size: 0.85rem; color: #fcd34d; font-weight: 600; margin-bottom: 4px;"><i class="bi bi-hand-index"></i> Ação necessária:</div>
                <div style="color: #e5e7eb; font-size: 0.9rem;">${step.action}</div>
            </div>
            
            ${step.hint ? `<div style="background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38bdf8; padding: 10px; border-radius: 8px; margin-bottom: 16px;">
                <div style="font-size: 0.8rem; color: #7dd3fc; font-weight: 600; margin-bottom: 3px;"><i class="bi bi-lightbulb"></i> Dica:</div>
                <div style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.5;">${step.hint}</div>
            </div>` : ''}
            
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(148,163,184,0.2); text-align: center;">
                <small style="color: #94a3b8; font-size: 0.8rem;">
                    💡 Complete a ação ou use os botões de navegação
                </small>
            </div>
        `;
        
        this.positionInstructionCard(step.target, step.position || 'right');
    }
    
    positionInstructionCard(targetSelector, position) {
        let element = document.querySelector(targetSelector);
        
        if (!element) {
            // ✅ Usa mesma lógica de fallback do spotlight
            const fallbackMap = {
                '#pressure': '#dynamicFields',
                '#temperature': '#dynamicFields',
                '#solventRatio': '#dynamicFields',
                '#tempStart': '#dynamicFields',
                '#tempEnd': '#dynamicFields'
            };
            
            const fallback = fallbackMap[targetSelector];
            if (fallback) {
                element = document.querySelector(fallback);
            }
            
            if (!element) {
                element = document.querySelector('.calc-panel');
            }
        }
        
        if (!element) return;
        
        const rect = element.getBoundingClientRect();
        const cardWidth = 420;
        
        setTimeout(() => {
            const cardHeight = this.instructionCard.offsetHeight;
            const gap = 30;
            
            let top, left;
            
            switch (position) {
                case 'right':
                    top = rect.top + rect.height / 2 - cardHeight / 2;
                    left = rect.right + gap;
                    if (left + cardWidth > window.innerWidth - 20) {
                        left = rect.left - cardWidth - gap;
                        if (left < 20) position = 'bottom';
                    }
                    break;
                case 'left':
                    top = rect.top + rect.height / 2 - cardHeight / 2;
                    left = rect.left - cardWidth - gap;
                    if (left < 20) {
                        left = rect.right + gap;
                        if (left + cardWidth > window.innerWidth - 20) position = 'bottom';
                    }
                    break;
                case 'bottom':
                    top = rect.bottom + gap;
                    left = rect.left + rect.width / 2 - cardWidth / 2;
                    break;
                case 'top':
                    top = rect.top - cardHeight - gap;
                    left = rect.left + rect.width / 2 - cardWidth / 2;
                    break;
                default:
                    top = rect.bottom + gap;
                    left = rect.left;
            }
            
            if (position === 'bottom') {
                top = rect.bottom + gap;
                left = rect.left + rect.width / 2 - cardWidth / 2;
            }
            
            if (left < 20) left = 20;
            if (left + cardWidth > window.innerWidth - 20) left = window.innerWidth - cardWidth - 20;
            if (top < 140) top = rect.bottom + gap;
            if (top + cardHeight > window.innerHeight - 20) {
                top = rect.top - cardHeight - gap;
                if (top < 140) top = Math.max(140, (window.innerHeight - cardHeight) / 2);
            }
            
            this.instructionCard.style.top = `${top + window.scrollY}px`;
            this.instructionCard.style.left = `${left}px`;
        }, 50);
    }
    
    updateNavigationBar() {
        const stepNum = this.currentStep + 1;
        const totalSteps = this.tutorial.steps.length;
        const percentage = (stepNum / totalSteps) * 100;
        
        this.navigationBar.innerHTML = `
            <button onclick="tutorial.previousStep()" 
                    style="padding: 8px 16px; background: rgba(148,163,184,0.2); border: 1px solid rgba(148,163,184,0.4); color: #cbd5e1; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: all 0.2s; ${this.currentStep === 0 ? 'opacity: 0.5; cursor: not-allowed;' : ''}" 
                    ${this.currentStep === 0 ? 'disabled' : ''}
                    onmouseover="if(!this.disabled) this.style.background='rgba(148,163,184,0.3)'" 
                    onmouseout="this.style.background='rgba(148,163,184,0.2)'">
                <i class="bi bi-arrow-left"></i> Anterior
            </button>
            
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 200px; height: 8px; background: rgba(148, 163, 184, 0.2); border-radius: 10px; overflow: hidden;">
                    <div style="width: ${percentage}%; height: 100%; background: linear-gradient(90deg, #f59e0b, #fcd34d); border-radius: 10px; transition: width 0.4s ease;"></div>
                </div>
                <span style="color: #fcd34d; font-weight: 600; font-size: 0.9rem; white-space: nowrap;">Passo ${stepNum}/${totalSteps}</span>
            </div>
            
            <button onclick="tutorial.nextStep()" 
                    style="padding: 8px 16px; background: rgba(245,158,11,0.2); border: 1px solid #f59e0b; color: #fcd34d; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: all 0.2s;"
                    onmouseover="this.style.background='rgba(245,158,11,0.3)'" 
                    onmouseout="this.style.background='rgba(245,158,11,0.2)'">
                Próximo <i class="bi bi-arrow-right"></i>
            </button>
            
            <button onclick="tutorial.pause()" 
                    style="padding: 8px 16px; background: rgba(239,68,68,0.2); border: 1px solid rgba(239,68,68,0.4); color: #fca5a5; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: all 0.2s;"
                    onmouseover="this.style.background='rgba(239,68,68,0.3)'" 
                    onmouseout="this.style.background='rgba(239,68,68,0.2)'">
                <i class="bi bi-x-circle"></i> Sair
            </button>
        `;
    }
    
    scrollToElement(targetSelector) {
        let element = document.querySelector(targetSelector);
        
        if (!element) {
            // ✅ Usa fallback
            element = document.querySelector('#dynamicFields');
        }
        
        if (!element) return;
        
        const rect = element.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const targetTop = rect.top + scrollTop - window.innerHeight / 3;
        
        window.scrollTo({ top: Math.max(0, targetTop), behavior: 'smooth' });
    }
    
    setupValidation(step) {
        const validation = step.validation;
        if (!validation) return;
        
        console.log('[TUTORIAL] 🔧 Configurando validação:', validation.type);
        
        switch (validation.type) {
            case 'component_added':
                this.validateComponentAdded();
                break;
            case 'select_value':
                this.validateSelectValue(validation.element, validation.value);
                break;
            case 'input_value':
                this.validateInputValue(validation.element, validation.min, validation.max);
                break;
            case 'composition_filled':
                this.validateCompositionFilled(validation.min, validation.max);
                break;
            case 'button_click':
                this.validateButtonClick(validation.element);
                break;
            case 'element_visible':
                this.validateElementVisible(validation.element);
                break;
        }
    }
    
    validateComponentAdded() {
        const checkInterval = setInterval(() => {
            if (this.paused || this.completed) {
                clearInterval(checkInterval);
                return;
            }
            
            const currentCount = document.querySelectorAll('.component-tag').length;
            
            if (currentCount > this.initialComponentCount) {
                console.log('[TUTORIAL] ✅ Componente adicionado!');
                clearInterval(checkInterval);
                
                const modal = document.getElementById('componentModal');
                if (modal && typeof closeComponentModal === 'function') {
                    closeComponentModal();
                }
                
                this.initialComponentCount = currentCount;
                this.showSuccessAndAdvance();
            }
        }, 300);
    }
    
    validateSelectValue(elementSelector, expectedValue) {
        const element = document.querySelector(elementSelector);
        if (!element) return;
        
        const handler = () => {
            if (element.value === expectedValue) {
                element.removeEventListener('change', handler);
                setTimeout(() => this.showSuccessAndAdvance(), 300);
            }
        };
        
        element.addEventListener('change', handler);
    }
    
    validateInputValue(elementSelector, min, max) {
        let element = document.querySelector(elementSelector);
        
        // ✅ FALLBACK UNIVERSAL para todos os campos
        if (!element) {
            const fallbackSelectors = [
                `#dynamicFields input[id="${elementSelector.replace('#', '')}"]`,
                `#dynamicFields input[name="${elementSelector.replace('#', '')}"]`,
                `#dynamicFields input[type="number"]:not([id])`,  // qualquer input numérico
                `#dynamicFields input[type="number"]`
            ];
            
            for (const selector of fallbackSelectors) {
                element = document.querySelector(selector);
                if (element) {
                    console.log('[TUTORIAL] ✅ Input encontrado via fallback:', selector);
                    break;
                }
            }
        }
        
        if (!element) {
            console.warn('[TUTORIAL] ⚠️ Input não encontrado:', elementSelector);
            return;
        }
        
        const validate = () => {
            const value = parseFloat(element.value);
            if (!isNaN(value) && value >= min && value <= max) {
                element.removeEventListener('input', validate);
                element.removeEventListener('change', validate);
                element.removeEventListener('blur', validate);
                setTimeout(() => this.showSuccessAndAdvance(), 500);
            }
        };
        
        element.addEventListener('input', validate);
        element.addEventListener('change', validate);
        element.addEventListener('blur', validate);
    }
    
    validateCompositionFilled(min, max) {
        const checkInterval = setInterval(() => {
            if (this.paused || this.completed) {
                clearInterval(checkInterval);
                return;
            }
            
            // ✅ BUSCA UNIVERSAL: x1, x2, x3, x_1, x_2, x_3, xComponent1, etc.
            const inputs = document.querySelectorAll(
                '#dynamicFields input[id^="x"], ' +
                '#dynamicFields input[name^="x"], ' +
                '#dynamicFields input[placeholder*="fração"], ' +
                '#dynamicFields input[placeholder*="composição"]'
            );
            
            for (const input of inputs) {
                const value = parseFloat(input.value);
                if (!isNaN(value) && value >= min && value <= max) {
                    console.log('[TUTORIAL] ✅ Composição válida detectada:', value);
                    clearInterval(checkInterval);
                    setTimeout(() => this.showSuccessAndAdvance(), 800);
                    return;
                }
            }
        }, 500);
    }
    
    validateButtonClick(elementSelector) {
        const element = document.querySelector(elementSelector);
        if (!element) {
            console.warn('[TUTORIAL] ⚠️ Botão não encontrado:', elementSelector);
            return;
        }
        
        const handler = () => {
            element.removeEventListener('click', handler);
            setTimeout(() => this.showSuccessAndAdvance(), 500);
        };
        
        element.addEventListener('click', handler, { once: true });
    }
    
    validateElementVisible(elementSelector) {
        const checkInterval = setInterval(() => {
            if (this.paused || this.completed) {
                clearInterval(checkInterval);
                return;
            }
            
            const element = document.querySelector(elementSelector);
            if (element && element.offsetParent !== null) {
                clearInterval(checkInterval);
                setTimeout(() => this.showSuccessAndAdvance(), 1500);
            }
        }, 500);
    }
    
    showSuccessAndAdvance() {
        console.log('🎉 [TUTORIAL] Step completo!');
        
        const successMsg = document.createElement('div');
        successMsg.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: white;
            padding: 20px 40px;
            border-radius: 16px;
            font-size: 1.2rem;
            font-weight: 700;
            z-index: 100010;
            box-shadow: 0 10px 40px rgba(34, 197, 94, 0.6);
            animation: successPop 0.5s ease;
        `;
        successMsg.innerHTML = '<i class="bi bi-check-circle-fill"></i> Correto!';
        
        document.body.appendChild(successMsg);
        
        setTimeout(() => {
            successMsg.remove();
            this.nextStep();
        }, 1500);
    }
    
    nextStep() { this.showStep(this.currentStep + 1); }
    previousStep() { if (this.currentStep > 0) this.showStep(this.currentStep - 1); }
    
    pause() {
        if (confirm('Deseja realmente sair do tutorial? Seu progresso será salvo.')) {
            this.paused = true;
            this.cleanup();
            window.location.href = '/educational/tutorials';
        }
    }
    
    complete() {
        console.log('🎉 [TUTORIAL] Tutorial completado!');
        this.completed = true;
        this.showCompletionModal();
        this.saveCompletion();
        setTimeout(() => this.cleanup(), 5000);
    }
    
    showCompletionModal() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #1e293b, #0f172a); border: 2px solid #22c55e;
            border-radius: 20px; padding: 40px; max-width: 500px; z-index: 100020;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6); text-align: center;
        `;
        modal.innerHTML = `
            <div style="font-size: 4rem; margin-bottom: 20px;">🎉</div>
            <h2 style="color: #22c55e; font-size: 1.8rem; font-weight: 700; margin-bottom: 15px;">Tutorial Completado!</h2>
            <p style="color: #cbd5e1; font-size: 1.1rem; line-height: 1.6; margin-bottom: 25px;">
                Parabéns! Você concluiu o tutorial<br><strong style="color: #fcd34d;">${this.tutorial.title}</strong>
            </p>
            <button onclick="this.parentElement.remove(); window.location.href='/educational/tutorials'" style="
                background: linear-gradient(135deg, #22c55e, #16a34a); border: none; color: white;
                padding: 12px 32px; border-radius: 12px; font-size: 1rem; font-weight: 600;
                cursor: pointer; transition: transform 0.2s;" 
                onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                <i class="bi bi-check-circle"></i> Ver Todos os Tutoriais
            </button>
        `;
        document.body.appendChild(modal);
    }
    
    cleanup() {
        console.log('🧹 [TUTORIAL] Limpando elementos');
        if (this.overlay) this.overlay.remove();
        if (this.spotlight) this.spotlight.remove();
        if (this.instructionCard) this.instructionCard.remove();
        if (this.navigationBar) this.navigationBar.remove();
        
        const styles = document.getElementById('tutorial-global-styles');
        if (styles) styles.remove();
        
        document.body.classList.remove('tutorial-active');
        document.querySelectorAll('.tutorial-highlighted').forEach(el => el.classList.remove('tutorial-highlighted'));
        
        const modal = document.getElementById('componentModal');
        if (modal) modal.classList.remove('tutorial-active');
    }
    
    saveProgress() {
        localStorage.setItem(`tutorial_${this.tutorial.id}_progress`, this.currentStep);
        localStorage.setItem(`tutorial_${this.tutorial.id}_timestamp`, Date.now());
    }
    
    saveCompletion() {
        localStorage.setItem(`tutorial_${this.tutorial.id}_completed`, 'true');
        localStorage.setItem(`tutorial_${this.tutorial.id}_completion_date`, new Date().toISOString());
    }
    
    static loadProgress(tutorialId) {
        const progress = localStorage.getItem(`tutorial_${tutorialId}_progress`);
        return progress ? parseInt(progress) : 0;
    }
    
    static isCompleted(tutorialId) {
        return localStorage.getItem(`tutorial_${tutorialId}_completed`) === 'true';
    }
}


let tutorial = null;


async function startTutorial(tutorialId) {
    console.log('🚀 [TUTORIAL] Iniciando tutorial:', tutorialId);
    try {
        const response = await fetch(`/educational/api/tutorials/${tutorialId}`);
        const data = await response.json();
        if (!data.success) throw new Error(data.error || 'Tutorial não encontrado');
        tutorial = new TutorialEngine(data.tutorial);
    } catch (error) {
        console.error('[TUTORIAL] Erro:', error);
        alert('Erro ao carregar tutorial. Tente novamente.');
    }
}


window.TutorialEngine = TutorialEngine;
window.startTutorial = startTutorial;
window.tutorial = tutorial;
