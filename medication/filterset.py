from django_filters.rest_framework import filterset, filters

from medication.models import AppointMent


class AppointMentFilterSet(filterset.FilterSet):
    type = filters.CharFilter(field_name='type', lookup_expr="type", label="Filter by AppointMent Type")
    next_appointment_date_from = filters.DateFilter(
        field_name='next_appointment_date',
        lookup_expr="gte"
    )
    next_appointment_date_to = filters.DateFilter(
        field_name='next_appointment_date',
        lookup_expr="lte"
    )

    class Meta:
        model = AppointMent
        fields = ('type',)
