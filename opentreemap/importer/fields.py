# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


class FieldNames(object):
    @classmethod
    def downcase_names(cls):
        # Much code expects lower-case field names, but we want to show
        # capitalized field names in the UI and in exported CSV's.
        # So downcase everything but create a dict to map back
        # (from a lowercased field name to its capitalized original).
        def is_string(t):
            return t is str or t is unicode

        for attr in cls.__dict__.keys():
            if attr[:1] != '_' and not '__' in attr:
                val = getattr(cls, attr)
                t = type(val)
                if is_string(t):
                    cls._capitalized_field_names[val.lower()] = val
                    val = val.lower()
                    setattr(cls, attr, val)
                elif t is list or t is tuple or t is set:
                    if len(val) > 0 and is_string(type(next(iter(val)))):
                        # val is a sequence of strings
                        val = t(item.lower() for item in val)
                        setattr(cls, attr, val)

    @classmethod
    def capitalize(cls, field_names):
        t = type(field_names)
        capitalized = t(cls._capitalized_field_names.get(n, n)
                        for n in field_names)
        return capitalized


class species(FieldNames):
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

    _capitalized_field_names = {}


class trees(FieldNames):
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
    GENUS = species.GENUS
    SPECIES = species.SPECIES
    CULTIVAR = species.CULTIVAR
    OTHER_PART_OF_NAME = species.OTHER_PART_OF_NAME
    COMMON_NAME = species.COMMON_NAME

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

    _capitalized_field_names = {}


species.downcase_names()
trees.downcase_names()
