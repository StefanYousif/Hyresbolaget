let map;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 55.604980, lng: 13.003822 },
    zoom: 10,
  });
}

window.initMap = initMap;