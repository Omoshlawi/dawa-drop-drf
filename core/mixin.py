from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import Patient
from . import permisions as custom_permission
from rest_framework import permissions, status

from .serializers import PatientOnlyTransferSerializer


class PatientTransferMixin:
    @action(
        detail=False,
        url_path='my-requests',
        url_name='patient-requests',
        methods=['get', 'post'],
        serializer_class=PatientOnlyTransferSerializer,
        permission_classes=[
            permissions.IsAuthenticated,
            custom_permission.IsPatient])
    def my_request(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.post_request(request)
        else:
            return self.get_request(request)

    def post_request(self, request):
        serializer = self.get_serializer(data=request.data)
        patient = Patient.objects.get_or_create(user=request.user)[0]
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(patient=patient)
        return Response(
            data=self.get_serializer(instance=instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def get_request(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        patient = Patient.objects.get_or_create(user=request.user)[0]
        queryset = queryset.filter(patient=patient)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
