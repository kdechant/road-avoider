mapboxgl.accessToken = 'pk.eyJ1IjoiZ2VtaW5pY2EiLCJhIjoiNjM5ZjdkNDI0OWZkNGVmMzJlZGUwZjFlYTNkZjU4NGYifQ.BMp74b7SVszf66pxAP_tSg';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v9',
    center: [-122.667918, 45.522127],
    zoom: 10,
});
var el, marker;

var colors = [
    "#cc3333",
    "#33cc33",
    "#3333cc",
    "#999933",
    "#993399"
];
var color_index = 0;

map.on('click', function(e) {
    //get the spatial features where your mouse is currently located.
    //note we use the pixel location (e.point) and not lat/lon here.
    //also specify the feature we want to pay attention
    //to - 'academic_positions'
    el = document.createElement('div');
    el.className = 'marker';
    marker = new mapboxgl.Marker(el).setLngLat([0,0]).addTo(map);
    marker.setLngLat(e.lngLat);

    $.get('/api?lat=' + e.lngLat.lat + '&lng=' + e.lngLat.lng, function (data) {
        color_index = 0;
        var max_dist = 0;
        var max_dist_point = [e.lngLat.lng, e.lngLat.lat];
        for (const key in data) {
            var d = data[key];
            coords = [];
            for (const pt of d) {
                coords.push([pt.lng, pt.lat]);
                if (pt.distance > max_dist) {
                    max_dist = pt.distance;
                    max_dist_point = [pt.lng, pt.lat];
                }
            }
            let id = e.lngLat.lat + "_" + e.lngLat.lng + "_" + key;
            map.addLayer({
                id: id,
                type: 'line',
                paint: {
                    "line-color": colors[color_index++],
                    "line-width": 5
                },
                source: {
                    'type': 'geojson',
                    data: {
                        type: 'Feature',
                        properties: {},
                        geometry: {
                            type: 'LineString',
                            coordinates: coords
                        }
                    }
                }
            });
            map.on('mouseenter', id, function (e) {
                // Change the cursor style as a UI indicator.
                map.getCanvas().style.cursor = 'pointer';
                // Populate the popup and set its coordinates
                // based on the feature found.
                popup.setLngLat(e.lngLat)
                    .setHTML("<p><b>Distance traveled:</b> " + turf.length(e.features[0].geometry, {"unit": "miles"}).toFixed(3) + " miles</p>")
                    .addTo(map);
            });
            map.on('mouseleave', id, function () {
                map.getCanvas().style.cursor = '';
                popup.remove();
            });
        }
        // move the marker to the best point we found
        marker.setLngLat(max_dist_point);
    });

});
var popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
});

map.on('load', function () {

    $.get('/api/points', function (data) {
        let features = [];
        for (const pt of data.reverse()) {
            features.push({
                'id': 'point' + pt.id,
                'type': 'Feature',
                'properties': {
                    'id': 'marker' + pt.id,
                    'title': pt.lat + ", " + pt.lng,
                    'distance': pt.distance,
                },
                'geometry': {
                    'coordinates': [pt.lng, pt.lat],
                    'type': 'Point'
                }
            });
        }
        map.addLayer({
            id: 'points',
            type: 'circle',
            source: {
                'type': 'geojson',
                'data': {
                    'type': 'FeatureCollection',
                    'features': features
                }
            },
            'paint': {
                'circle-radius': {
                    property: 'distance',
                    type: 'exponential',
                    stops: [
                        [30000, 1],
                        [40000, 15]
                    ]
                },
                'circle-color': {
                    property: 'distance',
                    type: 'exponential',
                    stops: [
                      [30000, '#cccccc'],
                      [40000, '#0000ff']
                    ]
                }
            },
        });
        map.on('mouseenter', 'points', function (e) {
            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = 'pointer';
            // Populate the popup and set its coordinates
            // based on the feature found.
            popup.setLngLat(e.lngLat)
                .setHTML("<p>" + e.features[0].properties.title + "</p><p><b>Distance from nearest road:</b> " + (e.features[0].properties.distance / 5280).toFixed(2) + " miles</p>")
                .addTo(map);
        });
        map.on('mouseleave', 'points', function () {
            map.getCanvas().style.cursor = '';
            popup.remove();
        });
    });
})
