var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function initmap() {
	// set up the map
	map = new L.Map('map');

	// create the tile layer with correct attribution
	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 12, attribution: osmAttrib});
	var localLayerName = getParameterByName("layer");
	if (!localLayerName){
	    localLayerName = "201112";
	};
    var localTileLayerUrl = 'http://10.143.166.17:8000/tiles/' + localLayerName + '/{z}/{x}/{y}.png';
	var localTileLayer = new L.TileLayer(localTileLayerUrl, {minZoom: 8, maxZoom: 12, attribution: "safecast.org", tms: true});
    L.control.scale({metric: true, imperial: false}).addTo(map);

	// start the map in Fukushima
	map.setView(new L.LatLng(37.435793, 140.735437), 10);
	map.addLayer(osm);
	map.addLayer(localTileLayer);
}