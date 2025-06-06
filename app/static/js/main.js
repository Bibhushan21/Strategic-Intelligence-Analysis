document.addEventListener('DOMContentLoaded', function() {
    // Analysis form is handled by analysis.js - no conflicting handlers here
    console.log('main.js loaded - analysis form handled by analysis.js');
    return; // Exit early to avoid conflicts
    
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
                    <div class="whitespace-pre-wrap hidden"></div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="best-practices">
                    <h3 class="text-lg font-semibold mb-2">Best Practices</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <div class="whitespace-pre-wrap hidden"></div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="horizon-scan">
                    <h3 class="text-lg font-semibold mb-2">Horizon Scan</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <div class="whitespace-pre-wrap hidden"></div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="scenarios">
                    <h3 class="text-lg font-semibold mb-2">Scenarios</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <div class="whitespace-pre-wrap hidden"></div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="synthesis">
                    <h3 class="text-lg font-semibold mb-2">Synthesis</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <div class="whitespace-pre-wrap hidden"></div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="action-plan">
                    <h3 class="text-lg font-semibold mb-2">Action Plan</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <div class="whitespace-pre-wrap hidden"></div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="initiatives">
                    <h3 class="text-lg font-semibold mb-2">High-Impact Initiatives</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <div class="whitespace-pre-wrap hidden"></div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow" data-section="prioritized-tasks">
                    <h3 class="text-lg font-semibold mb-2">Prioritized Tasks</h3>
                    <div class="loading-indicator">Waiting...</div>
                    <div class="whitespace-pre-wrap hidden"></div>
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
                    if (content === null || typeof content === 'undefined') return '<p>N/A</p>';
                    
                    if (typeof content === 'string') {
                        // 1. Escape HTML characters to prevent XSS and conflicts
                        let escapedContent = content.replace(/&/g, '&amp;')
                                                  .replace(/</g, '&lt;')
                                                  .replace(/>/g, '&gt;')
                                                  .replace(/"/g, '&quot;')
                                                  .replace(/'/g, '&#039;');

                        // 2. Replace ## headings with <h3>
                        // Regex: ^##\s+(.+?)\s*$(gm)
                        // ^     - matches the beginning of a line
                        // ##    - matches the literal characters "##"
                        // \s+   - matches one or more whitespace characters (space after ##)
                        // (.+?) - captures the heading text (non-greedy)
                        // \s*$  - matches any trailing whitespace until the end of the line
                        // gm    - global and multiline flags
                        escapedContent = escapedContent.replace(/^##\s+(.+?)\s*$/gm, '<h3>$1</h3>');

                        // 3. Replace **bold** text with <strong>
                        // Regex: \*\*(.+?)\*\*(g)
                        // \*\*  - matches literal "**"
                        // (.+?)  - captures the text to be bolded (non-greedy)
                        // g      - global flag
                        escapedContent = escapedContent.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

                        // 4. Replace newline characters with <br>
                        escapedContent = escapedContent.replace(/\n/g, '<br>');
                        
                        return escapedContent;
                    }
                    
                    // For non-string content (objects, arrays), pretty-print as JSON in a <pre> tag
                    try {
                        return '<pre>' + JSON.stringify(content, null, 2) + '</pre>';
                    } catch (e) {
                        // Fallback for complex objects that can't be stringified (e.g. circular refs)
                        return '<pre>' + String(content) + '</pre>';
                    }
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
        const contentElement = section.querySelector('div.whitespace-pre-wrap');
        
        if (loadingIndicator) {
            loadingIndicator.textContent = status === 'processing' ? 'Processing...' : 
                                         status === 'waiting' ? 'Waiting...' :
                                         status === 'error' ? 'Error' : 'Completed';
            loadingIndicator.className = `loading-indicator ${status}`;
        }
        
        if (contentElement) {
            contentElement.innerHTML = content;
            contentElement.classList.remove('hidden');
        }
    }
} 