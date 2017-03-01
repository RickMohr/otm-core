"use strict";

var $ = require('jquery'),
    _ = require('lodash'),
    Bacon = require('baconjs');

var dom = {
    locationInput: '#boundary-typeahead',
    locationSearched: '#location-searched .text',
    drawArea: '.draw-area',
    clearLocationInput: '.clear-location-input',
    clearLocationSearch: '.clear-location-search',
    clearCustomArea: '.clear-custom-area',
    controls: {
        standard: '#location-search-well',
        searched: '#location-searched',
        drawArea: '#draw-area-controls',
        customArea: '#custom-area-controls',
        editArea: '#edit-area-controls'
    }
};

var map,
    searchBar,
    polygon;

function init(options) {
    map = options.map;
    searchBar = options.searchBar;
    // $(dom.locationInput).on('keyup', showAppropriateButton);
    $(dom.clearCustomArea).click(clearCustomArea);
    $(dom.clearLocationInput).click(clearLocationInput);
    $(dom.clearLocationSearch).click(clearLocationSearch);
    Bacon.mergeAll(
        searchBar.geocodedLocationStream,
        searchBar.filterNonGeocodeObjectStream
    ).onValue(showSearchedLocation);
}

// function showAppropriateButton() {
//     var hasValue = ($(dom.locationInput).val().length > 0);
//     $(dom.drawArea).toggle(!hasValue);
//     $(dom.clearLocationInput).toggle(hasValue);
// }

function showSearchedLocation() {
    var text = $(dom.locationInput).val();
    $(dom.locationSearched).html(text);
    showControls(dom.controls.searched);
}

function getPolygon() {
    return polygon;
}

function setPolygon(newPolygon) {
    polygon = newPolygon.addTo(map);
}

function clearLocationInput() {
    $(dom.locationInput).val('');
    // showAppropriateButton();
}

function clearLocationSearch() {
    showControls(dom.controls.standard);
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
