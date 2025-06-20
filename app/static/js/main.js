// Enhanced main.js with interactive tour and tooltips
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced main.js loaded');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize interactive tour
    initializeInteractiveTour();
    
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Initialize form guidance
    initializeFormGuidance();
});

// Initialize Tippy.js tooltips
function initializeTooltips() {
    if (typeof tippy !== 'undefined') {
        tippy('[data-tippy-content]', {
            placement: 'top',
            arrow: true,
            theme: 'brand-theme',
            animation: 'scale',
            duration: [200, 150],
            maxWidth: 300,
            interactive: true
        });
    }
}

// Initialize interactive tour with Intro.js
function initializeInteractiveTour() {
    const startTourBtn = document.getElementById('startTourBtn');
    if (!startTourBtn || typeof introJs === 'undefined') return;
    
    startTourBtn.addEventListener('click', function() {
        const tour = introJs();
        
        tour.setOptions({
            steps: [
                {
                    intro: '<h3>Welcome to Strategic Intelligence Analysis!</h3><p>This interactive tour will guide you through creating a comprehensive strategic analysis.</p>'
                },
                {
                    element: '[data-step="1"]',
                    intro: '<h4>Strategic Question</h4><p>Start by entering your core strategic question. This should be specific, actionable, and focused on a key business challenge or opportunity.</p>',
                    position: 'bottom'
                },
                {
                    element: '[data-step="2"]',
                    intro: '<h4>Time Frame</h4><p>Choose the appropriate time horizon for your analysis.</p>',
                    position: 'top'
                },
                {
                    element: '[data-step="3"]',
                    intro: '<h4>Geographic Region</h4><p>Select the geographic scope for your analysis.</p>',
                    position: 'top'
                },
                {
                    element: '[data-step="4"]',
                    intro: '<h4>Analysis Customization</h4><p>Fine-tune your analysis with these parameters.</p>',
                    position: 'top'
                },
                {
                    element: '[data-step="5"]',
                    intro: '<h4>Additional Instructions</h4><p>Add specific constraints or focus areas.</p>',
                    position: 'top'
                },
                {
                    element: '[data-step="6"]',
                    intro: '<h4>Start Your Analysis</h4><p>Ready to begin! Click the "Start Analysis" button.</p>',
                    position: 'top'
                }
            ],
            showProgress: true,
            showBullets: true,
            showStepNumbers: true,
            exitOnOverlayClick: false,
            exitOnEsc: true,
            nextLabel: 'Next →',
            prevLabel: '← Previous',
            skipLabel: 'Skip Tour',
            doneLabel: 'Got it!'
        });
        
        tour.start();
    });
}

// Initialize mobile menu functionality
function initializeMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

// Initialize form guidance and validation
function initializeFormGuidance() {
    const strategicQuestion = document.getElementById('strategic_question');
    const prompt = document.getElementById('prompt');
    const timeFrame = document.getElementById('time_frame');
    const region = document.getElementById('region');
    
    // Real-time character count for strategic question
    if (strategicQuestion) {
        // Add counter element
        let counter = document.createElement('div');
        counter.className = 'char-counter text-xs mt-1 text-right';
        strategicQuestion.parentNode.appendChild(counter);
        const minLength = 20;
        const maxLength = 500;
        function updateCounter() {
            const length = strategicQuestion.value.length;
            counter.textContent = `${length} / ${maxLength} characters`;
            if (length < minLength) {
                counter.classList.add('text-amber-600');
                counter.classList.remove('text-green-600', 'text-red-600');
            } else if (length > maxLength) {
                counter.classList.add('text-red-600');
                counter.classList.remove('text-green-600', 'text-amber-600');
            } else {
                counter.classList.add('text-green-600');
                counter.classList.remove('text-amber-600', 'text-red-600');
            }
        }
        strategicQuestion.addEventListener('input', updateCounter);
        updateCounter();
    }
    
    // Real-time character count for prompt
    if (prompt) {
        let counter = document.createElement('div');
        counter.className = 'char-counter text-xs mt-1 text-right';
        prompt.parentNode.appendChild(counter);
        const maxLength = 500;
        function updateCounter() {
            const length = prompt.value.length;
            counter.textContent = `${length} / ${maxLength} characters`;
            if (length > maxLength) {
                counter.classList.add('text-red-600');
                counter.classList.remove('text-green-600');
            } else {
                counter.classList.add('text-green-600');
                counter.classList.remove('text-red-600');
            }
        }
        prompt.addEventListener('input', updateCounter);
        updateCounter();
    }
    
    // Add helpful suggestions for time frame and region
    if (timeFrame) {
        timeFrame.addEventListener('change', function() {
            showFieldSuggestion(this, 'time_frame');
        });
    }
    
    if (region) {
        region.addEventListener('change', function() {
            showFieldSuggestion(this, 'region');
        });
    }
}

// Show helpful suggestions for form fields
function showFieldSuggestion(element, fieldType) {
    const suggestions = {
        time_frame: {
            short_term: 'Perfect for tactical decisions and immediate actions',
            medium_term: 'Ideal for strategic planning and major initiatives',
            long_term: 'Great for vision setting and transformation projects'
        },
        region: {
            global: 'Comprehensive worldwide analysis',
            north_america: 'Focus on US and Canadian markets',
            europe: 'European market and regulatory environment',
            asia: 'Asian market dynamics and opportunities',
            africa: 'African market potential and challenges',
            latin_america: 'Latin American market conditions'
        }
    };
    
    const value = element.value;
    const suggestion = suggestions[fieldType]?.[value];
    
    if (suggestion) {
        // Remove existing suggestion
        const existingSuggestion = element.parentNode.querySelector('.field-suggestion');
        if (existingSuggestion) {
            existingSuggestion.remove();
        }
        
        // Add new suggestion
        const suggestionDiv = document.createElement('div');
        suggestionDiv.className = 'field-suggestion text-sm text-brand-lapis mt-2';
        suggestionDiv.innerHTML = suggestion;
        element.parentNode.appendChild(suggestionDiv);
    }
}

// Export functions for use in other scripts
window.formUtils = {
    initializeTooltips,
    initializeInteractiveTour,
    initializeMobileMenu,
    initializeFormGuidance
};
