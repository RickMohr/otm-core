"use strict";

var $ = require('jquery'),
    _ = require('lodash'),
    Bootstrap = require('bootstrap'),  // for $(...).collapse()
    Bacon = require('baconjs'),
    url = require('url'),
    addTreeModeName = require('treemap/mapPage/addTreeMode.js').name,
    addResourceModeName = require('treemap/mapPage/addResourceMode.js').name,
    BU = require('treemap/lib/baconUtils.js'),
    buttonEnabler = require('treemap/lib/buttonEnabler.js'),
    MapPage = require('treemap/lib/mapPage.js'),
    modes = require('treemap/mapPage/modes.js'),
    adHocPolygon = require('treemap/mapPage/adHocPolygon.js'),
    Search = require('treemap/lib/search.js');

function changeMode (modeOptions) {
    var modeName = modeOptions.modeName,
        type = modeOptions.modeType;

    if (modeName === addTreeModeName) {
        modes.activateAddTreeMode(false);
    } else if (modeName === addResourceModeName) {
        modes.activateAddResourceMode(false, type);
    } else {
        modes.activateBrowseTreesMode(false);
    }
}

var mapPage = MapPage.init({
        domId: 'map',
        trackZoomLatLng: true,
        fillSearchBoundary: true,
        saveSearchInUrl: true
    }),
    mapManager = mapPage.mapManager,

    triggerSearchFromSidebar = new Bacon.Bus(),

    ecoBenefitsSearchEvents =
        Bacon.mergeAll(
            mapPage.builtSearchEvents,
            triggerSearchFromSidebar.map(mapPage.getMapStateSearch)
        ),

    modeChangeStream = mapPage.mapStateChangeStream
        .filter(BU.isPropertyDefined('modeName')),

    completedEcobenefitsSearchStream = Search.init(
        ecoBenefitsSearchEvents,
        _.bind(mapManager.setFilter, mapManager));


modeChangeStream.onValue(changeMode);

var performAdd = function (e, addFn) {
    var btn = e.target;

    if (!mapPage.embed) {
        var type = $(btn).attr('data-class');
        e.preventDefault();
        addFn(false, type);
    } else {
        var href = btn.href,
            parsedHref = url.parse(href, true),
            currentLocation = url.parse(location.href, true),
            adjustedQuery = _.chain({})
                .assign(currentLocation.query, parsedHref.query)
                .omit('embed')
                .value();
        parsedHref.search = null;
        parsedHref.query = adjustedQuery;
        btn.href = url.format(parsedHref);
        // allow default
    }
};

$('[data-action="addtree"]').click(function(e) {
    performAdd(e, modes.activateAddTreeMode);
});

$('[data-action="addresource"]').click(function(e) {
    performAdd(e, modes.activateAddResourceMode);
});

buttonEnabler.run();

modes.init(mapManager, triggerSearchFromSidebar, mapPage.embed,
    completedEcobenefitsSearchStream);

adHocPolygon.init({
    map: mapManager.map
});

// Read state from current URL, initializing
// zoom/lat/long/search/mode/selection
mapPage.initMapState();

// Toggle class on panel-group when toggle is tapped to show/hide
// expanded view on mobile
var prevCenter;
$('#feature-panel').on('click', '.sidebar-panel-toggle', function() {
    $('body').toggleClass('hide-search open');
    $('#feature-panel').toggleClass('expanded with-map');

    // Recenter map on selected feature when shrinking it
    // Put it back to previous center when enlarging it again
    var latLon = prevCenter;
    if ($('body').is('.open')) {
        prevCenter = mapPage.map.getCenter();
        latLon = $("#map-feature-popup").data('latlon');
    }
    mapPage.map.invalidateSize();
    mapPage.map.panTo(latLon, {
        animate: true,
        duration: 0.4,
        easeLinearity: 0.1
    });
});

$('#eco-panel').on('click', '.sidebar-panel-toggle', function() {
    $('#eco-panel').toggleClass('expanded full');
});
