let map
let markers = []
let selectedProvider = null
let radiusCircle = null

// Zieladresse der Hochschule Burgenland
const destinationLocation = {
  name: "Hochschule Burgenland",
  address: "Campus 1, 7000 Eisenstadt",
  lat: 47.82948485,
  lng: 16.534787097735926,
  isDestination: true,
}

document.addEventListener("DOMContentLoaded", () => {
  initializeDateSelection()
  initializeMap()
})

function addMarker(lat, lon, name) {
  const marker = L.marker([lat, lon]).addTo(map)
  markers.push(marker)
}

function bookRoom() {
  if (selectedProvider) {
    alert(`Buchung erfolgreich für: ${selectedProvider.name}`)
  }
}

function highlightHotelOnMap(lat, lng, hotelName) {
  const hotelMarker = L.marker([lat, lng]).addTo(map).bindPopup(`<b>${hotelName}</b>`).openPopup()

  // Zoomen auf den Marker und die Hochschule Burgenland
  const bounds = L.latLngBounds([
    [destinationLocation.lat, destinationLocation.lng],
    [lat, lng],
  ])
  map.fitBounds(bounds, { padding: [100, 100] })
}

function initializeDateSelection() {
  const fromDateInput = document.getElementById("start_date")
  const toDateInput = document.getElementById("end_date")

  // Finde den nächsten Freitag und Samstag
  const today = new Date()
  const nextFriday = new Date(today)
  const nextSaturday = new Date(today)

  nextFriday.setDate(today.getDate() + ((5 - today.getDay() + 7) % 7))
  nextSaturday.setDate(nextFriday.getDate() + 1)

  // Formatierung als yyyy-mm-dd
  const formatDate = date => date.toISOString().split("T")[0]

  fromDateInput.value = formatDate(nextFriday)
  toDateInput.value = formatDate(nextSaturday)
}

function initializeMap() {
  map = L.map("map").setView([destinationLocation.lat, destinationLocation.lng], 13)
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map)

  L.marker([destinationLocation.lat, destinationLocation.lng])
    .addTo(map)
    .bindPopup(`<b>${destinationLocation.name}</b>`)
    .openPopup()
}

async function searchProviders() {
  const location = document.getElementById("location").value || destinationLocation.name
  const radius = Number.parseFloat(document.getElementById("radius").value)
  showRadiusCircle([destinationLocation.lat, destinationLocation.lng], radius)

  const startDate = document.getElementById("start_date").value
  const endDate = document.getElementById("end_date").value

  const response = await fetch(
    `/search-providers?location=${location}&radius=${radius}&start_date=${startDate}&end_date=${endDate}`
  )
  const providers = await response.json()

  const providerList = document.getElementById("provider-list")
  providerList.innerHTML = ""
  markers.forEach(marker => map.removeLayer(marker))
  markers = []

  if (!providers || providers.length === 0) {
    providerList.innerHTML = "<li>Keine Anbieter gefunden.</li>"
    document.getElementById("results-section").style.display = "block"
    return
  }

  providers.forEach(provider => {
    const li = document.createElement("li")
    li.className = "result-item"
    li.innerHTML = `
            <div class="result-info">
                <strong>${provider.name}</strong> (${provider.type}) - ${provider.distance} km entfernt
                <br>Adresse: ${provider.address}
                <br>Parkplatz: ${provider.parking.available ? "Verfügbar" : "Nicht verfügbar"}
            </div>
        `
    li.addEventListener("click", () => {
      selectProvider(provider, li)
      highlightHotelOnMap(provider.location[0], provider.location[1], provider.name)
    })
    providerList.appendChild(li)

    addMarker(provider.location[0], provider.location[1], provider.name)
  })

  document.getElementById("results-section").style.display = "block"
}

function selectProvider(provider, listItem) {
  selectedProvider = provider
  document.querySelectorAll(".result-item").forEach(item => item.classList.remove("selected"))
  listItem.classList.add("selected")
  document.getElementById("book-btn").style.display = "block"

  // Entferne den Radiuskreis beim Auswählen eines Anbieters
  if (radiusCircle) {
    map.removeLayer(radiusCircle)
  }
  map.setView(provider.location, 16)
}

function showRadiusCircle(center, radius) {
  if (radiusCircle) {
    map.removeLayer(radiusCircle)
  }

  const radiusInMeters = radius * 1000
  radiusCircle = L.circle(center, {
    color: "red",
    fillColor: "#f03",
    fillOpacity: 0.1,
    radius: radiusInMeters,
  }).addTo(map)
  map.setView(center, 11)
}

function validateSearch() {
  const startDate = new Date(document.getElementById("start_date").value)
  const endDate = new Date(document.getElementById("end_date").value)

  if (startDate && endDate && endDate > startDate) {
    const days = (endDate - startDate) / (1000 * 3600 * 24)
    document.getElementById("days").value = days
    document.getElementById("search-btn").disabled = false
  } else {
    document.getElementById("days").value = ""
    document.getElementById("search-btn").disabled = true
  }
}
