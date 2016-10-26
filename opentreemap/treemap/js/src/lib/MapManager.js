"use strict";

var $ = require('jquery'),
    _ = require('lodash'),
    R = require('ramda'),
    L = require('leaflet'),
    Bacon = require('baconjs'),
    format = require('util').format,
    U = require('treemap/lib/utility.js'),
    BU = require('treemap/lib/baconUtils.js'),
    urlState = require('treemap/lib/urlState.js'),

    layersLib = require('treemap/lib/layers.js'),
    CanopyFilterControl = require('treemap/lib/controls.js').CanopyFilterControl,

    config = require('treemap/lib/config.js'),
    reverse = require('reverse'),

    MIN_ZOOM_OPTION = layersLib.MIN_ZOOM_OPTION,
    MAX_ZOOM_OPTION = layersLib.MAX_ZOOM_OPTION,
    BASE_LAYER_OPTION = layersLib.BASE_LAYER_OPTION;

// Leaflet extensions
require('utfgrid');
require('leafletbing');
require('leafletgoogle');
require('esri-leaflet');

var MapManager = function() {};  // constructor

MapManager.prototype = {
    ZOOM_DEFAULT: 11,
    ZOOM_PLOT: 18,

    createTreeMap: function (options) {
        var hasPolygons = getDomMapBool('has-polygons', options.domId),
            hasBoundaries = getDomMapBool('has-boundaries', options.domId),
            plotLayer = layersLib.createPlotTileLayer(),
            allPlotsLayer = layersLib.createPlotTileLayer(),
            utfLayer = layersLib.createPlotUTFLayer();
        this._plotLayer = plotLayer;
        this._allPlotsLayer = allPlotsLayer;
        this._utfLayer = utfLayer;
        allPlotsLayer.setOpacity(0.3);

        options.bounds = getDomMapAttribute('bounds', options.domId);
        var map = this.createMap(options);

        if (options.plotLayerViewOnly) {
            this.layersControl.addOverlay(plotLayer, 'OpenTreeMap Trees');
        } else {
            map.addLayer(plotLayer);
            map.addLayer(utfLayer);
            var baseUtfEventStream = BU.leafletEventStream(utfLayer, 'click');

            if (hasPolygons) {
                var polygonLayer = layersLib.createPolygonTileLayer(),
                    allPolygonsLayer = layersLib.createPolygonTileLayer();
                this._hasPolygons = hasPolygons;
                this._polygonLayer = polygonLayer;
                this._allPolygonsLayer = allPolygonsLayer;
                allPolygonsLayer.setOpacity(0.3);
                map.addLayer(polygonLayer);

                fixZoomLayerSwitch(map, polygonLayer);
                fixZoomLayerSwitch(map, allPolygonsLayer);

                // When a map has polygons, we check to see if a utf event was
                // for a dot, and if not, and if the map is zoomed in enough to
                // see polygons, we make an AJAX call to see if there
                // is a polygon in that location.
                var shouldCheckForPolygon = function(e) {
                        return map.getZoom() >= MIN_ZOOM_OPTION.minZoom && e.data === null;
                    },
                    plotUtfEventStream = baseUtfEventStream.filter(R.not(shouldCheckForPolygon)),
                    emptyUtfEventStream = baseUtfEventStream.filter(shouldCheckForPolygon),

                    polygonDataStream = emptyUtfEventStream.map(function(e) {
                        var lat = e.latlng.lat,
                            lng = e.latlng.lng,
                            // The distance parameter changes as a function of zoom
                            // halving with every zoom level.  I arrived at 20
                            // meters at zoom level 15 through trial and error
                            dist = 20 / Math.pow(2, map.getZoom() - MIN_ZOOM_OPTION.minZoom),
                            url = reverse.polygon_for_point({instance_url_name: config.instance.url_name});

                        return url + format('?lng=%d&lat=%d&distance=%d', lng, lat, dist);
                    }).flatMap(BU.getJsonFromUrl);

                map.utfEvents = Bacon.mergeAll(
                    plotUtfEventStream,
                    emptyUtfEventStream.zip(polygonDataStream, function(utf, polygon) {
                        return _.merge({}, utf, polygon);
                    })
                );
            } else {
                map.utfEvents = baseUtfEventStream;
            }
        }

        if (hasBoundaries) {
            var boundariesLayer = layersLib.createBoundariesTileLayer();
            map.addLayer(boundariesLayer);
            this.layersControl.addOverlay(boundariesLayer, 'Boundaries');

            fixZoomLayerSwitch(map, boundariesLayer);
        }

        if (config.instance.canopyEnabled) {
            var canopyLayer = layersLib.createCanopyBoundariesTileLayer();

            var filterControl = new CanopyFilterControl();
            filterControl.tilerArgsProp
                .debounce(1000)
                .map(function(tilerArgs) {
                    tilerArgs.category = config.instance.canopyBoundaryCategory;
                    return tilerArgs;
                })
                .onValue(function(tilerArgs) {
                    var newUrl = layersLib.getCanopyBoundariesTileLayerUrl(tilerArgs);
                    canopyLayer.setUrl(newUrl);
                });

            map.on('overlayadd', function(e) {
                if (e.layer === canopyLayer) {
                    map.addControl(filterControl);
                }
            });

            map.on('overlayremove', function(e) {
                if (e.layer === canopyLayer) {
                    map.removeControl(filterControl);
                }
            });

            this.layersControl.addOverlay(canopyLayer, 'Regional Canopy Percentages');

            fixZoomLayerSwitch(map, canopyLayer);
        }

        _.each(config.instance.customLayers, _.partial(addCustomLayer, this));

        var zoomLatLngOutputStream = trackZoomLatLng(options, map, this);

        return zoomLatLngOutputStream;
    },

    createMap: function (options) {
        var center = options.centerWM || {x: 0, y: 0},
            zoom = options.zoom || 2,
            bounds = options.bounds,
            map = L.map(options.domId),
            type = options.type,
            basemapMapping = getBasemapLayers(type);

        if (_.isUndefined(bounds)) {
            map.setView(U.webMercatorToLeafletLatLng(center.x, center.y), zoom);
        } else {
            map.fitBounds([
                    U.webMercatorToLeafletLatLng(bounds.xmin, bounds.ymin),
                    U.webMercatorToLeafletLatLng(bounds.xmax, bounds.ymax)
                ],
                MAX_ZOOM_OPTION
            );
        }

        if (_.isArray(basemapMapping)) {
            _.each(_.values(basemapMapping),
                function (layer) {
                    map.addLayer(layer);
                });
        } else {
            var visible = _.keys(basemapMapping)[0];
            map.addLayer(basemapMapping[visible]);
            this.layersControl = L.control.layers(basemapMapping, null, {
                autoZIndex: false
            }).addTo(map);
        }

        if (options.disableScrollWithMouseWheel) {
            map.scrollWheelZoom = false;
        }

        this.map = map;
        return map;
    },

    updateRevHashes: function (response) {
        this._utfLayer.setHashes(response);
        this._plotLayer.setHashes(response);
        this._allPlotsLayer.setHashes(response);

        if (this._hasPolygons) {
            this._polygonLayer.setHashes(response);
            this._allPolygonsLayer.setHashes(response);
        }
    },

    setFilter: function (filter) {
        this._plotLayer.setFilter(filter);

        if (this._hasPolygons) {
            this._polygonLayer.setFilter(filter);
        }

        if (!this._allPlotsLayer.map) {
            this.map.addLayer(this._allPlotsLayer);
            if (this._hasPolygons) {
                this.map.addLayer(this._allPolygonsLayer);
            }
        }
        if (_.isEmpty(filter)) {
            this.map.removeLayer(this._allPlotsLayer);
            if (this._hasPolygons) {
                this.map.removeLayer(this._allPolygonsLayer);
            }
        }
    },

    setCenterAndZoomLL: function (zoom, location, reset) {
        // Never zoom out, or try to zoom farther than allowed.
        var zoomToApply = Math.max(
            this.map.getZoom(),
            Math.min(zoom, this.map.getMaxZoom()));

        this.map.setView(location, zoomToApply, {reset: !!reset});
    },

    setCenterAndZoomWM: function (zoom, location, reset) {
        this.setCenterAndZoomLL(
            zoom,
            U.webMercatorToLeafletLatLng(location.x, location.y),
            reset);
    },

    setCenterWM: function(location, reset) {
        this.setCenterAndZoomWM(this.ZOOM_PLOT, location, reset);
    },

    setCenterLL: function(location, reset) {
        this.setCenterAndZoomLL(this.ZOOM_PLOT, location, reset);
    }
};

