# -*- coding: utf-8 -*-
# flake8: noqa
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


# OTM modeling internal land use codes (from Baltimore mortality model)
Forest                      = 0
UrbanOpen                   = 1
LowMediumDensityResidential = 2
HighDensityResidential      = 3
Transportation              = 4
CommercialIndustrial        = 5
Institutional               = 6
Barren                      = 7
Exclude                     = None

land_use_names = {
    Forest                     : 'Forest'                        ,
    UrbanOpen                  : 'Urban Open'                    ,
    LowMediumDensityResidential: 'Low-Medium Density Residential',
    HighDensityResidential     : 'High Density Residential'      ,
    Transportation             : 'Transportation'                ,
    CommercialIndustrial       : 'Commercial/Industrial'         ,
    Institutional              : 'Institutional'                 ,
    Barren                     : 'Barren'                        ,
}


def get_land_use_categories():
    return [
        {
            'code': land_use_code,
            'mapping_code': mapping_code,
            'name': land_use_names.get(land_use_code, '')
        }
        for mapping_code, land_use_code in nlcd_mapping.iteritems()
        if land_use_code
        ]


# Map land use codes from National Land Cover Database (NLCD) to internal codes

nlcd_mapping = {
    11: Exclude,                      # Open Water
    12: Exclude,                      # Perennial Ice/Snow
    21: UrbanOpen,                    # Developed, Open Space
    22: LowMediumDensityResidential,  # Developed, Low Intensity
    23: LowMediumDensityResidential,  # Developed, Medium Intensity
    24: HighDensityResidential,       # Developed High Intensity
    31: Barren,                       # Barren Land
    41: Forest,                       # Deciduous Forest
    42: Forest,                       # Evergreen Forest
    43: Forest,                       # Mixed Forest
    51: Forest,                       # Dwarf Scrub
    52: Forest,                       # Shrub/Scrub
    71: UrbanOpen,                    # Grassland/Herbaceous
    72: UrbanOpen,                    # Sedge/Herbaceous
    73: Exclude,                      # Lichens
    74: Exclude,                      # Moss
    81: UrbanOpen,                    # Pasture/Hay
    82: UrbanOpen,                    # Cultivated Crops
    90: Forest,                       # Woody Wetlands
    95: Forest,                       # Emergent Herbaceous Wetlands
}
