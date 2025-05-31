// DOM Elements
const agentOutputs = document.getElementById('agentOutputs');
const analysisForm = document.getElementById('analysisForm');

// Track expanded state of agent sections
const expandedSections = new Set();

// Toggle agent section collapse/expand
function toggleAgentSection(agentName) {
    const content = document.getElementById(`${agentName}Content`);
    const arrow = document.getElementById(`${agentName}CollapseArrow`);
    
    if (!content || !arrow) return;
    
    const isExpanded = expandedSections.has(agentName);
    
    if (isExpanded) {
        // Collapse
        content.style.maxHeight = '0px';
        arrow.style.transform = 'rotate(0deg)';
        expandedSections.delete(agentName);
    } else {
        // Expand
        content.style.maxHeight = content.scrollHeight + 'px';
        arrow.style.transform = 'rotate(180deg)';
        expandedSections.add(agentName);
        
        // Auto-scroll to the section header after a short delay
        setTimeout(() => {
            const header = content.previousElementSibling;
            if (header) {
                header.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start',
                    inline: 'nearest'
                });
            }
        }, 300);
    }
}

// Auto-expand section when agent completes (if it's the first completion)
function autoExpandOnCompletion(agentName) {
    // Only auto-expand if no sections are currently expanded
    if (expandedSections.size === 0) {
        setTimeout(() => {
            toggleAgentSection(agentName);
        }, 500); // Small delay for visual effect
    }
}

// Recalculate height for expanded sections (useful when content changes)
function recalculateExpandedHeight(agentName) {
    if (expandedSections.has(agentName)) {
        const content = document.getElementById(`${agentName}Content`);
        if (content) {
            content.style.maxHeight = content.scrollHeight + 'px';
        }
    }
}

// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
    
    // Tab functionality for agent outputs
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('tab-button') || event.target.closest('.tab-button')) {
            const button = event.target.classList.contains('tab-button') ? event.target : event.target.closest('.tab-button');
            const agentName = button.dataset.agent;
            const tabType = button.dataset.tab;
            
            // Update button states
            const allButtons = document.querySelectorAll(`[data-agent="${agentName}"].tab-button`);
            allButtons.forEach(btn => {
                btn.classList.remove('active', 'bg-white', 'shadow-sm', 'text-gray-700');
                btn.classList.add('text-gray-500', 'hover:text-gray-700');
            });
            
            button.classList.add('active', 'bg-white', 'shadow-sm', 'text-gray-700');
            button.classList.remove('text-gray-500', 'hover:text-gray-700');
            
            // Update content visibility
            const allContent = document.querySelectorAll(`[data-agent="${agentName}"].tab-content`);
            allContent.forEach(content => {
                content.classList.add('hidden');
                content.classList.remove('active');
            });
            
            const activeContent = document.querySelector(`[data-content="${tabType}"][data-agent="${agentName}"]`);
            if (activeContent) {
                activeContent.classList.remove('hidden');
                activeContent.classList.add('active');
            }
            
            // Recalculate height if section is expanded
            recalculateExpandedHeight(agentName);
        }
    });
});

