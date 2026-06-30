let map;
let userMarker;
let donorMarkersLayer = L.layerGroup();
let currentLat, currentLng;

// Initialize the map system using browser geolocation tracking
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(position => {
        currentLat = position.coords.latitude;
        currentLng = position.coords.longitude;

        // Initialize Leaflet Map centered around user coordinates
        map = L.map('map').setView([currentLat, currentLng], 13);

        // OpenStreetMap Tile Layer (Free Alternative to Google Maps)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Add a unique pin marker representing the patient/seeker
        userMarker = L.marker([currentLat, currentLng]).addTo(map)
            .bindPopup('<b>Your Current Location</b>').openPopup();

        donorMarkersLayer.addTo(map);

        // Run initial nearby scan execution
        findNearbyDonors();
    }, () => {
        alert("Geolocation failed. Please allow tracking context permissions.");
    });
}

function findNearbyDonors() {
    const bloodGroup = document.getElementById('blood_group').value;
    const radius = document.getElementById('radius').value;
    const listPanel = document.getElementById('donor-list');

    if (!currentLat || !currentLng) return;

    // Async Fetch to Flask REST Endpoint
    fetch(`/api/nearby-donors?lat=${currentLat}&lng=${currentLng}&blood_group=${bloodGroup}&radius=${radius}`)
        .json()
        .then(data => {
            // Clear existing dashboard overlay data arrays
            donorMarkersLayer.clearLayers();
            listPanel.innerHTML = "";

            if (data.length === 0) {
                listPanel.innerHTML = "<p>No nearby active matches found inside your specified range context.</p>";
                return;
            }

            data.forEach(donor => {
                // Add Marker Pin for each Donor on Map
                const marker = L.marker([donor.lat, donor.lng]);
                marker.bindPopup(`
                    <b>Donor:</b> ${donor.name}<br>
                    <b>Group:</b> <span style="color:red;">${donor.blood_group}</span><br>
                    <b>Distance:</b> ${donor.distance} km<br>
                    <a href="tel:${donor.phone}">📞 Call Now</a>
                `);
                donorMarkersLayer.addLayer(marker);

                // Add text card to side execution list interface panel (Like Uber list)
                const card = document.createElement('div');
                card.className = 'donor-card';
                card.innerHTML = `
                    <h4>${donor.name} (${donor.blood_group})</h4>
                    <p>📍 Distance: <b>${donor.distance} KM away</b></p>
                    <p>📱 Contact: ${donor.phone}</p>
                    <hr>
                `;
                listPanel.appendChild(card);
            });
        });
}