# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from treemap.decorators import classproperty
from treemap.models import MapFeature, GeoHStoreUDFManager
from treemap.ecobenefits import CountOnlyBenefitCalculator


class PolygonalMapFeature(MapFeature):
    area_field_name = 'polygon'
    skip_detail_form = True

    polygon = models.MultiPolygonField(srid=3857)

    objects = GeoHStoreUDFManager()

    def __init__(self, *args, **kwargs):
        super(PolygonalMapFeature, self).__init__(*args, **kwargs)
        self._do_not_track.add('polygonalmapfeature_ptr')
        self.populate_previous_state()

    @property
    def is_editable(self):
        # this is a holdover until we can support editing for all resources
        return True

    @classproperty
    def benefits(cls):
        return CountOnlyBenefitCalculator(cls)

    def calculate_area(self):
        """
        Make a PostGIS query that accurately calculates the area of
        the polygon by first casting it to a Geography.
        """
        if self.pk is None:
            return None
        area_sql = 'ST_Area(ST_Transform(polygon, 4326)::geography)'
        area_col_name = 'area'
        return PolygonalMapFeature.objects \
                                  .filter(pk=self.pk) \
                                  .extra(select={area_col_name: area_sql}) \
                                  .values(area_col_name)[0][area_col_name]


class Bioswale(PolygonalMapFeature):
    objects = GeoHStoreUDFManager()

    udf_settings = {
        'Perennial Plants': {
            'iscollection': False,
            'defaults': {
                'type': 'multichoice',
                'choices': [
                    "Black-eyed Susan - Rudbeckia hirta",
                    "Daylily - Hemerocallis",
                    "Lobelia - Lobelia",
                    "Sedge - Carex",
                    "Switchgrass - Panicum virgatum",
                ],
            }
        },
        'Stewardship': {
            'iscollection': True,
            'range_field_key': 'Date',
            'action_field_key': 'Action',
            'action_verb': 'that have been',
            'defaults': [
                {'name': 'Action',
                 'choices': [
                     'Removed litter',
                     'Removed weeds',
                     'Pruned plants',
                     'Pruned trees',
                     'Watered bioswale',
                     'Removed sediments',
                     'Redistributed gravel',
                     'Redistributed soil',
                     'Aerated soil',
                 ],
                 'type': 'choice'},
                {'type': 'date',
                 'name': 'Date'}],
        }
    }

    default_config = {
        'singular': _('Bioswale'),
        'plural': _('Bioswales'),
        'should_show_eco': True,
        'diversion_rate': 0.95,
    }


class RainGarden(PolygonalMapFeature):
    objects = GeoHStoreUDFManager()

    udf_settings = {
        'Perennial Plants': {
            'iscollection': False,
            'defaults': {
                'type': 'multichoice',
                'choices': [
                    "Black-eyed Susan - Rudbeckia hirta",
                    "Daylily - Hemerocallis",
                    "Lobelia - Lobelia",
                    "Sedge - Carex",
                    "Switchgrass - Panicum virgatum",
                ],
            },
        },
        'Stewardship': {
            'iscollection': True,
            'range_field_key': 'Date',
            'action_field_key': 'Action',
            'action_verb': 'that have been',
            'defaults': [
                {'name': 'Action',
                 'choices': [
                     'Removed litter',
                     'Removed weeds',
                     'Pruned plants',
                     'Pruned trees',
                     'Watered bioswale',
                     'Removed sediments',
                     'Redistributed gravel',
                     'Redistributed soil',
                     'Aerated soil',
                 ],
                 'type': 'choice'},
                {'type': 'date',
                 'name': 'Date'}],
        },
    }

    default_config = {
        'singular': _('Rain Garden'),
        'plural': _('Rain Gardens'),
        'should_show_eco': True,
        'diversion_rate': 0.95,
    }


class RainBarrel(MapFeature):
    objects = GeoHStoreUDFManager()
    capacity = models.FloatField(
        verbose_name=_("Capacity"),
        error_messages={'invalid': _("Please enter a number.")})

    default_config = {
        'singular': _('Rain Barrel'),
        'plural': _('Rain Barrels'),
        'should_show_eco': False,
    }

    @classproperty
    def benefits(cls):
        return CountOnlyBenefitCalculator(cls)

    @property
    def is_editable(self):
        # this is a holdover until we can support editing for all resources
        return True
