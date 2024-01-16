from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator


from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Review
