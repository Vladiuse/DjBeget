import requests
import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from pprint import pprint
from .api import Beget, TrirazatApi
from .help import ImagePrev
from .link_checker import LinkCheckerManager
from .models import Site, OldLand, Domain, CodeExample, Company, Account, CampaignStatus, TrafficSource, Cabinet,\
    Country, Lead, RootDomain, SubDomain
from .serializers import DomainSerializer, CompanySerializer, AccountSerializer, TrafficSourceSerializer,\
    CabinetSerializer, CountrySerializer, LeadSerializer
from .new_checker import SiteMap as SiteMap, LinkChecker as NewLinkChecker
from django.views.decorators.csrf import csrf_exempt


DJANGO_SITE = 'https://main-prosale.store/'
NO_CONNECTION = 'Не удалось подключиться'


def main(request):
    return render(request, 'office/index_test.html')


@login_required
def sites(request):
    """Список сайтов, их статусов и тд"""
    # res = Company.objects.exclude(status_name__not="Запущено")
    # print(len(res), 'xxxxxxxxxxxxx')
    # sites = Site.objects.all().order_by('-pk')
    sites = list(Site.objects.exclude(site_name__in=Site.DONT_CHECK))  # исключаються тех сайты
    sites.sort(key=Site.get_sort_name)
    content = {'sites': sites,
               'page_title': 'Сайты',
               }
    return render(request, 'office/index.html', content)


@login_required
def update_sites(request):
    """Обновить список сайтов"""
    # TODO при изменение домена, если можель уже существует - домены не обновяться
    b = Beget()
    sites_id_bd = set([site.beget_id for site in Site.objects.all()])
    sites_beget = b.get_sites()
    sites_beget_id = set([site['id'] for site in sites_beget])
    sites_to_del = sites_id_bd - sites_beget_id
    # сайтов из базы которых нет в ответе с сервера
    for site_beget_id in sites_to_del:
        s = Site.objects.get(beget_id=site_beget_id)
        s.delete()
    for site_beget in sites_beget:
        try:
            site = Site.objects.get(beget_id=site_beget['id'])
        except Site.DoesNotExist:
            # добавление нового сайта
            beget_id = site_beget['id']
            site_name = site_beget['path']
            site = Site(beget_id=beget_id, site_name=site_name, title='None')
            site.save()
            site.check_cloac()
            site.update_title()
        # обновление доменов сайта
        for domain in site_beget['domains']:
            domain_beget_id = domain['id']
            try:
                domain = Domain.objects.get(beget_id=domain_beget_id)
            except ObjectDoesNotExist:
                b.update_domains()
                domain = Domain.objects.get(beget_id=domain_beget_id)
            site.domain_set.add(domain)
        site.save()
    return HttpResponseRedirect(reverse('office:sites'))


@login_required
def get_site_title(request, hard):
    # TODO удалить - перенести в Page
    """Обновить заголовки сайтов"""
    for site in Site.objects.all():
        site.update_title(bool(hard))
        # site.save()
    return HttpResponseRedirect(reverse('office:sites'))


@login_required
def old_lands(request):
    """Архив старых лэндов"""
    host = request.get_host()
    DOMAIN = 'http://vladiuse.beget.tech/'
    SOURCE_URL = 'http://vladiuse.beget.tech/get_lands_list.php'
    res = requests.get(SOURCE_URL)
    lands = res.text.split(';')
    if not lands[-1]:
        lands = lands[:-1]
    old_lands = OldLand.objects.all()
    old_lands_name = [old.name for old in old_lands]
    to_add = set(lands) - set(old_lands_name)
    to_dell = set(old_lands_name) - set(lands)
    for name in to_add:
        url = DOMAIN + name
        image = ImagePrev(url=url, name=name, host=host).get_image()
        old_dom = OldLand(name=name, url=url, image=image)
        old_dom.save()
    for name in to_dell:
        dom = OldLand.objects.get(name=name)
        dom.delete()
    old_lands = OldLand.objects.all()
    land_count = len(old_lands)
    info = f'Новых: {len(to_add)}, удалено: {len(to_dell)}'
    content = {
        'land_count': land_count,
        'domain': DOMAIN,
        'old_lands': old_lands,
        'info': info,
        'page_title': 'Архив',
    }
    return render(request, 'office/old_lands.html', content)


@login_required
def requisites(request):
    """Реквизиты и шаблоны html, css, js"""
    examples = CodeExample.objects.all()
    content = {
        'examples': examples,
        'page_title': 'Реквизиты',
    }
    return render(request, 'office/requisites.html', content)


@login_required
def checker(request, site_id, mode):
    """Проверочник сайтов"""
    site_model = Site.objects.get(pk=site_id)
    is_check_start = ''
    if not (mode == 0 and site_model.check_status != 'Не проверен'):
        # с главной страницы
        url = site_model.get_http_site()
        site_dir = site_model.site_name + '/public_html'
        site = SiteMap(url=url, is_cloac=site_model.is_cloac, dir_name=site_dir)
        checker = NewLinkChecker(site=site)
        checker.process()
        site_model.check_status = checker.result['result_text']
        new_check_data = {'main': checker.result,
                          'checkers': checker.results_from_checkers,}
        site_model.check_data = new_check_data
        site_model.save()
        is_check_start = 'Выполнена загрузка'
    content = {
        'site': site_model,
        'data': site_model.check_data,
        'is_check_start': is_check_start,
        'page_title': 'Проверка',
    }
    return render(request, 'office/checker.html', content)

