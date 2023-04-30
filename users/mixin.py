from rest_framework.decorators import action
from rest_framework.response import Response
from core import permisions as custom_permissions
from rest_framework import permissions


#     @action(detail=True, url_name='patient-detail', permission_classes=[permissions.IsAuthenticated])

class DoctorsMixin:
    @action(detail=False, url_name='doctor-list', url_path='doctors')
    def doctors_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(profile__user_type='doctor')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PatientsMixin:
    @action(
        detail=False, url_name='patient-list', url_path='patients',
        permission_classes=[custom_permissions.IsAgentOrDoctor]
    )
    def patients_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(profile__user_type='patient')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AgentsMixin:
    @action(detail=False, url_name='agent-list', url_path='agents')
    def agents_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(profile__user_type='agent')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, url_name='agent-detail', permission_classes=[permissions.IsAuthenticated])
    def agent_detail(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
