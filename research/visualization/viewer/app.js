const API_BASE = ""; // Relative path since served from same origin
let eventsChart = null;
let sensorsChart = null;
let healthChart = null;

async function fetchSensors() {
    try {
        const response = await fetch(`${API_BASE}/sensors`);
        const data = await response.json();
        renderSensors(data);
    } catch (error) {
        console.error("Error fetching sensors:", error);
    }
}

function renderSensors(data) {
    const container = document.getElementById('sensors-container');
    container.innerHTML = '';
    
    if (!data || Object.keys(data).length === 0) {
        container.innerHTML = '<p>No sensor data available.</p>';
        return;
    }

    for (const [key, value] of Object.entries(data)) {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-header">
                <h3>${key.charAt(0).toUpperCase() + key.slice(1)}</h3>
            </div>
            <div class="card-body">
                <p class="sensor-value">${value}</p>
            </div>
        `;
        container.appendChild(card);
    }
}

async function fetchSensorHistory() {
    try {
        const response = await fetch(`${API_BASE}/sensors/history?limit=20`);
        const data = await response.json();
        updateSensorChart(data);
    } catch (error) {
        console.error("Error fetching sensor history:", error);
    }
}

async function fetchHealthHistory() {
    try {
        const response = await fetch(`${API_BASE}/health/history?limit=20`);
        const data = await response.json();
        updateHealthChart(data);
    } catch (error) {
        console.error("Error fetching health history:", error);
    }
}

async function fetchAgents() {
    try {
        const response = await fetch(`${API_BASE}/agents`);
        const agents = await response.json();
        renderAgents(agents);
    } catch (error) {
        console.error("Error fetching agents:", error);
    }
}

function renderAgents(agents) {
    const container = document.getElementById('agents-container');
    container.innerHTML = '';
    
    agents.forEach(agent => {
        const card = document.createElement('div');
        card.className = 'card agent-card';
        
        // Parse specs if string or object
        let specsHtml = '';
        if (agent.specs) {
            specsHtml = '<ul class="specs-list">';
            for (const [key, value] of Object.entries(agent.specs)) {
                specsHtml += `<li><strong>${key}:</strong> ${value}</li>`;
            }
            specsHtml += '</ul>';
        }

        card.innerHTML = `
            <div class="card-header">
                <h3>${agent.name || agent.agent_id}</h3>
                <span class="badge ${agent.agent_type}">${agent.agent_type}</span>
            </div>
            <div class="card-body">
                <p><strong>ID:</strong> ${agent.agent_id}</p>
                ${specsHtml}
                <p class="timestamp" style="font-size: 0.8rem; color: #666; margin-top: 1rem;">
                    Created: ${new Date(agent.created_at).toLocaleDateString()}
                </p>
            </div>
        `;
        container.appendChild(card);
    });
}

async function fetchZones() {
    try {
        const response = await fetch(`${API_BASE}/zones`);
        const zones = await response.json();
        const select = document.getElementById('zone-filter');
        zones.forEach(zone => {
            const option = document.createElement('option');
            option.value = zone.zone_id;
            option.textContent = zone.name || zone.zone_id;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching zones:", error);
    }
}

async function fetchEvents() {
    try {
        const zoneFilter = document.getElementById('zone-filter').value;
        let url = `${API_BASE}/events/history?limit=20`;
        if (zoneFilter) url += `&zone_id=${encodeURIComponent(zoneFilter)}`;
        
        const response = await fetch(url);
        const events = await response.json();
        renderEvents(events);
        updateChart(events);
    } catch (error) {
        console.error("Error fetching events:", error);
    }
}

function renderEvents(events) {
    const tbody = document.querySelector('#events-table tbody');
    tbody.innerHTML = '';

    events.forEach(event => {
        const row = document.createElement('tr');
        
        let details = '-';
        if (event.object_class) {
            details = `Detected: <strong>${event.object_class}</strong>`;
            if (event.confidence) details += ` (${(event.confidence * 100).toFixed(0)}%)`;
        }

        row.innerHTML = `
            <td>${new Date(event.timestamp).toLocaleTimeString()}</td>
            <td><span class="event-type">${event.event_type}</span></td>
            <td>${event.source_id}</td>
            <td>${event.zone_id || '-'}</td>
            <td>${details}</td>
        `;
        tbody.appendChild(row);
    });
}

function initChart() {
    const ctx = document.getElementById('events-chart').getContext('2d');
    eventsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Events per Zone',
                data: [],
                backgroundColor: 'rgba(0, 122, 204, 0.5)',
                borderColor: 'rgba(0, 122, 204, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#333' },
                    ticks: { color: '#a0a0a0' }
                },
                x: {
                    grid: { color: '#333' },
                    ticks: { color: '#a0a0a0' }
                }
            },
            plugins: {
                legend: { labels: { color: '#e0e0e0' } }
            }
        }
    });
}

function updateChart(events) {
    if (!eventsChart) return;

    const zoneCounts = {};
    events.forEach(event => {
        const zone = event.zone_id || 'Unknown';
        zoneCounts[zone] = (zoneCounts[zone] || 0) + 1;
    });

    eventsChart.data.labels = Object.keys(zoneCounts);
    eventsChart.data.datasets[0].data = Object.values(zoneCounts);
    eventsChart.update();
}

function initSensorChart() {
    const ctx = document.getElementById('sensors-chart').getContext('2d');
    sensorsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: [],
                    borderColor: '#ff9800',
                    backgroundColor: 'rgba(255, 152, 0, 0.2)',
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Vibration',
                    data: [],
                    borderColor: '#007acc',
                    backgroundColor: 'rgba(0, 122, 204, 0.2)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    grid: { color: '#333' },
                    ticks: { color: '#a0a0a0' }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: '#333' },
                    ticks: { color: '#a0a0a0' },
                    title: { display: true, text: 'Temperature', color: '#a0a0a0' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#a0a0a0' },
                    title: { display: true, text: 'Vibration', color: '#a0a0a0' }
                }
            },
            plugins: {
                legend: { labels: { color: '#e0e0e0' } }
            }
        }
    });
}

function updateSensorChart(data) {
    if (!sensorsChart) return;
    
    const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
    const temps = data.map(d => d.temperature);
    const vibs = data.map(d => d.vibration);
    
    sensorsChart.data.labels = labels;
    sensorsChart.data.datasets[0].data = temps;
    sensorsChart.data.datasets[1].data = vibs;
    sensorsChart.update();
}

function initHealthChart() {
    const ctx = document.getElementById('health-chart').getContext('2d');
    healthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'System Health Score',
                data: [],
                borderColor: '#4caf50',
                backgroundColor: 'rgba(76, 175, 80, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { color: '#333' },
                    ticks: { color: '#a0a0a0' }
                },
                y: {
                    beginAtZero: true,
                    max: 1.0,
                    grid: { color: '#333' },
                    ticks: { color: '#a0a0a0' }
                }
            },
            plugins: {
                legend: { labels: { color: '#e0e0e0' } }
            }
        }
    });
}

function updateHealthChart(data) {
    if (!healthChart) return;
    
    const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
    const scores = data.map(d => d.health_score);
    
    healthChart.data.labels = labels;
    healthChart.data.datasets[0].data = scores;
    healthChart.update();
}

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    initSensorChart();
    initHealthChart();
    fetchZones();
    fetchSensors();
    fetchSensorHistory();
    fetchHealthHistory();
    fetchAgents();
    fetchEvents();
    document.getElementById('refresh-btn').addEventListener('click', fetchEvents);
    document.getElementById('zone-filter').addEventListener('change', fetchEvents);
    setInterval(fetchEvents, 5000); // Auto-refresh events
    setInterval(fetchSensors, 5000); // Auto-refresh sensors
    setInterval(fetchSensorHistory, 5000); // Auto-refresh sensor history
    setInterval(fetchHealthHistory, 5000); // Auto-refresh health history
});