// Zieladresse der Hochschule Burgenland
const destinationLocation = {
    name: "Hochschule Burgenland",
    address: "Campus 1, 7000 Eisenstadt",
    lat: 47.82948485,
    lng: 16.534787097735926,
    isDestination: true
};

// Karte erstellen und auf die Hochschule Burgenland zentrieren
const map = L.map('map').setView([destinationLocation.lat, destinationLocation.lng], 13);

// OpenStreetMap Layer hinzufügen
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Marker für Hochschule setzen
L.marker([destinationLocation.lat, destinationLocation.lng])
    .addTo(map)
    .bindPopup(`<b>${destinationLocation.name}</b><br>${destinationLocation.address}`)
    .openPopup();

// Nachricht vom Hauptfenster empfangen und verarbeiten
window.addEventListener("message", (event) => {
    if (event.data.type === "highlightHotel") {
        const { lat, lng, hotelName } = event.data;

        // Karte auf das ausgewählte Hotel zentrieren und Marker hinzufügen
        const hotelMarker = L.marker([lat, lng])
            .addTo(map)
            .bindPopup(`<b>${hotelName}</b>`)
            .openPopup();

        // Zoomen auf den Marker und die Hochschule Burgenland
        const bounds = L.latLngBounds([
            [destinationLocation.lat, destinationLocation.lng],
            [lat, lng]
        ]);
        map.fitBounds(bounds, { padding: [100, 100] });
    }
});
