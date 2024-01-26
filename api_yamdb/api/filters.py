from django_filters import rest_framework as filters
from django.db.models import Q

from reviews.models import Title


class TitleSearchFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    genre = filters.CharFilter(field_name='genre', method='get_slug')
    category = filters.CharFilter(field_name='category', method='get_slug')
    year = filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ['name', 'genre', 'year', 'category']

    def get_slug(self, queryset, name, value):
        name = f'{name}__slug'
        return queryset.filter(Q((name, value)))
