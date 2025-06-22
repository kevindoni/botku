// Dashboard JavaScript
class YouTubeDashboard {
    constructor() {
        this.isStreaming = false;
        this.commentBotRunning = false;
        this.viewerBotRunning = false;
        this.chart = null;
        this.updateInterval = null;
        this.socket = null;
        
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.initChart();
        this.startDataUpdates();
        this.checkSystemStatus();
    }
    
    setupWebSocket() {
        // Initialize Socket.IO connection
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
            this.socket.emit('request_status');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('system_status', (data) => {
            this.updateDashboard(data);
        });
        
        this.socket.on('status', (data) => {
            console.log('Status update:', data.message);
        });
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            indicator.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }
    
    updateDashboard(status) {
        try {
            // Update stream status
            if (status.stream) {
                this.isStreaming = status.stream.status;
                this.updateStreamStatus(status.stream);
            }
            
            // Update bot status
            if (status.bots) {
                this.updateBotStatus(status.bots);
            }
            
            // Update scheduler status
            if (status.scheduler) {
                this.updateSchedulerStatus(status.scheduler);
            }
            
            // Update timestamp
            if (status.timestamp) {
                const lastUpdate = document.getElementById('last-update');
                if (lastUpdate) {
                    lastUpdate.textContent = new Date(status.timestamp).toLocaleTimeString();
                }
            }
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }
    
    updateStreamStatus(streamData) {
        const statusElement = document.getElementById('stream-status');
        const uptimeElement = document.getElementById('stream-uptime');
        const startBtn = document.getElementById('start-stream-btn');
        const stopBtn = document.getElementById('stop-stream-btn');
        
        if (statusElement) {
            statusElement.textContent = streamData.status ? 'LIVE' : 'OFFLINE';
            statusElement.className = `status ${streamData.status ? 'live' : 'offline'}`;
        }
        
        if (uptimeElement && streamData.uptime) {
            uptimeElement.textContent = this.formatUptime(streamData.uptime);
        }
        
        // Update button states
        if (startBtn && stopBtn) {
            startBtn.disabled = streamData.status;
            stopBtn.disabled = !streamData.status;
        }
    }
      updateBotStatus(botsData) {
        // Update comment bot
        if (botsData.comment_bot) {
            const commentBotStatus = document.getElementById('comment-bot-status');
            const commentCount = document.getElementById('comments-posted');
            const toggleCommentBtn = document.getElementById('toggle-comment-bot');
            
            if (commentBotStatus) {
                commentBotStatus.textContent = botsData.comment_bot.active ? 'ACTIVE' : 'STOPPED';
                commentBotStatus.className = `badge ${botsData.comment_bot.active ? 'bg-success' : 'bg-secondary'}`;
            }
            
            if (commentCount) {
                commentCount.textContent = botsData.comment_bot.comments_sent || 0;
            }
            
            if (toggleCommentBtn) {
                toggleCommentBtn.innerHTML = `<i class="fas fa-comment"></i> ${botsData.comment_bot.active ? 'Stop Comment Bot' : 'Start Comment Bot'}`;
                toggleCommentBtn.className = `btn w-100 mb-2 ${botsData.comment_bot.active ? 'btn-danger' : 'btn-info'}`;
            }
            
            this.commentBotRunning = botsData.comment_bot.active;
        }
        
        // Update viewer bot
        if (botsData.viewer_bot) {
            const viewerBotStatus = document.getElementById('viewer-bot-status');
            const viewerCount = document.getElementById('bot-viewers');
            const toggleViewerBtn = document.getElementById('toggle-viewer-bot');
            
            if (viewerBotStatus) {
                viewerBotStatus.textContent = botsData.viewer_bot.active ? 'ACTIVE' : 'STOPPED';
                viewerBotStatus.className = `badge ${botsData.viewer_bot.active ? 'bg-success' : 'bg-secondary'}`;
            }
            
            if (viewerCount) {
                viewerCount.textContent = botsData.viewer_bot.active_viewers || 0;
            }
            
            if (toggleViewerBtn) {
                toggleViewerBtn.innerHTML = `<i class="fas fa-eye"></i> ${botsData.viewer_bot.active ? 'Stop Viewer Bot' : 'Start Viewer Bot'}`;
                toggleViewerBtn.className = `btn w-100 mb-2 ${botsData.viewer_bot.active ? 'btn-danger' : 'btn-secondary'}`;
            }
            
            this.viewerBotRunning = botsData.viewer_bot.active;
        }
    }
      updateSchedulerStatus(schedulerData) {
        const schedulerStatus = document.getElementById('scheduler-status');
        if (schedulerStatus) {
            schedulerStatus.textContent = schedulerData.running ? 'RUNNING' : 'STOPPED';
            schedulerStatus.className = `badge ${schedulerData.running ? 'bg-success' : 'bg-secondary'}`;
        }
    }
    
    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    setupEventListeners() {
        // Stream Control Buttons
        document.getElementById('start-stream-btn').addEventListener('click', () => {
            this.startStream();
        });
        
        document.getElementById('stop-stream-btn').addEventListener('click', () => {
            this.stopStream();
        });
        
        document.getElementById('restart-stream-btn').addEventListener('click', () => {
            this.restartStream();
        });
        
        // Bot Control Buttons
        document.getElementById('toggle-comment-bot').addEventListener('click', () => {
            this.toggleCommentBot();
        });
        
        document.getElementById('toggle-viewer-bot').addEventListener('click', () => {
            this.toggleViewerBot();
        });
    }
    
    async startStream() {
        try {
            this.showLoading('start-stream-btn');
            
            const response = await fetch('/api/stream/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isStreaming = true;
                this.updateStreamStatus(true);
                this.showNotification('Stream started successfully!', 'success');
                this.addActivity('Stream started');
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Network error: ${error.message}`, 'error');
        } finally {
            this.hideLoading('start-stream-btn');
        }
    }
    
    async stopStream() {
        try {
            this.showLoading('stop-stream-btn');
            
            const response = await fetch('/api/stream/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isStreaming = false;
                this.updateStreamStatus(false);
                this.showNotification('Stream stopped successfully!', 'warning');
                this.addActivity('Stream stopped');
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Network error: ${error.message}`, 'error');
        } finally {
            this.hideLoading('stop-stream-btn');
        }
    }
    
    async restartStream() {
        await this.stopStream();
        setTimeout(() => {
            this.startStream();
        }, 3000);
    }
    
    async toggleCommentBot() {
        try {
            const response = await fetch('/api/bot/comments/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.commentBotRunning = result.status === 'started';
                this.updateBotStatus('comment', this.commentBotRunning);
                this.showNotification(`Comment bot ${result.status}!`, 'info');
                this.addActivity(`Comment bot ${result.status}`);
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Network error: ${error.message}`, 'error');
        }
    }
    
    async toggleViewerBot() {
        try {
            const response = await fetch('/api/bot/viewers/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.viewerBotRunning = result.status === 'started';
                this.updateBotStatus('viewer', this.viewerBotRunning);
                this.showNotification(`Viewer bot ${result.status}!`, 'info');
                this.addActivity(`Viewer bot ${result.status}`);
            } else {
                this.showNotification(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Network error: ${error.message}`, 'error');
        }
    }
    
    updateStreamStatus(isStreaming) {
        const statusElement = document.getElementById('stream-status');
        const startBtn = document.getElementById('start-stream-btn');
        const stopBtn = document.getElementById('stop-stream-btn');
        const restartBtn = document.getElementById('restart-stream-btn');
        
        if (isStreaming) {
            statusElement.innerHTML = '<span class="text-success"><i class="fas fa-circle"></i> Live</span>';
            startBtn.disabled = true;
            stopBtn.disabled = false;
            restartBtn.disabled = false;
        } else {
            statusElement.innerHTML = '<span class="text-danger"><i class="fas fa-circle"></i> Offline</span>';
            startBtn.disabled = false;
            stopBtn.disabled = true;
            restartBtn.disabled = true;
        }
    }
    
    updateBotStatus(botType, isRunning) {
        const statusElement = document.getElementById(`${botType}-bot-status`);
        
        if (isRunning) {
            statusElement.className = 'badge bg-success';
            statusElement.textContent = 'Running';
        } else {
            statusElement.className = 'badge bg-secondary';
            statusElement.textContent = 'Stopped';
        }
    }
    
    async updateDashboardData() {
        try {
            // Get stream status
            const streamResponse = await fetch('/api/stream/status');
            const streamData = await streamResponse.json();
            
            // Get analytics
            const analyticsResponse = await fetch('/api/analytics');
            const analyticsData = await analyticsResponse.json();
            
            // Update UI elements
            this.updateStreamInfo(streamData);
            this.updateAnalytics(analyticsData);
            this.updateChart(analyticsData);
            
        } catch (error) {
            console.error('Error updating dashboard data:', error);
        }
    }
    
    updateStreamInfo(data) {
        if (data.stream_duration !== undefined) {
            document.getElementById('stream-duration').textContent = this.formatDuration(data.stream_duration);
        }
    }
    
    updateAnalytics(data) {
        if (data.viewers) {
            document.getElementById('bot-viewers').textContent = data.viewers.active_viewers || 0;
        }
        
        if (data.comments) {
            document.getElementById('comments-posted').textContent = data.comments.comments_posted || 0;
        }
    }
    
    initChart() {
        const ctx = document.getElementById('viewersChart').getContext('2d');
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Bot Viewers',
                    data: [],
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Comments',
                    data: [],
                    borderColor: '#1cc88a',
                    backgroundColor: 'rgba(28, 200, 138, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
    
    updateChart(data) {
        if (!this.chart) return;
        
        const now = new Date().toLocaleTimeString();
        
        // Add new data point
        this.chart.data.labels.push(now);
        this.chart.data.datasets[0].data.push(data.viewers?.active_viewers || 0);
        this.chart.data.datasets[1].data.push(data.comments?.comments_posted || 0);
        
        // Keep only last 20 data points
        if (this.chart.data.labels.length > 20) {
            this.chart.data.labels.shift();
            this.chart.data.datasets[0].data.shift();
            this.chart.data.datasets[1].data.shift();
        }
        
        this.chart.update('none');
    }
    
    startDataUpdates() {
        // Update every 5 seconds
        this.updateInterval = setInterval(() => {
            this.updateDashboardData();
        }, 5000);
        
        // Initial update
        this.updateDashboardData();
    }
    
    async checkSystemStatus() {
        // This would check various system components
        // For now, we'll simulate the checks
        
        setTimeout(() => {
            document.getElementById('youtube-api-status').className = 'badge bg-success';
            document.getElementById('youtube-api-status').textContent = 'Connected';
        }, 1000);
        
        setTimeout(() => {
            document.getElementById('obs-status').className = 'badge bg-warning';
            document.getElementById('obs-status').textContent = 'Not Used';
        }, 1500);
    }
    
    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const toastMessage = document.getElementById('toast-message');
        
        // Set message
        toastMessage.textContent = message;
        
        // Set toast type
        toast.className = `toast show bg-${type === 'error' ? 'danger' : type}`;
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
    
    addActivity(message) {
        const activityLog = document.getElementById('activity-log');
        const now = new Date().toLocaleTimeString();
        
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div>${message}</div>
            <small class="activity-time">${now}</small>
        `;
        
        // Add to top
        activityLog.insertBefore(activityItem, activityLog.firstChild);
        
        // Keep only last 10 items
        while (activityLog.children.length > 10) {
            activityLog.removeChild(activityLog.lastChild);
        }
    }
    
    showLoading(buttonId) {
        const button = document.getElementById(buttonId);
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Loading...';
    }
    
    hideLoading(buttonId) {
        const button = document.getElementById(buttonId);
        button.disabled = false;
        
        // Restore original button text
        const buttonTexts = {
            'start-stream-btn': '<i class="fas fa-play"></i> Start Stream',
            'stop-stream-btn': '<i class="fas fa-stop"></i> Stop Stream',
            'restart-stream-btn': '<i class="fas fa-redo"></i> Restart Stream'
        };
        
        button.innerHTML = buttonTexts[buttonId] || 'Button';
    }
    
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new YouTubeDashboard();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (window.dashboard) {
        if (document.hidden) {
            // Page is hidden, reduce update frequency
            clearInterval(window.dashboard.updateInterval);
            window.dashboard.updateInterval = setInterval(() => {
                window.dashboard.updateDashboardData();
            }, 30000); // Update every 30 seconds when hidden
        } else {
            // Page is visible, restore normal update frequency
            clearInterval(window.dashboard.updateInterval);
            window.dashboard.updateInterval = setInterval(() => {
                window.dashboard.updateDashboardData();
            }, 5000); // Update every 5 seconds when visible
        }
    }
});
