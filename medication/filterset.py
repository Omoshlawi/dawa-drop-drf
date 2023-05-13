from django_filters.rest_framework import filterset, filters

from medication.models import AppointMent


class AppointMentFilterSet(filterset.FilterSet):
    type = filters.CharFilter(field_name='type', lookup_expr="type", label="Filter by AppointMent Type")

    class Meta:
        model = AppointMent
        fields = ('type',)
