// Datumsauswahl initialisieren und Standardwerte setzen
document.addEventListener("DOMContentLoaded", () => {
    initializeDateSelection();
    loadHotels();
});

function initializeDateSelection() {
    const fromDateInput = document.getElementById("fromDate");
    const toDateInput = document.getElementById("toDate");

    // Finde den nächsten Freitag und Samstag
    const today = new Date();
    let nextFriday = new Date(today);
    let nextSaturday = new Date(today);

    nextFriday.setDate(today.getDate() + ((5 - today.getDay() + 7) % 7));
    nextSaturday.setDate(nextFriday.getDate() + 1);

    // Formatierung als yyyy-mm-dd
    const formatDate = (date) => date.toISOString().split("T")[0];

    fromDateInput.value = formatDate(nextFriday);
    toDateInput.value = formatDate(nextSaturday);
}

// Hotel-Daten abrufen und in der Tabelle anzeigen
async function loadHotels() {
    const tbody = document.getElementById('hotelList');
    tbody.innerHTML = ''; // Löscht vorhandene Einträge, um sicherzustellen, dass nichts doppelt angezeigt wird

    try {
        const url = `http://localhost/hotels?destination=Campus 1, 7000 Eisenstadt`;
        console.log(`Lade Hotels von URL: ${url}`);  // Debugging: URL-Check

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        });

        // Check, ob die Antwort des Endpunkts in Ordnung ist
        if (!response.ok) {
            console.error(`Fehler beim Laden der Hotel-Daten: ${response.status} ${response.statusText}`);
            return;
        }

        const responseData = await response.json();
        console.log("Antwortdaten:", responseData);  // Debugging: Anzeigen der gesamten Antwortdaten

        // Überprüfen, ob das erhaltene Objekt die erwartete Datenstruktur hat
        if (!responseData || !responseData.data || !Array.isArray(responseData.data)) {
            console.error("Ungültige Hotel-Daten erhalten:", responseData);
            return;
        }

        const hotels = responseData.data;

        if (hotels.length === 0) {
            console.warn("Keine Hotels in den erhaltenen Daten gefunden.");
            return;
        }

        // Durch die Hotels iterieren und in die Tabelle einfügen
        for (let i = 0; i < hotels.length; i++) {
            const hotel = hotels[i];

            // Überprüfen, ob die notwendigen Informationen vorhanden sind
            if (!hotel.name || !hotel.address || hotel.freeRooms === undefined) {
                console.error(`Fehlende Daten für Hotel ${i}`, hotel);
                continue; // Fehlerhafte Daten überspringen
            }

            // Wenn lat/lng fehlen, holen wir diese Daten mit der Nominatim API ab
            if (hotel.lat === undefined || hotel.lat === null || hotel.lng === undefined || hotel.lng === null) {
                console.log(`Geodaten fehlen für Hotel: ${hotel.name}. Rufe Koordinaten ab...`);
                const coords = await getCoordinatesFromAddress(hotel.address);
                if (coords) {
                    hotel.lat = coords.lat;
                    hotel.lng = coords.lng;
                    console.log(`Koordinaten erhalten für Hotel: ${hotel.name}, Lat: ${hotel.lat}, Lng: ${hotel.lng}`);
                } else {
                    console.warn(`Koordinaten konnten für Hotel: ${hotel.name} nicht abgerufen werden.`);
                    continue; // Überspringe Hotels ohne Koordinaten
                }
            }

            // Hotel in die Liste einfügen
            const row = document.createElement('tr');
            row.className = 'hotel-item';
            row.dataset.index = i;
            row.innerHTML = `
                <td>${hotel.name}</td>
                <td>${hotel.address}</td>
                <td>${hotel.freeRooms}</td>
                <td><button class="book-button" onclick="bookHotel('${hotel.hotel_id}')">Buchen</button></td>
            `;
            row.addEventListener('click', () => {
                console.log(`Hotel ${hotel.name} ausgewählt.`);
                highlightHotelOnMap(hotel.lat, hotel.lng, hotel.name);
            });
            tbody.appendChild(row);
        }

        console.log("Hotels erfolgreich geladen und in die Tabelle eingefügt.");  // Erfolgsnachricht

    } catch (error) {
        // Fehlerbehandlung mit vollständigem Fehlerausdruck
        console.error("Fehler beim Abrufen der Hotel-Daten:", error.message);
    }
}

// Hotel buchen
async function bookHotel(hotel_id) {
    const fromDateInput = document.getElementById("fromDate").value;
    const toDateInput = document.getElementById("toDate").value;

    const url = "http://localhost/booking";
    const data = {
        hotel_id: hotel_id,
        start_date: fromDateInput,
        end_date: toDateInput
    };

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert("Buchung erfolgreich!");
        } else {
            console.error(`Fehler bei der Buchung: ${response.status} ${response.statusText}`);
            alert("Fehler bei der Buchung. Bitte versuchen Sie es erneut.");
        }
    } catch (error) {
        console.error("Buchung fehlgeschlagen:", error.message);
        alert("Buchung fehlgeschlagen. Bitte überprüfen Sie Ihre Verbindung.");
    }
}

// Nachricht an den iframe senden, um ein Hotel auf der Karte hervorzuheben
function highlightHotelOnMap(lat, lng, hotelName) {
    const iframe = document.getElementById("mapIframe");
    if (iframe) {
        iframe.contentWindow.postMessage({
            type: "highlightHotel",
            lat: lat,
            lng: lng,
            hotelName: hotelName
        }, "*");
    } else {
        console.error("Iframe mit der ID 'mapIframe' nicht gefunden.");
    }
}

// Koordinaten von der Nominatim API (OpenStreetMap) abrufen
async function getCoordinatesFromAddress(address) {
    try {
        const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address)}&format=json&limit=1`;
        console.log(`Rufe Koordinaten von URL: ${url}`);  // Debugging: URL-Check

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            console.error(`Fehler beim Abrufen der Koordinaten: ${response.status} ${response.statusText}`);
            return null;
        }

        const data = await response.json();

        if (data.length > 0) {
            return {
                lat: parseFloat(data[0].lat),
                lng: parseFloat(data[0].lon)
            };
        } else {
            console.warn(`Keine Ergebnisse von Nominatim für die Adresse: ${address}`);
            return null;
        }
    } catch (error) {
        console.error("Fehler bei der Geocodierung:", error.message);
        return null;
    }
}
