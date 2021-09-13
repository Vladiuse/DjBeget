from rest_framework.serializers import ModelSerializer

from .models import Domain


class DomainSerializer(ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'beget_id', 'name', 'site', 'description', 'get_http', 'facebook', 'tiktok', 'google']
        read_only_fields = ['id', 'beget_id', 'name', ]
