// DOM Elements
const agentOutputs = document.getElementById('agentOutputs');
const analysisForm = document.getElementById('analysisForm');

// Create agent output section
function createAgentOutputSection(agentName) {
    const section = document.createElement('div');
    section.className = 'bg-white rounded-lg shadow-md p-6';
    section.innerHTML = `
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold">${agentName}</h2>
            <div class="flex items-center">
                <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-2"></div>
                <span class="text-sm text-gray-500">Processing...</span>
            </div>
        </div>
        <div class="prose max-w-none" id="${agentName}Output"></div>
    `;
    return section;
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

        // Convert markdown to HTML
        const html = marked.parse(output);
        if (!html) {
            throw new Error('Markdown parsing failed');
        }

        // Create a container for both formatted and raw output
        const container = document.createElement('div');
        container.className = 'space-y-4';

        // Add formatted output
        const formattedDiv = document.createElement('div');
        formattedDiv.className = 'prose max-w-none';
        formattedDiv.innerHTML = html;
        container.appendChild(formattedDiv);

        // Add raw output section
        const rawDiv = document.createElement('div');
        rawDiv.className = 'mt-4 border-t pt-4';
        rawDiv.innerHTML = `
            <details class="text-sm">
                <summary class="cursor-pointer text-gray-600 hover:text-gray-800">
                    View Raw Output
                </summary>
                <pre class="mt-2 p-4 bg-gray-50 rounded overflow-x-auto">${output}</pre>
            </details>
        `;
        container.appendChild(rawDiv);

        // Clear and update the output div
        outputDiv.innerHTML = '';
        outputDiv.appendChild(container);

    } catch (error) {
        console.error(`Error updating output for ${agentName}:`, error);
        outputDiv.innerHTML = `
            <div class="text-red-500">
                <p>Error displaying output:</p>
                <pre class="mt-2 p-2 bg-red-50 rounded">${output || 'No output available'}</pre>
            </div>
        `;
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