function getBasemapLayers(type) {
    var options = _.extend({}, MAX_ZOOM_OPTION, BASE_LAYER_OPTION);
    type = type || config.instance.basemap.type;

    function makeBingLayer(layer) {
        return new L.BingLayer(
            config.bing_api_key,
            _.extend(options, {type: layer}));
    }

    function makeEsriLayer(key) {
        var layer = L.esri.basemapLayer(key, options);
        layer.on('load', function () {
            // Otherwise basemap is behind plot layer (esri-leaflet 1.0.2, leaflet 0.7.3)
            layer.setZIndex(BASE_LAYER_OPTION.zIndex);
        });
        return layer;
    }

    if (type === 'bing') {
        return {
            'Road': makeBingLayer('Road'),
            'Aerial': makeBingLayer('Aerial'),
            'Hybrid': makeBingLayer('AerialWithLabels')
        };
    } else if (type === 'esri') {
        return {
            'Streets': makeEsriLayer("Topographic"),
            'Hybrid': L.layerGroup([
                makeEsriLayer("Imagery"),
                makeEsriLayer("ImageryTransportation")
            ]),
            'Satellite': makeEsriLayer("Imagery")
        };
    } else if (type === 'tms') {
        return [L.tileLayer(config.instance.basemap.data, options)];
    } else {
        return {
            'Streets': new L.Google('ROADMAP', options),
            'Hybrid': new L.Google('HYBRID', options),
            'Satellite': new L.Google('SATELLITE', options)
        };
    }
}

