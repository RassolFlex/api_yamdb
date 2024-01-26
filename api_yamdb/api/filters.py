from django_filters import rest_framework as filters

from reviews.models import Title


class TitleSearchFilter(filters.FilterSet):
    genre = filters.CharFilter(field_name='genre')
    category = filters.CharFilter(field_name='category')
    year = filters.CharFilter(field_name='year')

    class Meta:
        model = Title
        fields = ['genre', 'year', 'category']