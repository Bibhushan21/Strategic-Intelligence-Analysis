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
    console.log('Initializing mobile menu...');
    
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    console.log('Mobile menu button:', mobileMenuButton);
    console.log('Mobile menu:', mobileMenu);
    
    if (!mobileMenuButton || !mobileMenu) {
        console.error('Mobile menu elements not found!');
        return;
    }
    
    console.log('Mobile menu elements found, adding event listener...');
    
    // Add visual feedback for debugging
    mobileMenuButton.style.cursor = 'pointer';
    mobileMenuButton.style.backgroundColor = 'rgba(255, 0, 0, 0.1)'; // Temporary red background
    
    // Main click handler
    mobileMenuButton.addEventListener('click', function(e) {
        console.log('Mobile menu button clicked!');
        e.preventDefault();
        e.stopPropagation();
        
        mobileMenu.classList.toggle('hidden');
        console.log('Menu toggled, hidden class:', mobileMenu.classList.contains('hidden'));
        
        // Toggle aria-expanded for accessibility
        const isExpanded = !mobileMenu.classList.contains('hidden');
        mobileMenuButton.setAttribute('aria-expanded', isExpanded);
        
        // Change hamburger icon to X when menu is open
        const svg = mobileMenuButton.querySelector('svg');
        if (svg) {
            if (isExpanded) {
                svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
            } else {
                svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>';
            }
        }
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!mobileMenuButton.contains(e.target) && !mobileMenu.contains(e.target)) {
            if (!mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.add('hidden');
                mobileMenuButton.setAttribute('aria-expanded', 'false');
                
                const svg = mobileMenuButton.querySelector('svg');
                if (svg) {
                    svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>';
                }
            }
        }
    });
    
    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.add('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            mobileMenuButton.focus();
            
            const svg = mobileMenuButton.querySelector('svg');
            if (svg) {
                svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>';
            }
        }
    });
    
    // Set initial aria-expanded
    mobileMenuButton.setAttribute('aria-expanded', 'false');
    console.log('Mobile menu initialized successfully');
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
