

function initMap() {
  const myLatLng = { lat: 55.604980, lng: 13.003822  };
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 10,
    center: myLatLng,
  });
  const image =
    "https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png";


  new google.maps.Marker({
    position: myLatLng,
    map,
    title: "Hello Worsadsdsassdasld!",
    icon:image,
  });
  
}

window.initMap = initMap;