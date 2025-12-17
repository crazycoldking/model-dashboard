// AI Model Monitoring Dashboard JavaScript

let allModels = [];
let filteredModels = [];
let currentPage = 1;
const itemsPerPage = 50;

// Load models data
async function loadModels() {
    try {
        const response = await fetch('./data/models.json');
        const data = await response.json();
        allModels = data.models || [];
        
        // Update last updated time
        const lastUpdated = new Date(data.last_updated);
        document.getElementById('last-updated').textContent = formatDate(lastUpdated);
        
        // Initialize filters
        initializeFilters();
        
        // Apply filters and display
        applyFilters();
        
        // Update statistics
        updateStats();
    } catch (error) {
        console.error('Error loading models:', error);
        document.getElementById('models-container').innerHTML = 
            '<div class="no-results">Error loading models. Please try again later.</div>';
    }
}

// Initialize filter options
function initializeFilters() {
    // Get unique platforms
    const platforms = [...new Set(allModels.map(m => m.platform))].sort();
    const platformFilter = document.getElementById('platform-filter');
    platforms.forEach(platform => {
        const option = document.createElement('option');
        option.value = platform;
        option.textContent = platform;
        platformFilter.appendChild(option);
    });
    
    // Get unique task types
    const taskTypes = new Set();
    allModels.forEach(model => {
        if (model.task_types && Array.isArray(model.task_types)) {
            model.task_types.forEach(task => taskTypes.add(task));
        }
    });
    const taskFilter = document.getElementById('task-filter');
    [...taskTypes].sort().forEach(task => {
        const option = document.createElement('option');
        option.value = task;
        option.textContent = task;
        taskFilter.appendChild(option);
    });
    
    // Add event listeners
    document.getElementById('platform-filter').addEventListener('change', applyFilters);
    document.getElementById('status-filter').addEventListener('change', applyFilters);
    document.getElementById('task-filter').addEventListener('change', applyFilters);
    document.getElementById('sort-filter').addEventListener('change', applyFilters);
    document.getElementById('search-input').addEventListener('input', applyFilters);
    
    // Pagination
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayModels();
        }
    });
    document.getElementById('next-page').addEventListener('click', () => {
        const maxPages = Math.ceil(filteredModels.length / itemsPerPage);
        if (currentPage < maxPages) {
            currentPage++;
            displayModels();
        }
    });
}

// Apply all filters
function applyFilters() {
    const platformFilter = document.getElementById('platform-filter').value;
    const statusFilter = document.getElementById('status-filter').value;
    const taskFilter = document.getElementById('task-filter').value;
    const sortFilter = document.getElementById('sort-filter').value;
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    
    // Filter models
    filteredModels = allModels.filter(model => {
        // Platform filter
        if (platformFilter !== 'all' && model.platform !== platformFilter) {
            return false;
        }
        
        // Status filter
        if (statusFilter !== 'all' && model.status !== statusFilter) {
            return false;
        }
        
        // Task type filter
        if (taskFilter !== 'all') {
            if (!model.task_types || !model.task_types.includes(taskFilter)) {
                return false;
            }
        }
        
        // Search filter
        if (searchTerm) {
            const searchableText = `${model.name} ${model.description}`.toLowerCase();
            if (!searchableText.includes(searchTerm)) {
                return false;
            }
        }
        
        return true;
    });
    
    // Sort models
    filteredModels.sort((a, b) => {
        switch (sortFilter) {
            case 'stars':
                return (b.stars || 0) - (a.stars || 0);
            case 'downloads':
                return (b.downloads || 0) - (a.downloads || 0);
            case 'name':
                return (a.name || '').localeCompare(b.name || '');
            case 'updated':
            default:
                return (b.last_updated || '').localeCompare(a.last_updated || '');
        }
    });
    
    // Reset to first page
    currentPage = 1;
    displayModels();
}

// Display models for current page
function displayModels() {
    const container = document.getElementById('models-container');
    
    if (filteredModels.length === 0) {
        container.innerHTML = '<div class="no-results">No models found matching your filters.</div>';
        updatePagination();
        return;
    }
    
    // Calculate pagination
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, filteredModels.length);
    const pageModels = filteredModels.slice(startIndex, endIndex);
    
    // Generate HTML
    container.innerHTML = pageModels.map(model => createModelCard(model)).join('');
    
    // Update pagination
    updatePagination();
}

// Create model card HTML
function createModelCard(model) {
    const statusClass = model.status === 'active' ? 'active' : 'deprecated';
    const taskTags = (model.task_types || ['other']).slice(0, 3).map(task => 
        `<span class="task-tag">${escapeHtml(task)}</span>`
    ).join('');
    
    const updatedDate = model.last_updated ? formatDate(new Date(model.last_updated)) : 'N/A';
    
    return `
        <div class="model-card">
            <div class="model-header">
                <div>
                    <div class="model-name">${escapeHtml(model.name)}</div>
                    <span class="model-status ${statusClass}">${model.status}</span>
                </div>
                <span class="model-platform">${escapeHtml(model.platform)}</span>
            </div>
            
            ${model.description ? `<div class="model-description">${escapeHtml(model.description)}</div>` : ''}
            
            <div class="model-tasks">${taskTags}</div>
            
            <div class="model-meta">
                <div class="meta-item">
                    <strong>Updated:</strong> ${updatedDate}
                </div>
                ${model.version !== 'N/A' ? `<div class="meta-item"><strong>Version:</strong> ${escapeHtml(model.version)}</div>` : ''}
            </div>
            
            <div class="model-stats">
                ${model.stars > 0 ? `<div class="stat-item">⭐ ${formatNumber(model.stars)}</div>` : ''}
                ${model.downloads > 0 ? `<div class="stat-item">📥 ${formatNumber(model.downloads)}</div>` : ''}
            </div>
            
            <div class="model-links">
                ${model.documentation_url ? `<a href="${escapeHtml(model.documentation_url)}" target="_blank" rel="noopener" class="model-link">View Model</a>` : ''}
            </div>
        </div>
    `;
}

// Update statistics
function updateStats() {
    const totalModels = allModels.length;
    const activeModels = allModels.filter(m => m.status === 'active').length;
    const deprecatedModels = allModels.filter(m => m.status === 'deprecated').length;
    
    document.getElementById('total-models').textContent = totalModels;
    document.getElementById('active-models').textContent = activeModels;
    document.getElementById('deprecated-models').textContent = deprecatedModels;
}

// Update pagination controls
function updatePagination() {
    const maxPages = Math.ceil(filteredModels.length / itemsPerPage);
    const pageInfo = document.getElementById('page-info');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    pageInfo.textContent = `Page ${currentPage} of ${maxPages || 1} (${filteredModels.length} models)`;
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage >= maxPages;
}

// Utility functions
function formatDate(date) {
    if (!date || isNaN(date.getTime())) return 'N/A';
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 1) return 'Today';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', loadModels);
