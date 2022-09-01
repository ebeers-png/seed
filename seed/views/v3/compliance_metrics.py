# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2022, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.
:author
"""
from copy import deepcopy

import django.core.exceptions
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets

from seed.decorators import ajax_request_class, require_organization_id_class
from seed.lib.superperms.orgs.decorators import has_perm_class
from seed.lib.superperms.orgs.models import Organization
from seed.models.compliance_metrics import ComplianceMetric
from seed.serializers.compliance_metrics import ComplianceMetricSerializer
from seed.utils.api import OrgMixin, api_endpoint_class
from seed.utils.api_schema import (
    AutoSchemaHelper,
    swagger_auto_schema_org_query_param
)


class ComplianceMetricViewSet(viewsets.ViewSet, OrgMixin):
    serializer_class = ComplianceMetricSerializer
    model = ComplianceMetric

    @swagger_auto_schema_org_query_param
    @require_organization_id_class
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_viewer')
    def list(self, request):
        organization_id = self.get_organization(request)

        # temporary: get or create default metric first, then retrieve all to put in correct format
        the_org = Organization.objects.get(id=organization_id)
        ComplianceMetric.get_or_create_default(the_org)
        compliance_metric_queryset = ComplianceMetric.objects.filter(organization=organization_id)

        return JsonResponse({
            'status': 'success',
            'compliance_metrics': ComplianceMetricSerializer(compliance_metric_queryset, many=True).data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema_org_query_param
    @require_organization_id_class
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_viewer')
    def retrieve(self, request, pk):
        organization = self.get_organization(request)

        try:
            return JsonResponse({
                'status': 'success',
                'compliance_metric': ComplianceMetricSerializer(
                    ComplianceMetric.objects.get(id=pk, organization=organization)
                ).data
            }, status=status.HTTP_200_OK)
        except ComplianceMetric.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'ComplianceMetric with id {pk} does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema_org_query_param
    @require_organization_id_class
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_owner')
    def destroy(self, request, pk):
        organization_id = self.get_organization(request)

        try:
            ComplianceMetric.objects.get(id=pk, organization=organization_id).delete()
        except ComplianceMetric.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'ComplianceMetric with id {pk} does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({
            'status': 'success',
            'message': f'Successfully deleted ComplianceMetric ID {pk}'
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        request_body=AutoSchemaHelper.schema_factory(
            {
                'name': 'string',
                'start': 'string',
                'end': 'string',
                'actual_column': 'integer',
                'target_column': 'integer',
                'metric_type': 'integer',
                'x_axis_columns': ['integer'],
            },
        )
    )
    @require_organization_id_class
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_owner')
    def create(self, request):
        org_id = self.get_organization(request)
        data = deepcopy(request.data)
        data.update({'organization': org_id})
        serializer = ComplianceMetricSerializer(data=data)

        if not serializer.is_valid():
            error_response = {
                'status': 'error',
                'message': 'Data Validation Error',
                'errors': serializer.errors
            }

            return JsonResponse(error_response, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
            return JsonResponse({
                'status': 'success',
                'compliance_metric': serializer.data
            }, status=status.HTTP_200_OK)
        except django.core.exceptions.ValidationError as e:

            message_dict = e.message_dict
            return JsonResponse({
                'status': 'error',
                'message': 'Bad Request',
                'errors': message_dict
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[AutoSchemaHelper.query_org_id_field()],
        request_body=AutoSchemaHelper.schema_factory(
            {
                'name': 'string',
                'start': 'string',
                'end': 'string',
                'actual_column': 'integer',
                'target_column': 'integer',
                'metric_type': 'integer',
                'x_axis_columns': ['integer'],
            },
        )
    )
    @require_organization_id_class
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_owner')
    def update(self, request, pk):
        org_id = self.get_organization(request)

        compliance_metric = None
        try:
            compliance_metric = ComplianceMetric.objects.get(id=pk, organization=org_id)
        except ComplianceMetric.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': f'ComplianceMetric with id {pk} does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        data = deepcopy(request.data)
        data.update({'organization': org_id})
        serializer = ComplianceMetricSerializer(compliance_metric, data=data, partial=True)
        if not serializer.is_valid():
            return JsonResponse({
                'status': 'error',
                'message': 'Bad Request',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
            return JsonResponse({
                'status': 'success',
                'compliance_metric': serializer.data,
            }, status=status.HTTP_200_OK)
        except django.core.exceptions.ValidationError as e:
            message_dict = e.message_dict

            # rename key __all__ to general to make it more user friendly
            if '__all__' in message_dict:
                message_dict['general'] = message_dict.pop('__all__')

            return JsonResponse({
                'status': 'error',
                'message': 'Bad request',
                'errors': message_dict,
            }, status=status.HTTP_400_BAD_REQUEST)
