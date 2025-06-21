/**
 * Simple Agent Rating System
 * Single review button that opens agent selection form
 */

class AgentRatingSystem {
    constructor() {
        this.ratings = new Map();
        this.currentUserId = 'anonymous';
        this.ratingEndpoint = '/ratings';
        
        // Initialize when DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }

    /**
     * Initialize the rating system
     */
    initialize() {
        // Try to add button immediately
        this.addReviewButton();
        
        // Try again after 2 seconds (for dynamic content)
        setTimeout(() => {
            this.addReviewButton();
        }, 2000);
        
        // Try again after 5 seconds
        setTimeout(() => {
            this.addReviewButton();
        }, 5000);
        
        // Listen for analysis completion events
        this.listenForAnalysisCompletion();
    }

    /**
     * Listen for analysis completion to add button
     */
    listenForAnalysisCompletion() {
        // Listen for custom events that might indicate analysis completion
        document.addEventListener('analysisCompleted', () => {
            setTimeout(() => this.addReviewButton(), 1000);
        });
        
        // Also check periodically if buttons container becomes available
        const checkInterval = setInterval(() => {
            const buttonContainer = document.querySelector('.flex.flex-wrap.justify-center.gap-4');
            const downloadBtn = document.getElementById('downloadPdfBtn');
            const saveBtn = document.getElementById('saveAsTemplateBtn');
            
            // If we can see the action buttons and they're visible, try adding review button
            if (buttonContainer && (downloadBtn || saveBtn)) {
                const downloadVisible = downloadBtn && downloadBtn.style.display !== 'none';
                const saveVisible = saveBtn && saveBtn.style.display !== 'none';
                
                if (downloadVisible || saveVisible) {
                    this.addReviewButton();
                    
                    // Stop checking once we've found the buttons
                    if (document.querySelector('.main-review-btn')) {
                        clearInterval(checkInterval);
                    }
                }
            }
        }, 2000); // Check every 2 seconds
        
        // Stop checking after 30 seconds to avoid infinite checking
        setTimeout(() => {
            clearInterval(checkInterval);
        }, 30000);
    }

    /**
     * Add single review button to the action buttons container
     */
    addReviewButton() {
        // Target the specific button container
        const buttonContainer = document.querySelector('.flex.flex-wrap.justify-center.gap-4');
        
        if (!buttonContainer) {
            // Alternative selectors
            const altContainer = document.querySelector('[data-step="6"] .flex.gap-4') ||
                                document.getElementById('saveAsTemplateBtn')?.parentElement ||
                                document.querySelector('.flex.justify-center.pt-6 .flex') ||
                                document.querySelector('div.flex.flex-wrap.justify-center') ||
                                document.querySelector('.flex.gap-4') ||
                                document.querySelector('[data-step="6"]');
            
            if (altContainer) {
                this.createAndInsertReviewButton(altContainer);
            }
            return;
        }

        // Create review button in the same container
        this.createAndInsertReviewButton(buttonContainer);
    }

    /**
     * Create and insert the review button
     */
    createAndInsertReviewButton(container, referenceElement = null) {
        // Check if review button already exists
        if (container.querySelector('.main-review-btn')) {
            return;
        }

        const reviewButton = document.createElement('button');
        reviewButton.type = 'button';
        reviewButton.className = 'main-review-btn group relative bg-gradient-to-r from-brand-lapis to-brand-pervenche text-white font-brand-black font-bold px-8 py-4 rounded-2xl hover:from-brand-oxford hover:to-brand-lapis focus:outline-none focus:ring-4 focus:ring-brand-lapis/30 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 text-lg';
        reviewButton.style.display = 'inline-flex';
        
        reviewButton.innerHTML = `
            <span class="flex items-center">
                <svg class="w-5 h-5 mr-2 group-hover:animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
                </svg>
                Review Analysis
            </span>
            <!-- Hover effect overlay -->
            <div class="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        `;
        
        reviewButton.onclick = () => this.showReviewModal();
        
        // Add button to the container (it will appear alongside the other buttons)
        container.appendChild(reviewButton);
    }

    /**
     * Show review modal with agent selection
     */
    showReviewModal() {
        // Remove existing modal if any
        const existingModal = document.getElementById('reviewModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Get list of completed agents
        const agents = this.getCompletedAgents();
        
        // Create modal
        const modal = this.createReviewModal(agents);
        document.body.appendChild(modal);
    }

    /**
     * Get list of completed agents from the page
     */
    getCompletedAgents() {
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
        
        // Filter to only show agents that are actually completed on the page
        return agents.filter(agent => {
            const text = document.body.textContent.toLowerCase();
            return text.includes(agent.toLowerCase()) && text.includes('completed');
        });
    }

    /**
     * Create review modal HTML
     */
    createReviewModal(agents) {
        const modal = document.createElement('div');
        modal.id = 'reviewModal';
        modal.className = 'review-modal-overlay';
        
        modal.innerHTML = `
            <div class="review-modal">
                <div class="review-modal-header">
                    <h2>Review Analysis</h2>
                    <button class="modal-close" onclick="this.closest('.review-modal-overlay').remove()">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
                
                <div class="review-modal-content">
                    <p>Select the agents you want to review:</p>
                    
                    <div class="agent-selection">
                        ${agents.map(agent => `
                            <label class="agent-option">
                                <input type="checkbox" value="${agent}" class="agent-checkbox">
                                <span class="agent-name">${agent}</span>
                            </label>
                        `).join('')}
                    </div>
                    
                    <div class="review-form" id="reviewForm" style="display: none;">
                        <div class="form-group">
                            <label class="form-label">Overall Rating *</label>
                            <div class="star-rating">
                                ${[1, 2, 3, 4, 5].map(i => `
                                    <span class="star" data-rating="${i}" onclick="AgentRating.selectRating(this, ${i})">★</span>
                                `).join('')}
                                <span class="rating-value">Select a rating</span>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Review</label>
                            <textarea class="form-textarea" placeholder="Share your thoughts about the selected agents..." rows="4"></textarea>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Suggestions for improvement</label>
                            <textarea class="form-textarea" placeholder="How could the analysis be improved?" rows="3"></textarea>
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button class="btn-cancel" onclick="this.closest('.review-modal-overlay').remove()">Cancel</button>
                        <button class="btn-next" onclick="AgentRating.showReviewForm()">Next</button>
                        <button class="btn-submit" onclick="AgentRating.submitModalReview()" style="display: none;">Submit Review</button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }

    /**
     * Show review form after agent selection
     */
    static showReviewForm() {
        const selectedAgents = Array.from(document.querySelectorAll('.agent-checkbox:checked'));
        
        if (selectedAgents.length === 0) {
            alert('Please select at least one agent to review.');
            return;
        }
        
        // Show review form
        document.getElementById('reviewForm').style.display = 'block';
        
        // Update buttons
        document.querySelector('.btn-next').style.display = 'none';
        document.querySelector('.btn-submit').style.display = 'inline-block';
        
        // Update form title
        const selectedNames = selectedAgents.map(cb => cb.value).join(', ');
        document.querySelector('.review-modal h2').textContent = `Review: ${selectedNames}`;
    }

    /**
     * Handle star rating selection
     */
    static selectRating(starElement, rating) {
        const modal = starElement.closest('.review-modal-overlay');
        const container = starElement.closest('.review-modal');
        const stars = container.querySelectorAll('.star');
        const ratingValue = container.querySelector('.rating-value');

        // Update visual state
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('filled');
            } else {
                star.classList.remove('filled');
            }
        });

        // Update rating value display
        const ratingText = rating === 1 ? 'Poor' : 
                          rating === 2 ? 'Fair' : 
                          rating === 3 ? 'Good' : 
                          rating === 4 ? 'Very Good' : 'Excellent';
        ratingValue.textContent = `${rating}/5 - ${ratingText}`;

        // Store selected rating on the modal overlay (the element we query later)
        modal.setAttribute('data-selected-rating', rating);

        // Enable submit button
        const submitBtn = container.querySelector('.btn-submit');
        if (submitBtn) {
            submitBtn.disabled = false;
        }
    }

    /**
     * Submit modal review
     */
    static async submitModalReview() {
        const modal = document.getElementById('reviewModal');
        const selectedAgents = Array.from(modal.querySelectorAll('.agent-checkbox:checked')).map(cb => cb.value);
        const rating = parseInt(modal.getAttribute('data-selected-rating'));
        const review = modal.querySelector('.form-textarea').value;
        const suggestions = modal.querySelectorAll('.form-textarea')[1]?.value || '';
        
        if (!rating || rating === 0 || isNaN(rating)) {
            alert('Please select a rating');
            return;
        }

        try {
            // Get current session ID from URL or generate one
            const sessionId = AgentRatingSystem.getCurrentSessionId();
            
            // Submit individual ratings for each selected agent
            const submissionPromises = selectedAgents.map(async (agentName) => {
                const ratingData = {
                    session_id: sessionId,
                    agent_result_id: AgentRatingSystem.generateAgentResultId(agentName, sessionId),
                    agent_name: agentName,
                    rating: rating,
                    review_text: review || null,
                    helpful_aspects: null, // Could be expanded later
                    improvement_suggestions: suggestions || null,
                    would_recommend: rating >= 4, // 4 or 5 stars = recommend
                    user_id: "anonymous"
                };

                const response = await fetch('/ratings/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(ratingData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`Failed to submit rating for ${agentName}: ${errorData.detail}`);
                }

                return response.json();
            });

            // Wait for all submissions to complete
            await Promise.all(submissionPromises);
            
            AgentRatingSystem.showSuccessMessage('Review submitted successfully!', 'Thank you for your feedback!');
            modal.remove();
            
        } catch (error) {
            console.error('Error submitting review:', error);
            AgentRatingSystem.showErrorMessage('Failed to submit review', error.message || 'Please try again.');
        }
    }

    /**
     * Get current session ID from URL or generate one
     */
    static getCurrentSessionId() {
        // Try to get session ID from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const sessionId = urlParams.get('session_id');
        
        if (sessionId) {
            return parseInt(sessionId);
        }
        
        // Try to get from current analysis session (if available)
        if (window.currentSessionId) {
            return window.currentSessionId;
        }
        
        // Generate a temporary session ID based on timestamp
        return Date.now();
    }

    /**
     * Generate agent result ID (temporary implementation)
     */
    static generateAgentResultId(agentName, sessionId) {
        // Create a simple hash-like ID based on agent name and session
        const agentHash = agentName.replace(/\s+/g, '').toLowerCase();
        const baseId = sessionId.toString().slice(-4); // Last 4 digits of session ID
        const agentCode = agentHash.charCodeAt(0) + agentHash.charCodeAt(agentHash.length - 1);
        
        return parseInt(`${baseId}${agentCode}`);
    }

    /**
     * Show success message popup
     */
    static showSuccessMessage(title, message) {
        const overlay = document.createElement('div');
        overlay.className = 'success-popup-overlay';
        
        const popup = document.createElement('div');
        popup.className = 'success-popup';
        popup.innerHTML = `
            <span class="success-popup-icon">✅</span>
            <div class="success-popup-title">${title}</div>
            <div class="success-popup-message">${message}</div>
        `;
        
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            overlay.remove();
        }, 3000);
        
        // Remove on click
        overlay.addEventListener('click', () => {
            overlay.remove();
        });
    }

    /**
     * Show error message popup
     */
    static showErrorMessage(title, message) {
        const overlay = document.createElement('div');
        overlay.className = 'success-popup-overlay';
        
        const popup = document.createElement('div');
        popup.className = 'success-popup';
        popup.style.background = 'linear-gradient(135deg, #f56565, #e53e3e)';
        popup.innerHTML = `
            <span class="success-popup-icon">❌</span>
            <div class="success-popup-title">${title}</div>
            <div class="success-popup-message">${message}</div>
        `;
        
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            overlay.remove();
        }, 4000);
        
        // Remove on click
        overlay.addEventListener('click', () => {
            overlay.remove();
        });
    }
}

// Initialize global instance
document.addEventListener('DOMContentLoaded', () => {
    const ratingSystem = new AgentRatingSystem();
    ratingSystem.initialize();
    
    // Store global reference
    window.AgentRating = window.AgentRating || {};
    window.AgentRating.instance = ratingSystem;
    window.AgentRating.addReviewButton = () => ratingSystem.addReviewButton();
    window.AgentRating.selectRating = AgentRatingSystem.selectRating;
    window.AgentRating.showReviewForm = AgentRatingSystem.showReviewForm;
    window.AgentRating.submitModalReview = AgentRatingSystem.submitModalReview;
});

// Global function to manually add review button (can be called from console or other scripts)
window.addReviewButton = function() {
    if (window.AgentRating && window.AgentRating.addReviewButton) {
        window.AgentRating.addReviewButton();
    }
};

// Function to be called when analysis completes
window.onAnalysisComplete = function() {
    if (window.AgentRating && window.AgentRating.addReviewButton) {
        // Wait a bit for DOM to update
        setTimeout(() => {
            window.AgentRating.addReviewButton();
        }, 500);
    }
}; 