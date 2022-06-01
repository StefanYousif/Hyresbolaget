
var geocoder;
var map;
var address = [
  "Måsvägen 12b, lund",
  "rapsvägen 115, arlöv",
  "dalbyvägen 37, arlöv"
];
function initMap() {
  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 8,
    center: {lat: 55.604980, lng: 13.003822 }
  });
  geocoder = new google.maps.Geocoder();
  
  for (let i = 0; i < address.length; i++) {
    codeAddress(geocoder, map, address[i]);
  }
  codeAddress(geocoder, map);
}

function codeAddress(geocoder, map, address) {
  geocoder.geocode({'address': address}, function(results, status) {
    if (status === 'OK') {
      map.setCenter(results[0].geometry.location);
      var marker = new google.maps.Marker({
        map: map,
        position: results[0].geometry.location
      });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}
/*
  var adress = {{ address_list }};
*/


window.initMap = initMap;