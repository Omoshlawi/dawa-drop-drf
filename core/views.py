from rest_framework import reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from . import permisions as custom_permissions
from .models import HIVClinic, DeliveryMode
from .serializers import HIVClinicSerializer, DeliveryModeSerializer


# Create your views here.


class ApiRootView(APIView):
    def get(self, request):
        return Response({
            "users_url": reverse.reverse_lazy('users:user-list', request=request),
            "doctors_url": reverse.reverse_lazy('users:user-doctor-list', request=request),
            "deliver_agents_url": reverse.reverse_lazy('users:user-agent-list', request=request),
            "patients_url": reverse.reverse_lazy('users:user-patient-list', request=request),
            "clinics_url": reverse.reverse_lazy('core:clinic-list', request=request),
            "award_programs_url": reverse.reverse_lazy('awards:program-list', request=request),
            "reward_url": reverse.reverse_lazy('awards:reward-list', request=request),
            "delivery_modes_url": reverse.reverse_lazy('core:mode-list', request=request),
            "orders_url": reverse.reverse_lazy('orders:order-list', request=request),
            "feedback_url": reverse.reverse_lazy('orders:feedback-list', request=request),
            "delivery_url": reverse.reverse_lazy('orders:delivery-list', request=request),
        })


class HIVClinicViewSet(viewsets.ModelViewSet):
    permission_classes = [custom_permissions.IsAdminOrReadOnly]
    queryset = HIVClinic.objects.all()
    serializer_class = HIVClinicSerializer


class DeliveryModeViewSet(viewsets.ModelViewSet):
    permission_classes = [custom_permissions.IsAdminOrReadOnly]
    queryset = DeliveryMode.objects.all()
    serializer_class = DeliveryModeSerializer