// Create agent output section
function createAgentOutputSection(agentName) {
    const section = document.createElement('div');
    section.className = 'relative bg-gradient-to-br from-white to-gray-50 rounded-3xl shadow-2xl border border-gray-100 overflow-hidden transform transition-all duration-500 hover:scale-102 hover:shadow-3xl';
    
    // Get agent-specific colors and icons
    const agentConfig = getAgentConfig(agentName);
    
    section.innerHTML = `
        <!-- Background Pattern -->
        <div class="absolute inset-0 opacity-5">
            <div class="absolute top-0 right-0 w-32 h-32 ${agentConfig.bgColor} rounded-full translate-x-16 -translate-y-16"></div>
            <div class="absolute bottom-0 left-0 w-24 h-24 ${agentConfig.accentColor} rounded-full -translate-x-12 translate-y-12"></div>
        </div>
        
        <!-- Collapsible Header Section -->
        <div class="collapsible-header cursor-pointer relative z-10 bg-gradient-to-r ${agentConfig.gradientFrom} ${agentConfig.gradientTo} p-6 border-b border-white/20 hover:opacity-90 transition-opacity duration-200" 
             onclick="toggleAgentSection('${agentName}')">
            <div class="flex items-center justify-between">
                <!-- Agent Title with Icon -->
                <div class="flex items-center">
                    <div class="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mr-4 shadow-lg">
                        ${agentConfig.icon}
                    </div>
                    <div>
                        <h2 class="text-xl font-bold text-white drop-shadow-sm">${agentName}</h2>
                        <p class="text-white/80 text-sm font-medium">${agentConfig.description}</p>
                    </div>
                </div>
                
                <!-- Right side with Status and Collapse Arrow -->
                <div class="flex items-center space-x-4">
                    <!-- Status Indicator -->
                    <div id="${agentName}StatusIndicator" class="status-indicator flex items-center bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 border border-white/20">
                        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        <span class="text-sm text-white font-medium">Processing...</span>
                    </div>
                    
                    <!-- Collapse/Expand Arrow -->
                    <div class="collapse-arrow transition-transform duration-300 transform" id="${agentName}CollapseArrow">
                        <svg class="w-6 h-6 text-white drop-shadow-sm" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </div>
                </div>
            </div>
            
            <!-- Progress Bar -->
            <div class="mt-4 bg-white/20 rounded-full h-2 overflow-hidden">
                <div class="bg-white h-full rounded-full animate-pulse transition-all duration-1000" style="width: 0%" id="${agentName}ProgressBar"></div>
            </div>
        </div>
        
        <!-- Collapsible Content Section -->
        <div class="collapsible-content max-h-0 overflow-hidden transition-all duration-500 ease-in-out" id="${agentName}Content">
            <div class="relative z-10 p-6">
                <!-- Tabs for Content Views -->
                <div class="flex space-x-1 mb-6 bg-gray-100 rounded-xl p-1">
                    <button class="tab-button active flex-1 text-sm font-medium py-2 px-4 rounded-lg transition-all duration-200 bg-white shadow-sm text-gray-700" 
                            data-tab="formatted" data-agent="${agentName}">
                        <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Formatted
                    </button>
                    <button class="tab-button flex-1 text-sm font-medium py-2 px-4 rounded-lg transition-all duration-200 text-gray-500 hover:text-gray-700" 
                            data-tab="raw" data-agent="${agentName}">
                        <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
                        </svg>
                        Raw Output
                    </button>
                </div>
                
                <!-- Content Container -->
                <div class="content-container">
                    <!-- Formatted Content -->
                    <div class="tab-content active" data-content="formatted" data-agent="${agentName}">
                        <div class="prose max-w-none bg-white/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-200/50 shadow-inner min-h-32" id="${agentName}Output">
                            <!-- Loading Animation -->
                            <div class="flex items-center justify-center py-12">
                                <div class="relative">
                                    <div class="w-12 h-12 border-4 border-gray-200 rounded-full"></div>
                                    <div class="absolute top-0 left-0 w-12 h-12 border-4 ${agentConfig.borderColor} border-t-transparent rounded-full animate-spin"></div>
                                </div>
                                <span class="ml-4 text-gray-600 font-medium">Analyzing...</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Raw Content -->
                    <div class="tab-content hidden" data-content="raw" data-agent="${agentName}">
                        <div class="bg-gray-900 rounded-2xl p-6 border border-gray-700 shadow-inner">
                            <pre class="text-green-400 text-sm font-mono overflow-x-auto whitespace-pre-wrap" id="${agentName}RawOutput">
                                <div class="text-gray-500">Raw output will appear here...</div>
                            </pre>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer with Timestamp -->
            <div class="relative z-10 px-6 pb-4">
                <div class="flex items-center justify-between text-xs text-gray-500">
                    <span id="${agentName}Timestamp" class="flex items-center">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Started processing...
                    </span>
                    <span id="${agentName}Duration" class="opacity-0">Duration: --</span>
                </div>
            </div>
        </div>
    `;
    
    return section;
}

