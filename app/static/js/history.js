// History page functionality
class HistoryManager {
    constructor() {
        this.currentPage = 0;
        this.pageSize = 12;
        this.sessions = [];
        this.totalSessions = 0;
        this.isLoading = false;
        this.currentFilters = {};
        this.hasMore = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadHistory();
    }
    
    initializeElements() {
        this.searchInput = document.getElementById('searchInput');
        this.statusFilter = document.getElementById('statusFilter');
        this.regionFilter = document.getElementById('regionFilter');
        this.applyFiltersBtn = document.getElementById('applyFilters');
        this.clearFiltersBtn = document.getElementById('clearFilters');
        this.historyGrid = document.getElementById('historyGrid');
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.loadMoreSection = document.getElementById('loadMoreSection');
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        this.resultCount = document.getElementById('resultCount');
        this.sessionModal = document.getElementById('sessionModal');
        this.modalContent = document.getElementById('modalContent');
        this.closeModal = document.getElementById('closeModal');
    }
    
    bindEvents() {
        // Filter controls
        this.applyFiltersBtn.addEventListener('click', () => this.applyFilters());
        this.clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        
        // Search on Enter key
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            }
        });
        
        // Load more
        this.loadMoreBtn.addEventListener('click', () => this.loadMoreSessions());
        
        // Modal controls
        this.closeModal.addEventListener('click', () => this.closeSessionModal());
        this.sessionModal.addEventListener('click', (e) => {
            if (e.target === this.sessionModal) {
                this.closeSessionModal();
            }
        });
        
        // Mobile menu toggle
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', function() {
                mobileMenu.classList.toggle('hidden');
            });
        }
    }
    
    async loadHistory(reset = true) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        
        if (reset) {
            this.currentPage = 0;
            this.sessions = [];
            this.historyGrid.innerHTML = '';
            this.showLoading();
        }
        
        try {
            const params = new URLSearchParams({
                limit: this.pageSize,
                offset: this.currentPage * this.pageSize,
                ...this.currentFilters
            });
            
            const response = await fetch(`/api/analysis-history?${params}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const newSessions = data.data.sessions || [];
                this.sessions = reset ? newSessions : [...this.sessions, ...newSessions];
                this.totalSessions = data.data.pagination?.total || this.sessions.length;
                this.hasMore = data.data.pagination?.has_more || false;
                
                this.renderSessions(newSessions, reset);
                this.updateResultCount();
                this.updateLoadMoreButton();
            } else {
                console.error('Failed to load history:', data.message);
                this.showEmptyState();
            }
        } catch (error) {
            console.error('Error loading history:', error);
            this.showEmptyState();
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    async loadMoreSessions() {
        this.currentPage++;
        await this.loadHistory(false);
    }
    
    applyFilters() {
        this.currentFilters = {
            search: this.searchInput.value.trim() || undefined,
            status: this.statusFilter.value || undefined,
            region: this.regionFilter.value || undefined
        };
        
        // Remove undefined values
        Object.keys(this.currentFilters).forEach(key => {
            if (this.currentFilters[key] === undefined) {
                delete this.currentFilters[key];
            }
        });
        
        this.loadHistory(true);
    }
    
    clearFilters() {
        this.searchInput.value = '';
        this.statusFilter.value = '';
        this.regionFilter.value = '';
        this.currentFilters = {};
        this.loadHistory(true);
    }
    
    renderSessions(sessions, reset = true) {
        if (reset) {
            this.historyGrid.innerHTML = '';
        }
        
        if (sessions.length === 0 && reset) {
            this.showEmptyState();
            return;
        }
        
        this.showHistoryGrid();
        
        sessions.forEach(session => {
            const sessionCard = this.createSessionCard(session);
            this.historyGrid.appendChild(sessionCard);
        });
    }
    
    createSessionCard(session) {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer transform hover:scale-105';
        
        const statusColor = this.getStatusColor(session.status);
        const regionDisplay = this.formatRegion(session.region);
        const timeFrameDisplay = this.formatTimeFrame(session.time_frame);
        
        card.innerHTML = `
            <div class="p-6">
                <!-- Header -->
                <div class="flex justify-between items-start mb-4">
                    <div class="flex-1">
                        <h3 class="text-lg font-semibold text-gray-800 line-clamp-2 mb-2">
                            ${this.truncateText(session.strategic_question, 80)}
                        </h3>
                        <div class="flex items-center space-x-2">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor}">
                                ${session.status}
                            </span>
                            <span class="text-xs text-gray-500">
                                Session #${session.id}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Details -->
                <div class="space-y-2 mb-4">
                    <div class="flex items-center text-sm text-gray-600">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        ${regionDisplay}
                    </div>
                    <div class="flex items-center text-sm text-gray-600">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        ${timeFrameDisplay}
                    </div>
                    <div class="flex items-center text-sm text-gray-600">
                        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                        ${session.agent_results_count || 0} agents, ${Math.round(session.completion_rate || 0)}% complete
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="flex justify-between items-center text-xs text-gray-500 pt-4 border-t border-gray-100">
                    <span>${this.formatDate(session.created_at)}</span>
                                            <span class="text-brand-lapis hover:text-brand-oxford font-brand-regular font-medium">
                        View Details →
                    </span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => this.openSessionModal(session.id));
        
        return card;
    }
    
    async openSessionModal(sessionId) {
        try {
            this.sessionModal.classList.remove('hidden');
            this.modalContent.innerHTML = `
                <div class="text-center py-12">
                    <div class="relative inline-block">
                        <div class="w-12 h-12 border-4 border-gray-200 rounded-full"></div>
                        <div class="absolute top-0 left-0 w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                    <p class="mt-4 text-gray-600 font-medium">Loading session details...</p>
                </div>
            `;
            
            // TODO: Implement session detail loading
            setTimeout(() => {
                this.modalContent.innerHTML = `
                    <div class="text-center py-12">
                        <h3 class="text-lg font-semibold text-gray-800 mb-4">Session Details</h3>
                        <p class="text-gray-600 mb-4">Session ID: ${sessionId}</p>
                        <p class="text-sm text-gray-500">Detailed session view coming soon...</p>
                        <p class="text-sm text-gray-500 mt-2">This will show the full analysis results and agent outputs.</p>
                    </div>
                `;
            }, 1000);
            
        } catch (error) {
            console.error('Error loading session details:', error);
        }
    }
    
    closeSessionModal() {
        this.sessionModal.classList.add('hidden');
    }
    
    showLoading() {
        this.loadingState.classList.remove('hidden');
        this.historyGrid.classList.add('hidden');
        this.emptyState.classList.add('hidden');
    }
    
    hideLoading() {
        this.loadingState.classList.add('hidden');
    }
    
    showHistoryGrid() {
        this.historyGrid.classList.remove('hidden');
        this.emptyState.classList.add('hidden');
    }
    
    showEmptyState() {
        this.historyGrid.classList.add('hidden');
        this.emptyState.classList.remove('hidden');
        this.loadMoreSection.classList.add('hidden');
    }
    
    updateResultCount() {
        const displayed = this.sessions.length;
        const total = this.totalSessions;
        this.resultCount.textContent = `Showing ${displayed} of ${total} analyses`;
    }
    
    updateLoadMoreButton() {
        if (this.hasMore && this.sessions.length > 0) {
            this.loadMoreSection.classList.remove('hidden');
        } else {
            this.loadMoreSection.classList.add('hidden');
        }
    }
    
    getStatusColor(status) {
        const colors = {
            'completed': 'bg-green-100 text-green-800',
            'processing': 'bg-yellow-100 text-yellow-800',
            'failed': 'bg-red-100 text-red-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    }
    
    formatRegion(region) {
        const regions = {
            'global': 'Global',
            'north_america': 'North America',
            'europe': 'Europe',
            'asia': 'Asia',
            'africa': 'Africa',
            'latin_america': 'Latin America'
        };
        return regions[region] || region || 'Unknown';
    }
    
    formatTimeFrame(timeFrame) {
        const frames = {
            'short_term': 'Short Term (1-2 years)',
            'medium_term': 'Medium Term (3-5 years)',
            'long_term': 'Long Term (5+ years)'
        };
        return frames[timeFrame] || timeFrame || 'Unknown';
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new HistoryManager();
}); 