@login_required
def domains(request):
    """Список доменов"""
    Beget().update_domains()
    domains_bd = RootDomain.objects.all().order_by('name')
    # domains_bd = [domain for domain in domains_bd if domain.is_root() is True]
    # for dom in domains_bd:
    #     print(dom.name, dom.is_root())
    # free_doms = Domain.objects.filter(site__isnull=True)
    content = {'domains': domains_bd,
               # 'free_doms': free_doms,
               'page_title': 'Домены',
               }
    return render(request, 'office/domains.html', content)


@login_required
def domain_change_status(request, dom_id, source, new_status):
    """Изменение статуса домена"""
    s = {
        'BAN': Domain.BAN,
        'USE': Domain.USE,
        'NEW': Domain.NEW,
    }
    new_status = s[new_status]
    domain = Domain.objects.get(pk=dom_id)
    if source == 'facebook':
        domain.facebook = new_status
    elif source == 'google':
        domain.google = new_status
    elif source == 'tiktok':
        domain.tiktok = new_status
    else:
        pass
    domain.save()
    return HttpResponseRedirect(reverse('office:domains'))

@login_required
def delete_site(request, site_id):
    site = Site.objects.get(pk=site_id)
    b = Beget()
    result = b.del_site(site.beget_id)
    if result:
        site.delete()
    return JsonResponse({'answer': result})


@login_required
@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def domains_list_api(request):
    if request.method == 'GET':
        domains = Domain.objects.all()
        domains = [domain for domain in domains if domain.is_root() is True]
        serializer = DomainSerializer(domains, many=True)
        return Response(serializer.data)


@login_required
@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def domains_detail(request, pk):
    try:
        domain = Domain.objects.get(pk=pk)
    except Domain.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DomainSerializer(domain)
        return Response(serializer.data, )
    elif request.method == 'POST':
        serializer = DomainSerializer(domain, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def company_list_api(request):
    companys = Company.objects.all()
    serializer = CompanySerializer(companys, many=True)
    return Response(serializer.data)


@login_required
@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def campaning_detail(request, pk):
    """ получения данных по РК или обновление"""
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CompanySerializer(company)
        return Response(serializer.data, )
    elif request.method == 'POST':
        print(request.data, )
        serializer = CompanySerializer(company)

        CompanySerializer().update(company, request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     print('good')
        return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def create_capmaning(request):
    """Создание новой кампании"""
    # TODO - при создании кампании сайт - не становиться запущеным!
    data = json.loads(request.POST['data'])
    name = data['text']
    pixel = data['pixel']
    daily = data['daily']
    cab = Cabinet.objects.get(pk=data['cab_id'])
    status = CampaignStatus.objects.get(pk=5)
    new_camp = Company(name=name, cab=cab, status=status, daily=daily, pixel=pixel)
    new_camp.save()
    for geo_id in data['geos_id']:
        country = Country.objects.get(pk=geo_id)
        new_camp.geo.add(country)
    for domain_id in data['domains_id']:
        domain = Domain.objects.get(pk=domain_id)
        new_camp.land.add(domain)
    new_camp.save()
    statusys = CampaignStatus.objects.all()
    content = {
        'comp': new_camp,
        'statusys': statusys,
    }
    # return Response(data, template_name='office/camp.html')
    # return render(request, 'office/camp.html', content)
    return render(request, 'office/camp.html', content)
    # return Response({'answer': 'success', 'result': template})



@login_required
def campanings(request):
    """ Текущие РК"""
    campamings = Company.objects.order_by('-published')
    statusys = CampaignStatus.objects.all()
    content = {
        'campanings': campamings,
        'statusys': statusys,
        'page_title': 'Кампании',
    }
    return render(request, 'office/campanings.html', content)


@login_required
@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def zapusk_data(request):
    """данные для создания нового запуска"""
    source = TrafficSource.objects.all()
    accounts = Account.objects.all()
    cabs = Cabinet.objects.all()
    domains = Domain.objects.filter(site__isnull=False)
    country = Country.objects.all()
    source_serializer = TrafficSourceSerializer(source,many=True)
    accounts_serializer = AccountSerializer(accounts, many=True)
    cabs_serializer = CabinetSerializer(cabs, many=True)
    domains_serializer = DomainSerializer(domains, many=True)
    country_serializer = CountrySerializer(country, many=True)

    return Response({
        'source': source_serializer.data,
        'accounts': accounts_serializer.data,
        'cabs': cabs_serializer.data,
        'domains': domains_serializer.data,
        'geos': country_serializer.data,
    })


def all_leads(request):
    leads = Lead.objects.all().order_by('-pk')
    content = {
        'leads': leads,
        'page_title': 'Лиды',
    }
    return render(request, 'office/leads.html', content)


def update_leads(request):
    leads = Lead.objects.filter(lead_id__isnull=False)
    lead_to_update_ids = []
    for lead in leads:
        if lead.get_lead_status() in [1,2]:
            lead_to_update_ids.append(lead.lead_id)
    lead_pp_data = TrirazatApi().get_lead_feedback(lead_to_update_ids)
    print(len(lead_pp_data), '*' * 30)
    for lead in lead_pp_data:
        try:
            lead_db = Lead.objects.get(lead_id=lead['id'])
            lead_db.pp_lead_status = lead
            lead_db.save()

        except Lead.DoesNotExist as error:
            print(error)
    return HttpResponseRedirect(reverse('office:leads'))


@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
@csrf_exempt
def add_lead(request):
    if request.method == 'POST':
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=404)
    else:
        return JsonResponse({"error": "error not POST"})