// Get agent-specific configuration (colors, icons, descriptions)
function getAgentConfig(agentName) {
    const configs = {
        'Problem Explorer': {
            gradientFrom: 'from-purple-600',
            gradientTo: 'to-indigo-600',
            bgColor: 'bg-purple-500',
            accentColor: 'bg-indigo-400',
            borderColor: 'border-purple-500',
            description: 'Breaking down the strategic challenge',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>`
        },
        'Best Practices': {
            gradientFrom: 'from-green-600',
            gradientTo: 'to-emerald-600',
            bgColor: 'bg-green-500',
            accentColor: 'bg-emerald-400',
            borderColor: 'border-green-500',
            description: 'Identifying proven solutions and methods',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
            </svg>`
        },
        'Horizon Scanning': {
            gradientFrom: 'from-blue-600',
            gradientTo: 'to-cyan-600',
            bgColor: 'bg-blue-500',
            accentColor: 'bg-cyan-400',
            borderColor: 'border-blue-500',
            description: 'Scanning for emerging trends and signals',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>`
        },
        'Scenario Planning': {
            gradientFrom: 'from-orange-600',
            gradientTo: 'to-red-600',
            bgColor: 'bg-orange-500',
            accentColor: 'bg-red-400',
            borderColor: 'border-orange-500',
            description: 'Exploring possible future scenarios',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>`
        },
        'Research Synthesis': {
            gradientFrom: 'from-teal-600',
            gradientTo: 'to-green-600',
            bgColor: 'bg-teal-500',
            accentColor: 'bg-green-400',
            borderColor: 'border-teal-500',
            description: 'Synthesizing insights and findings',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>`
        },
        'Strategic Action': {
            gradientFrom: 'from-pink-600',
            gradientTo: 'to-purple-600',
            bgColor: 'bg-pink-500',
            accentColor: 'bg-purple-400',
            borderColor: 'border-pink-500',
            description: 'Developing actionable strategies',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>`
        },
        'High Impact': {
            gradientFrom: 'from-yellow-600',
            gradientTo: 'to-orange-600',
            bgColor: 'bg-yellow-500',
            accentColor: 'bg-orange-400',
            borderColor: 'border-yellow-500',
            description: 'Identifying high-impact initiatives',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
            </svg>`
        },
        'Backcasting': {
            gradientFrom: 'from-indigo-600',
            gradientTo: 'to-blue-600',
            bgColor: 'bg-indigo-500',
            accentColor: 'bg-blue-400',
            borderColor: 'border-indigo-500',
            description: 'Working backwards from desired future',
            icon: `<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>`
        }
    };
    
    return configs[agentName] || configs['Problem Explorer']; // Fallback to default
}

// Update section content
function updateSection(sectionId, content) {
    const section = document.querySelector(`[data-section="${sectionId}"]`);
    if (!section) return;

    const loadingIndicator = section.querySelector('.loading-indicator');
    const contentElement = section.querySelector('pre');

    if (loadingIndicator) {
        loadingIndicator.remove();
    }

    if (contentElement) {
        contentElement.textContent = content;
        contentElement.classList.remove('hidden');
    }
}

// Update agent output
function updateAgentOutput(agentName, output) {
    const outputDiv = document.getElementById(`${agentName}Output`);
    const rawOutputDiv = document.getElementById(`${agentName}RawOutput`);
    const timestampSpan = document.getElementById(`${agentName}Timestamp`);
    const durationSpan = document.getElementById(`${agentName}Duration`);
    const progressBar = document.getElementById(`${agentName}ProgressBar`);
    
    if (!outputDiv) {
        console.warn(`Output div not found for ${agentName}`);
        return;
    }

    try {
        // Validate output
        if (!output || typeof output !== 'string') {
            console.warn(`Invalid output for ${agentName}:`, output);
            outputDiv.innerHTML = '<p class="text-red-500">Error: Invalid output format</p>';
            return;
        }

        // Log raw output to console
        console.log(`Raw output for ${agentName}:`, output);

        // Pre-process the output to handle single newlines
        let processedOutput = output
            .replace(/\n\n/g, '|||DOUBLE_NEWLINE|||')
            .replace(/\n/g, '  \n')
            .replace(/\|\|\|DOUBLE_NEWLINE\|\|\|/g, '\n\n');

        // Convert markdown to HTML
        const html = marked.parse(processedOutput);
        if (!html) {
            throw new Error('Markdown parsing failed');
        }

        // Update formatted content
        outputDiv.innerHTML = html;

        // Update raw content
        if (rawOutputDiv) {
            rawOutputDiv.innerHTML = `<div class="text-green-400">${output}</div>`;
        }

        // Update progress bar to 100%
        if (progressBar) {
            progressBar.style.width = '100%';
            progressBar.classList.remove('animate-pulse');
        }

        // Update status indicator
        const statusIndicator = document.getElementById(`${agentName}StatusIndicator`);
        if (statusIndicator) {
            statusIndicator.innerHTML = `
                <div class="w-4 h-4 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                <span class="text-sm text-white font-medium">Completed</span>
            `;
        }

        // Update timestamp
        if (timestampSpan) {
            const now = new Date();
            timestampSpan.innerHTML = `
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Completed at ${now.toLocaleTimeString()}
            `;
        }

        // Show duration (placeholder - you could track actual start time)
        if (durationSpan) {
            durationSpan.classList.remove('opacity-0');
            durationSpan.innerHTML = 'Duration: ~30s'; // Placeholder
        }

        // Add completion animation
        const section = outputDiv.closest('.relative.bg-gradient-to-br');
        if (section) {
            section.classList.add('animate-pulse');
            setTimeout(() => {
                section.classList.remove('animate-pulse');
            }, 1000);
        }

        // Auto-expand this section if it's the first to complete
        autoExpandOnCompletion(agentName);

        // Recalculate height if this section is expanded
        recalculateExpandedHeight(agentName);

    } catch (error) {
        console.error(`Error updating output for ${agentName}:`, error);
        
        // Update with error state
        outputDiv.innerHTML = `
            <div class="text-red-500 bg-red-50 rounded-lg p-4 border border-red-200">
                <div class="flex items-center mb-2">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    <strong class="font-semibold">Error displaying output</strong>
                </div>
                <pre class="text-sm bg-white rounded p-2 mt-2 overflow-x-auto">${output || 'No output available'}</pre>
            </div>
        `;
        
        // Update status to error
        const statusIndicator = document.getElementById(`${agentName}StatusIndicator`);
        if (statusIndicator) {
            statusIndicator.innerHTML = `
                <div class="w-4 h-4 bg-red-400 rounded-full mr-2"></div>
                <span class="text-sm text-white font-medium">Error</span>
            `;
        }
    }
}

// Remove loading state
function removeLoadingState(agentName) {
    const outputDiv = document.getElementById(`${agentName}Output`);
    if (!outputDiv) {
        console.warn(`Output div not found for ${agentName}`);
        return;
    }

    const section = outputDiv.parentElement;
    if (!section) {
        console.warn(`Section not found for ${agentName}`);
        return;
    }

    const loadingDiv = section.querySelector('.flex.items-center');
    if (loadingDiv) {
        loadingDiv.innerHTML = `
            <span class="text-sm text-green-600">Completed</span>
        `;
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4';
    errorDiv.innerHTML = `
        <strong class="font-bold">Error!</strong>
        <span class="block sm:inline">${message}</span>
    `;
    agentOutputs.insertBefore(errorDiv, agentOutputs.firstChild);
}

// Form submission handler
analysisForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Clear previous outputs
    agentOutputs.innerHTML = '';
    
    // Get form data
    const formData = new FormData(e.target);
    const inputData = {
        strategic_question: formData.get('strategic_question'),
        time_frame: formData.get('time_frame'),
        region: formData.get('region'),
        prompt: formData.get('prompt') || undefined
    };
    
    try {
        // Start analysis
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(inputData)
        });
        
        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }
        
        // Create sections for each agent
        const agents = [
            'Problem Explorer',
            'Best Practices',
            'Horizon Scanning',
            'Scenario Planning',
            'Research Synthesis',
            'Strategic Action',
            'High Impact',
            'Backcasting'
        ];
        
        agents.forEach(agent => {
            const section = createAgentOutputSection(agent);
            agentOutputs.appendChild(section);
        });
        
        // Auto-scroll to the analysis results section
        agentOutputs.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
        
        // Process the response stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (!line.trim()) continue;
                
                try {
                    const data = JSON.parse(line);
                    console.log('Received data:', data); // Debug log
                    
                    // Get the first key from the data object (agent name)
                    const agentName = Object.keys(data)[0];
                    if (!agentName) {
                        console.warn('No agent name found in data');
                        continue;
                    }
                    
                    console.log('Processing agent:', agentName); // Debug log
                    const outputDiv = document.getElementById(`${agentName}Output`);
                    if (outputDiv) {
                        const agentData = data[agentName];
                        if (agentData && agentData.data) {
                            updateAgentOutput(agentName, agentData.data.formatted_output || agentData.data.raw_response);
                            removeLoadingState(agentName);
                        } else {
                            console.warn(`No data found for agent: ${agentName}`);
                        }
                    } else {
                        console.warn(`Output div not found for agent: ${agentName}`);
                    }
                } catch (error) {
                    console.error('Error parsing agent output:', error);
                }
            }
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message);
    }
}); 