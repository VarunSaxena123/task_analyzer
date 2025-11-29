// Global state
let tasks = [];
let currentTaskId = 1;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 Initializing Smart Task Analyzer...");
    
    // Set up event listeners
    document.getElementById('taskForm').addEventListener('submit', addTaskFromForm);
    document.getElementById('taskImportance').addEventListener('input', function() {
        document.getElementById('importanceValue').textContent = this.value;
    });
    
    // Set today's date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('taskDueDate').value = today;
    document.getElementById('taskDueDate').min = today;
    
    updateDisplay();
    loadSampleData();
});

function addTaskFromForm(event) {
    event.preventDefault();
    
    const task = {
        id: currentTaskId++,
        title: document.getElementById('taskTitle').value.trim(),
        due_date: document.getElementById('taskDueDate').value,
        estimated_hours: parseInt(document.getElementById('taskHours').value) || 1,
        importance: parseInt(document.getElementById('taskImportance').value) || 5,
        dependencies: getDependenciesArray()
    };
    
    if (!task.title) {
        showMessage('Please enter a task title', 'error');
        return;
    }
    
    tasks.push(task);
    updateDisplay();
    
    // Reset form
    document.getElementById('taskForm').reset();
    document.getElementById('taskDueDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('importanceValue').textContent = '5';
    
    showMessage('Task added successfully!', 'success');
}

function getDependenciesArray() {
    const depsInput = document.getElementById('taskDependencies').value;
    return depsInput ? depsInput.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id)) : [];
}

function loadSampleData() {
    console.log("Loading sample data...");
    const sampleData = [
        {
            "title": "Fix critical login bug",
            "due_date": new Date(Date.now() + 86400000).toISOString().split('T')[0],
            "estimated_hours": 3,
            "importance": 9,
            "dependencies": []
        },
        {
            "title": "Write API documentation",
            "due_date": new Date(Date.now() + 259200000).toISOString().split('T')[0],
            "estimated_hours": 2,
            "importance": 6,
            "dependencies": [1]
        },
        {
            "title": "Setup production deployment",
            "due_date": new Date(Date.now() + 172800000).toISOString().split('T')[0],
            "estimated_hours": 4,
            "importance": 8,
            "dependencies": []
        }
    ];
    
    sampleData.forEach((task, index) => {
        task.id = currentTaskId + index;
    });
    currentTaskId += sampleData.length;
    
    tasks = sampleData;
    updateDisplay();
    showMessage('Sample data loaded! Click "Analyze Tasks" to see prioritization.', 'success');
}

function updateDisplay() {
    // Update task count
    document.getElementById('taskCount').textContent = tasks.length;
    
    // Update tasks list
    const tasksList = document.getElementById('tasksList');
    if (tasks.length === 0) {
        tasksList.innerHTML = '<p>No tasks added yet.</p>';
    } else {
        tasksList.innerHTML = tasks.map(task => `
            <div class="task-item">
                <strong>${task.title}</strong><br>
                Due: ${task.due_date} | Hours: ${task.estimated_hours} | Importance: ${task.importance}/10
                ${task.dependencies.length ? `| Depends on: ${task.dependencies.join(', ')}` : ''}
                <button onclick="removeTask(${task.id})" class="remove-btn">Remove</button>
            </div>
        `).join('');
    }
    
    // Update JSON input
    document.getElementById('jsonInput').value = JSON.stringify(tasks, null, 2);
}

function removeTask(taskId) {
    tasks = tasks.filter(task => task.id !== taskId);
    updateDisplay();
    showMessage('Task removed!', 'success');
}

function processBulkJson() {
    const jsonInput = document.getElementById('jsonInput').value.trim();
    if (!jsonInput) {
        showMessage('Please enter JSON data', 'error');
        return;
    }
    
    try {
        const parsed = JSON.parse(jsonInput);
        if (!Array.isArray(parsed)) {
            throw new Error('JSON must be an array');
        }
        
        tasks = parsed.map((task, index) => ({
            id: task.id || currentTaskId + index,
            title: task.title || `Task ${index + 1}`,
            due_date: task.due_date || new Date().toISOString().split('T')[0],
            estimated_hours: parseInt(task.estimated_hours) || 1,
            importance: Math.max(1, Math.min(10, parseInt(task.importance) || 5)),
            dependencies: task.dependencies || []
        }));
        
        currentTaskId = Math.max(...tasks.map(t => t.id)) + 1;
        updateDisplay();
        showMessage('JSON processed successfully!', 'success');
        
    } catch (error) {
        showMessage('Invalid JSON: ' + error.message, 'error');
    }
}

