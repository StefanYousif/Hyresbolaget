document.getElementById("button").addEventListener("click", function(){
  document.querySelector(".popup").style.display = "flex";
})

document.querySelector(".close").addEventListener("click", function(){
  document.querySelector(".popup").style.display = "none";
})


let map;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 8,
  });
}

window.initMap = initMap;