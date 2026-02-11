const map = L.map('map').setView([56.49, -4.2], 7);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18,
}).addTo(map);

const CONDITION_COLORS = {
    good: '#28a745',
    moderate: '#ffc107',
    poor: '#dc3545',
};

let markersLayer = L.layerGroup().addTo(map);

function loadAssets(params) {
    const query = new URLSearchParams(params).toString();
    fetch('/api/assets?' + query)
        .then(response => response.json())
        .then(assets => {
            markersLayer.clearLayers();
            assets.forEach(asset => {
                const color = CONDITION_COLORS[asset.condition] || '#6c757d';
                const marker = L.circleMarker([asset.latitude, asset.longitude], {
                    radius: 8,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.85,
                });
                marker.bindPopup(
                    '<strong>' + escapeHtml(asset.name) + '</strong><br>' +
                    'ID: ' + escapeHtml(asset.asset_id) + '<br>' +
                    'Type: ' + escapeHtml(asset.asset_type) + '<br>' +
                    'Condition: ' + escapeHtml(asset.condition) + '<br>' +
                    (asset.last_inspected ? 'Inspected: ' + escapeHtml(asset.last_inspected) : '')
                );
                markersLayer.addLayer(marker);
            });
            document.getElementById('asset-count').textContent = assets.length + ' asset(s) displayed';
        });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initial load
loadAssets({});

// Filter form handling
const filterForm = document.getElementById('filter-form');
if (filterForm) {
    filterForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(filterForm);
        const params = {};
        for (const [key, value] of formData.entries()) {
            if (value) params[key] = value;
        }
        loadAssets(params);
    });
}
