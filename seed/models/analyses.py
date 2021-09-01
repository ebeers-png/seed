# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2021, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from django.contrib.postgres.fields import JSONField
from django.db import models

from seed.landing.models import SEEDUser as User
from seed.lib.superperms.orgs.models import Organization

import logging
logger = logging.getLogger(__name__)

class Analysis(models.Model):
    """
    The Analysis represents an analysis performed on one or more properties.
    """
    BSYNCR = 1
    BETTER = 2
    EUI = 3

    SERVICE_TYPES = (
        (BSYNCR, 'BSyncr'),
        (BETTER, 'BETTER'),
        (EUI, 'EUI')
    )

    PENDING_CREATION = 8
    CREATING = 10
    READY = 20
    QUEUED = 30
    RUNNING = 40
    FAILED = 50
    STOPPED = 60
    COMPLETED = 70

    STATUS_TYPES = (
        (PENDING_CREATION, 'Pending Creation'),
        (CREATING, 'Creating'),
        (READY, 'Ready'),
        (QUEUED, 'Queued'),
        (RUNNING, 'Running'),
        (FAILED, 'Failed'),
        (STOPPED, 'Stopped'),
        (COMPLETED, 'Completed'),
    )

    name = models.CharField(max_length=255, blank=False, default=None)
    service = models.IntegerField(choices=SERVICE_TYPES)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(default=PENDING_CREATION, choices=STATUS_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    configuration = JSONField(default=dict, blank=True)
    # parsed_results can contain any results gathered from the resulting file(s)
    # that are applicable to the entire analysis (ie all properties involved).
    # For property-specific results, use the AnalysisPropertyView's parsed_results
    parsed_results = JSONField(default=dict, blank=True)

    def get_property_view_info(self, property_id=None):
        if property_id is not None:
            analysis_property_views = self.analysispropertyview_set.filter(property=property_id)
        else:
            analysis_property_views = self.analysispropertyview_set

        return {
            'number_of_analysis_property_views': analysis_property_views.count(),
            'views': list(analysis_property_views.values_list('id', flat=True).distinct()),
            'cycles': list(analysis_property_views.values_list('cycle', flat=True).distinct())
        }

    def get_highlights(self, property_id):
        if self.status < self.COMPLETED:
            return []
        for view in self.analysispropertyview_set.filter(property=property_id):
            extra_data = view.property_state.extra_data
            break

        # Bsynchr
        if self.service == self.BSYNCR:
            return [{'name':'Unimplemented','value':'Oops!'}]

        # BETTER
        elif self.service == self.BETTER:
            ret = []
            if 'better_cost_savings_combined' in extra_data:
                ret.append({
                    'name': 'Potential Cost Savings (USD)',
                    'value': f'${extra_data["better_cost_savings_combined"]:,.2f}'
                })
            if 'better_energy_savings_combined' in extra_data:
                value = 1.2
                ret.append({
                    'name': 'Potential Energy Savings (kWh)',
                    'value': f'{extra_data["better_energy_savings_combined"]:,.2f}'
                })
            return ret

        # EUI
        elif self.service == self.EUI:
            return [{'name': 'EUI', 'value': f'{extra_data["analysis_eui"]:,.2f}'}]

        # Unexpected
        return [{'name':'Unexpected Analysis Type','value':'Oops!'}]
        

    def in_terminal_state(self):
        """Returns True if the analysis has finished, e.g. stopped, failed,
        completed, etc

        :returns: bool
        """
        return self.status in [self.FAILED, self.STOPPED, self.COMPLETED]