function trackZoomLatLng(options, map, mapManager) {
    var shouldOutput = true,
        zoomLatLngOutputStream =
            BU.leafletEventStream(map, 'moveend')
                .filter(function () {return shouldOutput;})
                .map(function (e) {
                    var zoomLatLng = _.extend({zoom: map.getZoom()}, map.getCenter());
                    return zoomLatLng;
                });

    if (options.trackZoomLatLng) {
        var zoomLatLngInputStream;
        if (options.zoomLatLngInputStream) {
            // Calling page will save/load zoomLatLng
            zoomLatLngInputStream = options.zoomLatLngInputStream;
        } else {
            // Save/load zoomLatLng in urlState
            zoomLatLngInputStream = urlState.stateChangeStream
                .filter('.zoomLatLng')
                .map('.zoomLatLng');
            zoomLatLngOutputStream.onValue(urlState.setZoomLatLng);
        }

        zoomLatLngInputStream.onValue(function (zoomLatLng) {
            if (!_.isEmpty(zoomLatLng)) {
                shouldOutput = false;
                mapManager.setCenterAndZoomLL(
                    zoomLatLng.zoom,
                    new L.LatLng(zoomLatLng.lat, zoomLatLng.lng));
                shouldOutput = true;
            }
        });
    }
    return zoomLatLngOutputStream;
}

function getDomMapBool(dataAttName, domId) {
    return (getDomMapAttribute(dataAttName, domId) == 'True');
}

function getDomMapAttribute(dataAttName, domId) {
    domId = domId || 'map';
    var $map = $('#' + domId),
        value = $map.data(dataAttName);
    return value;
}

// Work around https://github.com/Leaflet/Leaflet/issues/1905
function fixZoomLayerSwitch(map, layer) {
    map.on('zoomend', function(e) {
        var zoom = map.getZoom();
        if (zoom < MIN_ZOOM_OPTION.minZoom) {
            layer._clearBgBuffer();
        }
    });
}

function addCustomLayer(mapManager, layerInfo) {
    var layer = layersLib.createCustomLayer(layerInfo);
    mapManager.layersControl.addOverlay(layer, layerInfo.name);
    if (layerInfo.showByDefault) {
        mapManager.map.addLayer(layer);
    }
}

module.exports = MapManager;
