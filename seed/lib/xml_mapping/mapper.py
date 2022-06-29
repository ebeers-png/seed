# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
:author
"""

from __future__ import absolute_import

import logging

from buildingsync_asset_extractor.processor import BSyncProcessor as BAE

from seed.building_sync.building_sync import BuildingSync
from seed.building_sync.mappings import (
    BASE_MAPPING_V2,
    merge_mappings,
    xpath_to_column_map
)

_log = logging.getLogger(__name__)


def build_column_mapping(base_mapping=None, custom_mapping=None):
    if base_mapping is None:
        base_mapping = BuildingSync.VERSION_MAPPINGS_DICT[BuildingSync.BUILDINGSYNC_V2_0]
    merged_map = merge_mappings(base_mapping, custom_mapping)
    column_mapping = xpath_to_column_map(merged_map)
    return {
        xpath: ('PropertyState', db_column, 100)
        for xpath, db_column in column_mapping.items()
    }

def get_valid_units():
    # taken from mapping partial (./static/seed/partials/mapping.html)
    valid_units = [
        # area units
        "ft**2",
        "m**2",
        # eui_units
        "kBtu/ft**2/year",
        "kWh/m**2/year",
        "GJ/m**2/year",
        "MJ/m**2/year",
        "kBtu/m**2/year",
        # from BAE
        "F"
    ]
    return valid_units

def get_BAE_mappings():
    results = []
    valid_units = get_valid_units()
    # results
    bsync_assets = BAE.get_default_asset_defs()
    for item in bsync_assets:
        from_units = None
        if 'units' in item:
            from_units = item['units']
        # only add units defined above
        if from_units not in valid_units:
            from_units = None
        if item['type'] == 'sqft':
            # these types need 2 different entries: 1 for "primary" and 1 for "secondary"
            for i in ['Primary', 'Secondary']:
                results.append({
                    'from_field': i + ' ' + item['export_name'],
                    'from_field_value': 'text',  # hard code this for now
                    'from_units': from_units,
                    'to_field': i + ' ' + item['export_name'],
                    'to_table_name': 'PropertyState'
                })
        else:
            results.append({
                'from_field': item['export_name'],
                'from_field_value': 'text',  # hard code this for now
                'from_units': from_units,
                'to_field': item['export_name'],
                'to_table_name': 'PropertyState'
            })
    return results


def default_buildingsync_profile_mappings():
    """Returns the default ColumnMappingProfile mappings for BuildingSync
    :return: list
    """
    valid_Units = get_valid_units()

    mapping = BASE_MAPPING_V2.copy()
    base_path = mapping['property']['xpath'].rstrip('/')
    result = []
    for col_name, col_info in mapping['property']['properties'].items():
        from_units = col_info.get('units')
        if from_units not in valid_units:
            from_units = None

        sub_path = col_info['xpath'].replace('./', '')
        absolute_xpath = f'{base_path}/{sub_path}'
        result.append({
            'from_field': absolute_xpath,
            'from_field_value': col_info['value'],
            'from_units': from_units,
            'to_field': col_name,
            'to_table_name': 'PropertyState'
        })

    # BAE results
    bae_results = get_BAE_mappings()
    result.extend(bae_results)

    return result
