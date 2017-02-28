"use strict";

var $ = require('jquery'),
    _ = require('lodash'),
    L = require('leaflet');

var dom = {
    locationInput: '#boundary-typeahead',
    drawArea: '.draw-area',
    clearLocationSearch: '.clear-location-search',
    clearCustomArea: '.clear-custom-area',
    controls: {
        standard: '#location-search-well',
        drawArea: '#draw-area-controls',
        customArea: '#custom-area-controls',
        editArea: '#edit-area-controls'
    }
};

var map,
    polygon;

function init(options) {
    map = options.map;
    $(dom.locationInput).on('keyup', showAppropriateButton);
    $(dom.clearCustomArea).click(clearCustomArea);
    $(dom.clearLocationSearch).click(clearLocationSearch);
}

function showAppropriateButton() {
    var hasValue = ($(dom.locationInput).val().length > 0);
    $(dom.drawArea).toggle(!hasValue);
    $(dom.clearLocationSearch).toggle(hasValue);
}

function getPolygon() {
    return polygon;
}

function setPolygon(newPolygon) {
    polygon = newPolygon.addTo(map);
}

function clearLocationSearch() {
    $(dom.locationInput).val('');
    showAppropriateButton();
}

function clearCustomArea() {
    if (polygon) {
        map.removeLayer(polygon);
        polygon = null;
    }
    showControls(dom.controls.standard);
}

function showControls(controls) {
    _.each(dom.controls, function (c) {
        $(c).hide();
    });
    $(controls).show();
}

module.exports = {
    init: init,
    getPolygon: getPolygon,
    setPolygon: setPolygon,
    showStandardControls: _.partial(showControls, dom.controls.standard),
    showDrawAreaControls: _.partial(showControls, dom.controls.drawArea),
    showCustomAreaControls: _.partial(showControls, dom.controls.customArea),
    showEditAreaControls: _.partial(showControls, dom.controls.editArea)
};
