// Test script to manually trigger agent output updates
// Run this in browser console to test if updateAgentOutput works

console.log('=== TESTING AGENT OUTPUT UPDATE ===');

// Test data that mimics what should come from the backend
const testAgentData = {
    "Best Practices": {
        "status": "success",
        "data": {
            "formatted_output": "# Best Practices Analysis\n\n### Best Practice 1: Digital Transformation\n**Time Frame:** 2020-2022\n**Organization:** Microsoft\n**Challenge:** Legacy system modernization\n**Problem:** Outdated technology infrastructure\n**Solution:** Cloud-first approach with phased migration\n\nThis is a test to see if the frontend can display agent outputs correctly.",
            "raw_response": "Raw response text here..."
        },
        "agent_type": "BestPracticesAgent"
    }
};

// Simulate the agent processing
const agentName = "Best Practices";
const agentData = testAgentData[agentName];

console.log('Testing with agent:', agentName);
console.log('Agent data:', agentData);

// Check if the output div exists
const outputDiv = document.getElementById(`${agentName}Output`);
console.log('Output div exists:', !!outputDiv);

if (outputDiv && agentData && agentData.status === 'success' && agentData.data) {
    console.log('Conditions met, calling updateAgentOutput...');
    
    const content = agentData.data.formatted_output || 
                   agentData.data.analysis || 
                   agentData.data.response || 
                   JSON.stringify(agentData.data, null, 2);
    
    console.log('Content to display:', content);
    
    // Call the update function (if it exists)
    if (typeof updateAgentOutput === 'function') {
        updateAgentOutput(agentName, content);
        console.log('✅ updateAgentOutput called successfully');
    } else {
        console.log('❌ updateAgentOutput function not found');
    }
    
    // Call remove loading state (if it exists)
    if (typeof removeLoadingState === 'function') {
        removeLoadingState(agentName);
        console.log('✅ removeLoadingState called successfully');
    } else {
        console.log('❌ removeLoadingState function not found');
    }
} else {
    console.log('❌ Conditions not met for updating agent output');
    console.log('  outputDiv exists:', !!outputDiv);
    console.log('  agentData exists:', !!agentData);
    console.log('  status is success:', agentData?.status === 'success');
    console.log('  data exists:', !!agentData?.data);
}

console.log('=== TEST COMPLETE ==='); 