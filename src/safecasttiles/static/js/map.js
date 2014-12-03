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

function httpGet(theUrl)
{
    if (window.XMLHttpRequest)
    {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else
    {// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            return xmlhttp.responseText;
        }
    }
    xmlhttp.open("GET", theUrl, false );
    xmlhttp.send();
}

function initmap() {
    var mapOptions = {zoomControl: false};
	var localLayerName = getParameterByName("layer");
	if (!localLayerName){
	    localLayerName = "201112";
        mapOptions = {zoomControl: true};  // show zoom control if query string not given (likely to be a user not autobot)
	};
    var localTileLayerUrl = 'http://10.143.166.17:8000/tiles/' + localLayerName + '/{z}/{x}/{y}.png';
	var localTileLayer = new L.TileLayer(localTileLayerUrl, {minZoom: 8, maxZoom: 12, attribution: "safecast.org", tms: true});

	// set up the map with mapOptions (toggles zoom control)
	map = new L.Map('map', mapOptions);

	// create the tile layer with correct attribution
	//var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	//var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	//var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 12, attribution: osmAttrib});

    L.control.scale({metric: true, imperial: false}).addTo(map);

    // add legend
    var legend = L.control({position: 'bottomright'});
    legend.onAdd = function (map) {
        var legendDivInnerHTML = httpGet("http://127.0.0.1:8000/legend/");
        var div = L.DomUtil.create("div", "info legend");
        div.innerHTML += legendDivInnerHTML;
        return div;
    };
    legend.addTo(map);


    // add layername label
    var info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };
    // method that we will use to update the control based on feature properties passed (update function ote used atm)
    info.update = function (props) {
        // parse localLayerName to int year and month to create display timeline overlay
        var selectedLayerYear = parseInt(localLayerName.substring(0, 4));
        // workaround for phantomjs parseInt issue
        var selectedLayerMonth = parseInt(localLayerName.substring(4));
        if (localLayerName.substring(4, 5) == "0"){
            selectedLayerMonth = parseInt(localLayerName.substring(5));
        };
        this._div.innerHTML = getTimeline(selectedLayerYear, selectedLayerMonth);
    };
    info.addTo(map);

	// start the map in Fukushima
	map.setView(new L.LatLng(37.435793, 140.735437), 9);
	//map.addLayer(osm);
	map.addLayer(localTileLayer);
}