function clearTasks() {
    tasks = [];
    currentTaskId = 1;
    updateDisplay();
    clearResults();
    showMessage('All tasks cleared!', 'success');
}

function clearResults() {
    document.getElementById('priorityList').innerHTML = '';
    document.getElementById('suggestions').classList.add('hidden');
    document.getElementById('suggestionsList').innerHTML = '';
    hideMessage();
}

// API Functions
async function analyzeTasks() {
    if (tasks.length === 0) {
        showMessage('Please add some tasks first', 'error');
        return;
    }
    
    const strategy = document.getElementById('strategySelect').value;
    
    try {
        showLoading(true);
        clearResults();
        hideMessage();
        
        console.log('Sending POST request to /api/tasks/analyze/');
        
        const response = await fetch('/api/tasks/analyze/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            // Handle HTML error responses
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/html')) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status} - ${response.statusText}`);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
        }
        
        const data = await response.json();
        console.log('Analysis successful:', data);
        
        displayResults(data.tasks);
        showMessage(`✅ Successfully analyzed ${data.total_tasks} tasks!`, 'success');
        
    } catch (error) {
        console.error('Analysis failed:', error);
        showMessage('Analysis failed: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function getSuggestions() {
    try {
        showLoading(true);
        hideMessage();
        
        console.log('Sending GET request to /api/tasks/suggest/');
        
        const response = await fetch('/api/tasks/suggest/');
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            // Handle HTML error responses
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/html')) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status} - ${response.statusText}`);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
        }
        
        const data = await response.json();
        console.log('Suggestions received:', data);
        
        displaySuggestions(data.suggestions);
        showMessage('✅ Suggestions loaded!', 'success');
        
    } catch (error) {
        console.error('Suggestions failed:', error);
        showMessage('Suggestions failed: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function displayResults(scoredTasks) {
    const priorityList = document.getElementById('priorityList');
    
    priorityList.innerHTML = `
        <h3>Analysis Results</h3>
        <p>Total tasks: ${scoredTasks.length}</p>
        <div class="tasks-container">
            ${scoredTasks.map((task, index) => `
                <div class="priority-item ${getPriorityClass(task.priority_score)}">
                    <div class="priority-header">
                        <span class="rank">#${index + 1}</span>
                        <strong>${task.title}</strong>
                        <span class="score">${task.priority_score}</span>
                    </div>
                    <div class="explanation">${task.explanation}</div>
                    <div class="details">
                        Due: ${task.due_date} | Hours: ${task.estimated_hours} | Importance: ${task.importance}/10
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function displaySuggestions(suggestions) {
    const suggestionsDiv = document.getElementById('suggestions');
    const suggestionsList = document.getElementById('suggestionsList');
    
    suggestionsDiv.classList.remove('hidden');
    suggestionsList.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-item">
            <h4>#${suggestion.rank}: ${suggestion.title}</h4>
            <p><strong>Score:</strong> ${suggestion.priority_score}</p>
            <p><strong>Reason:</strong> ${suggestion.reason}</p>
            <div class="suggestion-meta">
                <span>Due: ${suggestion.due_date}</span>
                <span>Effort: ${suggestion.estimated_hours}h</span>
                <span>Importance: ${suggestion.importance}/10</span>
            </div>
        </div>
    `).join('');
}

// Utility functions
function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('error');
    messageDiv.textContent = message;
    messageDiv.className = type;
    messageDiv.classList.remove('hidden');
    
    if (type === 'success') {
        setTimeout(hideMessage, 5000);
    }
}

function hideMessage() {
    document.getElementById('error').classList.add('hidden');
}

function getPriorityClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

// Make functions globally available
window.loadSampleData = loadSampleData;
window.processBulkJson = processBulkJson;
window.clearTasks = clearTasks;
window.removeTask = removeTask;
window.analyzeTasks = analyzeTasks;
window.getSuggestions = getSuggestions;