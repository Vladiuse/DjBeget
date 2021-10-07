from rest_framework.serializers import ModelSerializer

from .models import Domain, Company, Country, TrafficSource, Account, Cabinet, CampaignStatus


class DomainSerializer(ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'beget_id', 'name', 'site', 'description', 'get_http', 'facebook', 'tiktok', 'google', 'get_root_domain']
        read_only_fields = ['id', 'beget_id', 'name', ]


class TrafficSourceSerializer(ModelSerializer):
    class Meta:
        model = TrafficSource
        fields = [
            'id', 'name', 'short_name',
        ]


class AccountSerializer(ModelSerializer):
    source = TrafficSourceSerializer()

    class Meta:
        model = Account
        fields = ['id', 'name', 'source', 'description']


class CabinetSerializer(ModelSerializer):
    account = AccountSerializer()
    domain = DomainSerializer()

    class Meta:
        model = Cabinet
        fields = ['id', 'name', 'account', 'description', 'pixel', 'domain']


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CampaignStatusSerializer(ModelSerializer):
    class Meta:
        model = CampaignStatus
        fields = ['id', 'name']


class CompanySerializer(ModelSerializer):
    cab = CabinetSerializer()
    geo = CountrySerializer(many=True, read_only=True)
    land = DomainSerializer(many=True)
    status = CampaignStatusSerializer()

    class Meta:
        model = Company
        fields = ['id', 'name', 'status','cab','geo',  'land', 'published', 'edited']
        # read_only_fields = []
        # extra_kwargs = {'cab': {'required': False},'land': {'required': False}}

    def update(self, instance, validated_data):
        status_id = validated_data.get('status', instance.status)
        instance.status = CampaignStatus.objects.get(pk=status_id)
        for dom in instance.land.all():
            if instance.status.name == 'Запущено' or instance.status.name == 'На расмотрении':
                dom.site.set_site_run()
            else:
                dom.site.set_site_not_run()
        instance.save()
        return instance

class TestSerializer(ModelSerializer):
    class Meta:
        model = Company


