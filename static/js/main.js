document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const strategic_question = document.getElementById('strategic_question').value;
        const selectedScopes = Array.from(document.querySelectorAll('input[name="scope"]:checked')).map(cb => cb.value);
        const time_frame = document.getElementById('time_frame').value;
        const region = document.getElementById('region').value;
        const prompt = document.getElementById('prompt').value;
        const result = document.getElementById('result');

        // Initialize result sections
        result.innerHTML = `
            <div class="space-y-6">
                <div class="bg-white p-4 rounded-lg shadow" data-section="problem-analysis">
                    <h3 class="text-lg font-semibold mb-2">Problem Analysis</h3>
                    <div class="loading-indicator">Processing...</div>
                    <pre class="whitespace-pre-wrap hidden"></pre>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="best-practices">
                    <h3 class="text-lg font-semibold mb-2">Best Practices</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <pre class="whitespace-pre-wrap hidden"></pre>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="horizon-scan">
                    <h3 class="text-lg font-semibold mb-2">Horizon Scan</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <pre class="whitespace-pre-wrap hidden"></pre>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="scenarios">
                    <h3 class="text-lg font-semibold mb-2">Scenarios</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <pre class="whitespace-pre-wrap hidden"></pre>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="synthesis">
                    <h3 class="text-lg font-semibold mb-2">Synthesis</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <pre class="whitespace-pre-wrap hidden"></pre>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="action-plan">
                    <h3 class="text-lg font-semibold mb-2">Action Plan</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <pre class="whitespace-pre-wrap hidden"></pre>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="initiatives">
                    <h3 class="text-lg font-semibold mb-2">High-Impact Initiatives</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <pre class="whitespace-pre-wrap hidden"></pre>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="prioritized-tasks">
                    <h3 class="text-lg font-semibold mb-2">Prioritized Tasks</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <pre class="whitespace-pre-wrap hidden"></pre>
                </div>
            </div>
        `;
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    strategic_question, 
                    scope: selectedScopes,
                    time_frame, 
                    region, 
                    prompt
                }),
            });
            const data = await response.json();
            
            // Update sections as they complete
            if (data.status === 'success') {
                const resultData = data.data;
                
                // Helper function to format content
                const formatContent = (content) => {
                    if (!content) return 'N/A';
                    
                    if (typeof content === 'string') {
                        return content;
                    }
                    
                    if (Array.isArray(content)) {
                        return content.map(item => {
                            if (typeof item === 'object') {
                                return Object.entries(item)
                                    .map(([key, value]) => `${key}: ${value}`)
                                    .join('\n');
                            }
                            return item;
                        }).join('\n\n');
                    }
                    
                    if (typeof content === 'object') {
                        return Object.entries(content)
                            .map(([key, value]) => {
                                if (Array.isArray(value)) {
                                    return `${key}:\n${value.map(v => `- ${v}`).join('\n')}`;
                                }
                                return `${key}: ${value}`;
                            })
                            .join('\n\n');
                    }
                    
                    return String(content);
                };

                // Update each section with proper formatting
                if (resultData.problem_analysis?.data?.response) {
                    updateSection('problem-analysis', formatContent(resultData.problem_analysis.data.response));
                }
                
                if (resultData.best_practices?.data?.response) {
                    updateSection('best-practices', formatContent(resultData.best_practices.data.response));
                }
                
                if (resultData.horizon_scan?.data?.response) {
                    updateSection('horizon-scan', formatContent(resultData.horizon_scan.data.response));
                }
                
                if (resultData.scenarios?.data?.response) {
                    updateSection('scenarios', formatContent(resultData.scenarios.data.response));
                }
                
                if (resultData.synthesis?.data?.response) {
                    updateSection('synthesis', formatContent(resultData.synthesis.data.response));
                }
                
                if (resultData.action_plan?.data?.response) {
                    updateSection('action-plan', formatContent(resultData.action_plan.data.response));
                }
                
                if (resultData.initiatives?.data?.response) {
                    updateSection('initiatives', formatContent(resultData.initiatives.data.response));
                }
                
                if (resultData.prioritized_tasks?.data?.response) {
                    updateSection('prioritized-tasks', formatContent(resultData.prioritized_tasks.data.response));
                }
            } else {
                result.innerHTML = `<div class="text-red-600">Error: ${data.error || 'Unknown error occurred'}</div>`;
            }
        } catch (error) {
            result.innerHTML = `<div class="text-red-600">Error: ${error.message}</div>`;
        }
    });
});

// Function to update section content
function updateSection(sectionName, content, status = 'completed') {
    const section = document.querySelector(`[data-section="${sectionName}"]`);
    if (section) {
        const loadingIndicator = section.querySelector('.loading-indicator');
        const contentElement = section.querySelector('pre');
        
        if (loadingIndicator) {
            loadingIndicator.textContent = status === 'processing' ? 'Processing...' : 
                                         status === 'waiting' ? 'Waiting...' :
                                         status === 'error' ? 'Error' : 'Completed';
            loadingIndicator.className = `loading-indicator ${status}`;
        }
        
        if (contentElement) {
            contentElement.textContent = content;
            contentElement.classList.remove('hidden');
        }
    }
} 