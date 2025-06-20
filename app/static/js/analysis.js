// DOM Elements
const agentOutputs = document.getElementById('agentOutputs');
const analysisForm = document.getElementById('analysisForm');
const startAnalysisBtn = document.getElementById('startAnalysisBtn');
const stopAnalysisBtn = document.getElementById('stopAnalysisBtn');

// Button state management
let isAnalysisRunning = false;

// Reset analysis button to ready state
function resetAnalysisButton() {
    isAnalysisRunning = false;
    
    if (startAnalysisBtn) {
        startAnalysisBtn.disabled = false;
        startAnalysisBtn.style.cursor = 'pointer';
        startAnalysisBtn.querySelector('span').innerHTML = `
            <svg class="w-5 h-5 mr-2 group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            Start Analysis
        `;
    }
    
    if (stopAnalysisBtn) {
        stopAnalysisBtn.style.display = 'none';
    }
    
    console.log('Analysis button reset to ready state');
}

function startAnalysis() {
    if (isAnalysisRunning) return;
    isAnalysisRunning = true;
    startAnalysisBtn.disabled = true;
    startAnalysisBtn.style.cursor = 'wait';
    startAnalysisBtn.querySelector('span').innerHTML = `
        <svg class="w-5 h-5 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        Analysis Started...`;
    stopAnalysisBtn.style.display = 'block';
    
    // Always show progress indicator
    showProgressIndicator();
}

function stopAnalysis() {
    if (!isAnalysisRunning) return;
    
    isAnalysisRunning = false;
    startAnalysisBtn.disabled = false;
    startAnalysisBtn.style.cursor = 'pointer';
    startAnalysisBtn.querySelector('span').innerHTML = `
        <svg class="w-5 h-5 mr-2 group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
        </svg>
        Start Analysis
    `;
    stopAnalysisBtn.style.display = 'none';
    
    // Hide progress indicator
    hideProgressIndicator();
}

// Show progress indicator
function showProgressIndicator() {
    const existingIndicator = document.getElementById('progressContainer');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    const progressContainer = document.createElement('div');
    progressContainer.id = 'progressContainer';
    progressContainer.className = 'fixed top-4 right-4 bg-white rounded-lg shadow-lg p-4 z-50 max-w-sm border border-brand-lapis/20';
    progressContainer.innerHTML = `
        <div class="flex items-center space-x-3 mb-3">
            <div class="flex-shrink-0">
                <svg class="w-6 h-6 text-brand-lapis animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
            </div>
            <div class="flex-1 min-w-0">
                <p id="progressIndicator" class="text-sm font-medium text-brand-lapis">Initializing analysis...</p>
                <p id="progressDetails" class="text-xs text-brand-nickel mt-1">Preparing AI agents</p>
            </div>
            <button onclick="hideProgressIndicator()" class="flex-shrink-0 text-brand-nickel hover:text-brand-oxford transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        <div class="mb-3">
            <div class="flex justify-between text-xs text-brand-nickel mb-1">
                <span>Overall Progress</span>
                <span id="progressPercentage">0%</span>
            </div>
            <div class="bg-brand-kodama rounded-full h-2">
                <div id="progressBar" class="bg-gradient-to-r from-brand-lapis to-brand-pervenche h-2 rounded-full transition-all duration-300" style="width: 0%" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        </div>
        <div id="agentProgress" class="space-y-2">
            <div class="text-xs text-brand-nickel font-medium">Agent Status:</div>
            <div id="agentStatusList" class="space-y-1">
                <!-- Agent status items will be added here -->
            </div>
        </div>
    `;
    
    document.body.appendChild(progressContainer);
    
    // Add slide-in animation
    progressContainer.style.opacity = '0';
    progressContainer.style.transform = 'translateX(100%)';
    setTimeout(() => {
        progressContainer.style.transition = 'all 0.3s ease';
        progressContainer.style.opacity = '1';
        progressContainer.style.transform = 'translateX(0)';
    }, 10);
}

// Update progress with more details
function updateProgressDetails(message, details = '') {
    const progressIndicator = document.getElementById('progressIndicator');
    const progressDetails = document.getElementById('progressDetails');
    
    if (progressIndicator) {
        progressIndicator.textContent = message;
    }
    
    if (progressDetails && details) {
        progressDetails.textContent = details;
    }
}

// Update agent status in progress indicator
function updateAgentProgressStatus(agentName, status, progress = 0) {
    const agentStatusList = document.getElementById('agentStatusList');
    if (!agentStatusList) return;
    
    let agentStatusItem = agentStatusList.querySelector(`[data-agent="${agentName}"]`);
    
    if (!agentStatusItem) {
        agentStatusItem = document.createElement('div');
        agentStatusItem.className = 'flex items-center justify-between text-xs';
        agentStatusItem.setAttribute('data-agent', agentName);
        agentStatusList.appendChild(agentStatusItem);
    }
    
    const statusColors = {
        'waiting': 'text-brand-nickel',
        'running': 'text-brand-lapis',
        'completed': 'text-green-600',
        'error': 'text-red-600'
    };
    
    const statusIcons = {
        'waiting': '⏳',
        'running': '🔄',
        'completed': '✅',
        'error': '❌'
    };
    
    agentStatusItem.innerHTML = `
        <span class="flex items-center">
            <span class="mr-2">${statusIcons[status] || '⏳'}</span>
            <span class="font-medium">${agentName.replace(/([A-Z])/g, ' $1').trim()}</span>
        </span>
        <span class="${statusColors[status] || 'text-brand-nickel'}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>
    `;
    
    // Update overall progress
    updateOverallProgress();
}

// Hide progress indicator
function hideProgressIndicator() {
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.transition = 'all 0.3s ease';
        progressContainer.style.opacity = '0';
        progressContainer.style.transform = 'translateX(100%)';
        setTimeout(() => {
            progressContainer.remove();
        }, 300);
    }
}

// Update overall progress based on agent statuses
