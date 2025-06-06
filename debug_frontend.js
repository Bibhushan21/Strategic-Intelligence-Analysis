// Debug script to run in browser console
// Copy and paste this into the browser console to debug agent output issues

console.log('=== FRONTEND DEBUG SCRIPT ===');

// Check if agents are visible
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

console.log('\n=== AGENT OUTPUT SECTIONS ===');
agents.forEach(agent => {
    const outputDiv = document.getElementById(`${agent}Output`);
    const statusIndicator = document.getElementById(`${agent}StatusIndicator`);
    
    console.log(`\n${agent}:`);
    console.log(`  Output div exists: ${!!outputDiv}`);
    console.log(`  Status indicator exists: ${!!statusIndicator}`);
    
    if (outputDiv) {
        console.log(`  Output content length: ${outputDiv.innerHTML.length}`);
        console.log(`  Output preview: ${outputDiv.innerHTML.substring(0, 100)}...`);
    }
    
    if (statusIndicator) {
        console.log(`  Status HTML: ${statusIndicator.innerHTML}`);
    }
});

// Check analysis results
console.log('\n=== ANALYSIS RESULTS ===');
if (typeof analysisResults !== 'undefined') {
    console.log('Analysis results keys:', Object.keys(analysisResults));
    Object.keys(analysisResults).forEach(key => {
        console.log(`${key}:`, analysisResults[key]);
    });
} else {
    console.log('analysisResults variable not found');
}

// Check analysis completion status
console.log('\n=== COMPLETION STATUS ===');
console.log('analysisCompleted:', typeof analysisCompleted !== 'undefined' ? analysisCompleted : 'undefined');

// Check buttons
console.log('\n=== BUTTONS ===');
const downloadBtn = document.getElementById('downloadPdfBtn');
const saveBtn = document.getElementById('saveAsTemplateBtn');

console.log('Download PDF button:', {
    exists: !!downloadBtn,
    visible: downloadBtn ? downloadBtn.style.display : 'N/A',
    disabled: downloadBtn ? downloadBtn.disabled : 'N/A'
});

console.log('Save Template button:', {
    exists: !!saveBtn,
    visible: saveBtn ? saveBtn.style.display : 'N/A',
    disabled: saveBtn ? saveBtn.disabled : 'N/A'
});

console.log('\n=== DEBUG COMPLETE ==='); 