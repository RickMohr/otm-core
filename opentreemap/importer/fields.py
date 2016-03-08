# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


class species_capitalized(object):
    # Fields of the OTM Species object
    GENUS = 'Genus'
    SPECIES = 'Species'
    CULTIVAR = 'Cultivar'
    OTHER_PART_OF_NAME = 'Other Part of Name'
    COMMON_NAME = 'Common Name'
    IS_NATIVE = 'Is Native'
    FLOWERING_PERIOD = 'Flowering Period'
    FRUIT_OR_NUT_PERIOD = 'Fruit or Nut Period'
    FALL_CONSPICUOUS = 'Fall Conspicuous'
    FLOWER_CONSPICUOUS = 'Flower Conspicuous'
    PALATABLE_HUMAN = 'Palatable Human'
    HAS_WILDLIFE_VALUE = 'Has Wildlife Value'
    FACT_SHEET_URL = 'Fact Sheet URL'
    PLANT_GUIDE_URL = 'Plant Guide URL'
    MAX_DIAMETER = 'Max Diameter'
    MAX_HEIGHT = 'Max Height'

    # Other import and/or export fields
    ID = 'Database ID of Species'
    ITREE_CODE = 'i-Tree Code'

    # This is a pseudo field which is filled in
    # when a matching species is found, but before
    # a commit is made. It is a list of all species
    # that somehow match this one (usda, sci name)
    POSSIBLE_MATCHES = 'calc__species'

    # This is a pseudo field which is filled in
    # when a matching itree code is found
    ITREE_PAIRS = 'calc__itree'

    DATE_FIELDS = set()

    STRING_FIELDS = {GENUS, SPECIES, CULTIVAR, OTHER_PART_OF_NAME,
                     COMMON_NAME, ITREE_CODE, FLOWERING_PERIOD,
                     FRUIT_OR_NUT_PERIOD, FACT_SHEET_URL,
                     PLANT_GUIDE_URL}

    POS_FLOAT_FIELDS = {MAX_DIAMETER, MAX_HEIGHT}

    FLOAT_FIELDS = set()

    POS_INT_FIELDS = set()

    BOOLEAN_FIELDS = {IS_NATIVE, FALL_CONSPICUOUS, PALATABLE_HUMAN,
                      FLOWER_CONSPICUOUS, HAS_WILDLIFE_VALUE}

    # Note: this is a tuple and not a set so it will be ordered in exports
    ALL = (GENUS, SPECIES, CULTIVAR, OTHER_PART_OF_NAME, ITREE_CODE,
           COMMON_NAME, IS_NATIVE, FLOWERING_PERIOD, FRUIT_OR_NUT_PERIOD,
           FALL_CONSPICUOUS, FLOWER_CONSPICUOUS, PALATABLE_HUMAN,
           HAS_WILDLIFE_VALUE, FACT_SHEET_URL, PLANT_GUIDE_URL, MAX_DIAMETER,
           MAX_HEIGHT)

    PLOT_CHOICES = set()


class trees_capitalized(object):
    # X/Y are required
    POINT_X = 'Point X'
    POINT_Y = 'Point Y'

    # This is a pseudo field which is filled in
    # when data is cleaned and contains a GEOS
    # point object
    POINT = 'calc__point'

    # This is a pseudo field which is filled in
    # when data is cleaned and may contain a
    # OTM Species object, if the species was
    # matched
    SPECIES_OBJECT = 'calc__species_object'

    # Plot Fields
    STREET_ADDRESS = 'Street Address'
    CITY_ADDRESS = 'City'
    POSTAL_CODE = 'Postal Code'
    PLOT_WIDTH = 'Planting Site Width'
    PLOT_LENGTH = 'Planting Site Length'

    # TODO: READONLY restore when implemented
    # READ_ONLY = 'Read Only'

    OPENTREEMAP_PLOT_ID = 'Planting Site ID'
    EXTERNAL_ID_NUMBER = 'Owner Original ID'

    TREE_PRESENT = 'Tree Present'

    # Tree Fields (species matching)
    GENUS = species_capitalized.GENUS
    SPECIES = species_capitalized.SPECIES
    CULTIVAR = species_capitalized.CULTIVAR
    OTHER_PART_OF_NAME = species_capitalized.OTHER_PART_OF_NAME
    COMMON_NAME = species_capitalized.COMMON_NAME

    # Tree fields
    DIAMETER = 'Diameter'
    TREE_HEIGHT = 'Tree Height'
    CANOPY_HEIGHT = 'Canopy Height'
    DATE_PLANTED = 'Date Planted'
    DATE_REMOVED = 'Date Removed'

    # order matters, so this is a tuple and not a set
    SPECIES_FIELDS = (GENUS, SPECIES, CULTIVAR, OTHER_PART_OF_NAME,
                      COMMON_NAME)

    DATE_FIELDS = {DATE_PLANTED, DATE_REMOVED}

    STRING_FIELDS = {STREET_ADDRESS, CITY_ADDRESS, POSTAL_CODE, GENUS,
                     SPECIES, CULTIVAR, OTHER_PART_OF_NAME, COMMON_NAME,
                     EXTERNAL_ID_NUMBER}

    POS_FLOAT_FIELDS = {PLOT_WIDTH, PLOT_LENGTH, DIAMETER, TREE_HEIGHT,
                        CANOPY_HEIGHT}

    FLOAT_FIELDS = {POINT_X, POINT_Y}

    POS_INT_FIELDS = {OPENTREEMAP_PLOT_ID}

    # TODO: READONLY restore when implemented
    BOOLEAN_FIELDS = {TREE_PRESENT}

    EXPORTER_PAIRS = (
        ('geom__x', POINT_X),
        ('geom__y', POINT_Y),
        ('address_street', STREET_ADDRESS),
        ('address_city', CITY_ADDRESS),
        ('address_zip', POSTAL_CODE),
        ('width', PLOT_WIDTH),
        ('length', PLOT_LENGTH),
        ('tree__plot', OPENTREEMAP_PLOT_ID),
        ('owner_orig_id', EXTERNAL_ID_NUMBER),
        ('tree_present', TREE_PRESENT),
        ('tree__species__genus', GENUS),
        ('tree__species__species', SPECIES),
        ('tree__species__cultivar', CULTIVAR),
        ('tree__species__other_part_of_name', OTHER_PART_OF_NAME),
        ('tree__species__common_name', COMMON_NAME),
        ('tree__diameter', DIAMETER),
        ('tree__height', TREE_HEIGHT),
        ('tree__canopy_height', CANOPY_HEIGHT),
        ('tree__date_planted', DATE_PLANTED),
        ('tree__date_removed', DATE_REMOVED),
    )

    # TODO: READONLY restore when implemented
    # Note: this is a tuple and not a set so it will be ordered in exports
    ALL = tuple([p[1] for p in EXPORTER_PAIRS])


class species(object):
    pass


class trees(object):
    pass


def duplicate_with_lower_case_names(cls_capitalized, cls):
    def is_string(t):
        return t is str or t is unicode

    for attr in cls_capitalized.__dict__.keys():
        if attr[:1] != '_':
            val = getattr(cls_capitalized, attr)
            t = type(val)
            if is_string(t):
                val = val.lower()
            elif t is list or t is tuple or t is set:
                val = t(item.lower() for item in val if is_string(type(item)))

            setattr(cls, attr, val)


duplicate_with_lower_case_names(trees_capitalized, trees)
duplicate_with_lower_case_names(species_capitalized, species)

