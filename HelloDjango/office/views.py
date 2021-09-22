import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .api import Beget
from .beget_api_keys import begget_login, begget_pass
from .help import ImagePrev
from .link_checker import LinkCheckerManager
from .models import Site, OldLand, Domain, CodeExample, Company, Account, Cabinet, CampaignStatus
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .serializers import DomainSerializer, CompanySerializer, AccountSerializer, CabinetSerializer

DJANGO_SITE = 'https://main-prosale.store/'
NO_CONNECTION = 'Не удалось подключиться'

# @login_required
# def get_domains_api():
#     # TODO удалить
#     get_list_domains_url = f'https://api.beget.com/api/site/getList?login={begget_login}&passwd={begget_pass}&output_format=json'
#     res = requests.get(get_list_domains_url)
#     answer = res.json()
#     domains = []
#     for site in answer['answer']['result']:
#         for domain in site['domains']:
#             domain = domain['fqdn']
#             domains.append(domain)
#     return domains

@login_required
def sites(request):
    """Список сайтов, их статусов и тд"""
    # sites = Site.objects.all().order_by('-pk')
    sites = list(Site.objects.exclude(site_name__in=Site.DONT_CHECK))  # исключаються тех сайты
    sites.sort(key=Site.get_sort_name)
    content = {'sites': sites,
               }
    return render(request, 'office/index.html', content)

@login_required
def update_sites(request):
    """Обновить список сайтов"""
    #TODO при изменение домена, если можель уже существует - домены не обновяться
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
            #добавление нового сайта
            beget_id = site_beget['id']
            site_name = site_beget['path']
            site = Site(beget_id=beget_id, site_name=site_name, title='None')
            site.save()
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
    # for site_beget_id_add in sites_to_add:
    #     for site_beget in sites_beget:
    #         if site_beget['id'] == site_beget_id_add:
    #             beget_id = site_beget['id']
    #             site_name = site_beget['path']
    #             s = Site(beget_id=beget_id, site_name=site_name)
    #             s.save()
    #             for domain in site_beget['domains']:
    #                 domain_beget_id = domain['id']
    #                 try:
    #                     domain = Domain.objects.get(beget_id=domain_beget_id)
    #                 except ObjectDoesNotExist:
    #                     b.update_domains()
    #                     domain = Domain.objects.get(beget_id=domain_beget_id)
    #                 s.domain_set.add(domain)
    #             s.save()
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
    }
    return render(request, 'office/old_lands.html', content)

@login_required
def requisites(request):
    """Реквизиты и шаблоны html, css, js"""
    examples = CodeExample.objects.all()
    content = {
        'examples': examples,
    }
    return render(request, 'office/requisites.html', content)

@login_required
def checker(request, site_id):
    """Проверочник сайтов"""
    if site_id == 666:
        url = 'https://good-markpro.ru/'
        site = Site.objects.get(domain=url)

    else:
        site = Site.objects.get(pk=site_id)
        url = site.get_http_site()
    # try:
    #     link_manager = LinkCheckerManager(url=url)
    #     link_manager.process()
    #     result = link_manager.result
    #     if result:
    #         site.check_status = Site.GREEN
    #         site.save()
    #     content = {
    #         'content': result}
    # except MyError as exc:
    #     content = {'exception':exc}
    link_manager = LinkCheckerManager(url=url)
    link_manager.process()
    result = link_manager.result
    site.set_status(link_manager.get_general_result())
    content = {'content': result, 'site': site}
    return render(request, 'office/checker.html', content)

@login_required
def domains(request):
    """Список доменов"""
    Beget().update_domains()
    domains_bd = Domain.objects.all().order_by('name')
    free_doms = Domain.objects.filter(site__isnull=True)
    content = {'domains': domains_bd,
               'free_doms': free_doms,
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

@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def domains_list_api(request):
    if request.method == 'GET':
        domains = Domain.objects.all()
        serializer = DomainSerializer(domains, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def domains_detail(request, pk):
    try:
        domain = Domain.objects.get(pk=pk)
    except Domain.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DomainSerializer(domain)
        return Response(serializer.data,)
    elif request.method == 'POST':
        serializer = DomainSerializer(domain, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def company_list_api(request):
    companys = Company.objects.all()
    serializer = CompanySerializer(companys, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def campaning_detail(request, pk):
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CompanySerializer(company)
        return Response(serializer.data,)
    elif request.method == 'POST':
        print(request.data,)
        serializer = CompanySerializer(company)

        CompanySerializer().update(company, request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     print('good')
        return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    pass


def campanings(request):
    campamings = Company.objects.all()
    statusys = CampaignStatus.objects.all()
    content = {'campanings': campamings, 'statusys': statusys}
    return render(request, 'office/campanings.html', content)