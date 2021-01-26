# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2020, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from django.db.models import Count
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.decorators import action

from seed.analysis_pipelines.pipeline import AnalysisPipeline, AnalysisPipelineException
from seed.decorators import ajax_request_class
from seed.lib.superperms.orgs.decorators import has_perm_class
from seed.models import Analysis, Cycle, PropertyView, PropertyState
from seed.serializers.analyses import AnalysisSerializer
from seed.utils.api import api_endpoint_class, OrgValidateMixin
from seed.utils.api_schema import AutoSchemaHelper
from seed.utils.viewsets import SEEDOrgCreateUpdateModelViewSet


class CreateAnalysisSerializer(AnalysisSerializer):
    property_view_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    class Meta:
        model = Analysis
        fields = ['name', 'service', 'configuration', 'property_view_ids']

    def create(self, validated_data):
        return Analysis.objects.create(
            name=validated_data['name'],
            service=validated_data['service'],
            configuration=validated_data.get('configuration', {}),
            user_id=validated_data['user_id'],
            organization_id=validated_data['organization_id']
        )


class AnalysisViewSet(OrgValidateMixin, SEEDOrgCreateUpdateModelViewSet):
    serializer_class = AnalysisSerializer
    model = Analysis

    @swagger_auto_schema(
        manual_parameters=[
            AutoSchemaHelper.query_org_id_field(),
        ],
        request_body=CreateAnalysisSerializer,
    )
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_member')
    def create(self, request):
        serializer = CreateAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                'status': 'error',
                'message': 'Bad request',
                'errors': serializer.errors
            })

        analysis = serializer.save(
            user_id=request.user.id,
            organization_id=request.query_params['organization_id']
        )
        pipeline = AnalysisPipeline.factory(analysis)
        try:
            progress_data = pipeline.prepare_analysis(serializer.validated_data['property_view_ids'])
            return JsonResponse({
                'status': 'success',
                'progress_key': progress_data['progress_key'],
                'progress': progress_data,
            })
        except AnalysisPipelineException as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_409_CONFLICT)

    @swagger_auto_schema(
        manual_parameters=[
            AutoSchemaHelper.query_org_id_field(True),
            AutoSchemaHelper.query_integer_field('property_id', False, 'Property ID')
        ]
    )
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_member')
    def list(self, request):
        organization_id = request.query_params.get('organization_id', None)
        property_id = request.query_params.get('property_id', None)
        analyses = []
        if property_id is not None:
            analyses_queryset = (
                Analysis.objects.filter(organization=organization_id, analysispropertyview__property=property_id)
                .distinct()
                .order_by('-id')
            )
        else:
            analyses_queryset = (
                Analysis.objects.filter(organization=organization_id)
                .order_by('-id')
            )
        for analysis in analyses_queryset:
            property_view_info = analysis.get_property_view_info(property_id)
            serialized_analysis = AnalysisSerializer(analysis).data
            serialized_analysis.update(property_view_info)
            analyses.append(serialized_analysis)

        return JsonResponse({
            'status': 'success',
            'analyses': analyses
        })

    @swagger_auto_schema(manual_parameters=[AutoSchemaHelper.query_org_id_field(True)])
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_member')
    def retrieve(self, request, pk):
        organization_id = int(request.query_params.get('organization_id', 0))
        try:
            analysis = Analysis.objects.get(id=pk, organization_id=organization_id)
        except Analysis.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': "Requested analysis doesn't exist in this organization."
            }, status=status.HTTP_409_CONFLICT)
        serialized_analysis = AnalysisSerializer(analysis).data
        property_view_info = analysis.get_property_view_info()
        serialized_analysis.update(property_view_info)

        return JsonResponse({
            'status': 'success',
            'analysis': serialized_analysis
        })

    @swagger_auto_schema(manual_parameters=[AutoSchemaHelper.query_org_id_field()])
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_member')
    @action(detail=True, methods=['post'])
    def start(self, request, pk):
        organization_id = int(request.query_params.get('organization_id', 0))
        try:
            analysis = Analysis.objects.get(id=pk, organization_id=organization_id)
            pipeline = AnalysisPipeline.factory(analysis)
            progress_data = pipeline.start_analysis()
            return JsonResponse({
                'status': 'success',
                'progress_key': progress_data['progress_key'],
                'progress': progress_data,
            })
        except Analysis.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Requested analysis doesn\'t exist in this organization.'
            }, status=status.HTTP_409_CONFLICT)
        except AnalysisPipelineException as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_409_CONFLICT)

    @swagger_auto_schema(manual_parameters=[AutoSchemaHelper.query_org_id_field()])
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_member')
    @action(detail=True, methods=['post'])
    def stop(self, request, pk):
        organization_id = int(request.query_params.get('organization_id', 0))
        try:
            analysis = Analysis.objects.get(id=pk, organization_id=organization_id)
            pipeline = AnalysisPipeline.factory(analysis)
            pipeline.stop()
            return JsonResponse({
                'status': 'success',
            })
        except Analysis.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Requested analysis doesn\'t exist in this organization.'
            }, status=status.HTTP_409_CONFLICT)

    @swagger_auto_schema(manual_parameters=[AutoSchemaHelper.query_org_id_field()])
    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_member')
    def destroy(self, request, pk):
        organization_id = int(request.query_params.get('organization_id', 0))
        try:
            analysis = Analysis.objects.get(id=pk, organization_id=organization_id)
            pipeline = AnalysisPipeline.factory(analysis)
            pipeline.delete()
            return JsonResponse({
                'status': 'success',
            })
        except Analysis.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Requested analysis doesn\'t exist in this organization.'
            }, status=status.HTTP_409_CONFLICT)

    @api_endpoint_class
    @ajax_request_class
    @has_perm_class('requires_member')
    @action(detail=False, methods=['get'])
    def stats(self, request):
        org_id = self.get_organization(request)
        cycle_id = request.query_params.get('cycle_id')

        if not cycle_id:
            return JsonResponse({
                'success': False,
                'message': 'cycle_id parameter is missing'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            Cycle.objects.get(id=cycle_id, organization_id=org_id)
        except Cycle.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Cycle does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        views = PropertyView.objects.filter(state__organization_id=org_id, cycle_id=cycle_id)
        states = PropertyState.objects.filter(id__in=views.values_list('state_id', flat=True))
        property_types = states.values('property_type').annotate(count=Count('property_type')).order_by('-count')

        return JsonResponse({
            'status': 'success',
            'total_records': views.count(),
            'property_types': {item['property_type']: item['count'] for item in property_types}
        })
