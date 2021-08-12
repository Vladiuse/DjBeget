# import os, sys
# sys.path.append('/home/v/vladiuse/.local/lib/python3.6/site-packages/requests')

import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .api import MyError, Beget
from .beget_api_keys import begget_login, begget_pass
from .help import ImagePrev, get_url_link_from_name
from .link_checker import Url, SuccessPage, LinkCheckerManager
from .models import Stream, Site, OldLand, Domain

DJANGO_SITE = 'https://main-prosale.store/'
NO_CONNECTION = 'Не удалось подключиться'


def get_domains_api():
    get_list_domains_url = f'https://api.beget.com/api/site/getList?login={begget_login}&passwd={begget_pass}&output_format=json'
    res = requests.get(get_list_domains_url)
    answer = res.json()
    domains = []
    for site in answer['answer']['result']:
        for domain in site['domains']:
            domain = domain['fqdn']
            domains.append(domain)
    return domains


def get_free_doms():
    get_list_domains_url = f'https://api.beget.com/api/site/getList?login={begget_login}&passwd={begget_pass}&output_format=json'
    res = requests.get(get_list_domains_url)
    answer = res.json()
    domains = []
    for site in answer['answer']['result']:
        dom_id = ''
        dom_name = ''
        for dom in site['domains']:
            dom_id += str(dom['id'])
            dom_name += dom['fqdn']
            domains.append(dom_name)

    get_doms = f'https://api.beget.com/api/domain/getList?login={begget_login}&passwd={begget_pass}&output_format=json'
    res = requests.get(get_doms)
    answer = res.json()
    doms = []
    for dom in answer['answer']['result']:
        doms.append(dom['fqdn'])

    free_doms = []
    for d in doms:
        if d not in domains:
            free_doms.append(d)

    return free_doms


def index(request):
    sites = Site.objects.all()
    site_count = len(sites)
    free_doms = get_free_doms()
    content = {'sites': sites,
               'site_count': site_count,
               'free_doms': free_doms,
               }
    return render(request, 'office/index.html', content)


def add_spend(request, summ):
    stream = Stream.objects.get(pk=1)
    stream.description = str(summ)
    stream.save()
    result_answer = 'Add Spend ' + str(summ)
    return HttpResponse('<h1>' + result_answer + '</h1>')


def update_domains(request):
    domains = set(get_domains_api())
    sites = set([site.site_name for site in Site.objects.all()])
    to_del = set(sites) - set(domains)
    to_add = set(domains) - set(sites)
    for site in to_del:
        s = Site.objects.get(site_name=site)
        s.delete()
    for site in to_add:
        url = get_url_link_from_name(site)
        s = Site(site_name=site, domain=url, title='None')
        s.save()
    return HttpResponseRedirect(reverse('office:index'))


def get_h1_title(url):
    try:
        res = requests.get(url)
    except:
        return NO_CONNECTION
    res.encoding = 'utf-8'
    IF_NO_BLOCK = '!!! Нет описания !!!'
    result = IF_NO_BLOCK
    for h_number in range(1, 4):
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.find_all(f'h{h_number}')
        if len(title) != 0:
            result = title[0].text.strip()
            break
    if len(result) > 40:
        result = result[:40] + '...'
    return result


def get_title(request):
    sites = Site.objects.all()
    for site in sites:
        h1_title = get_h1_title(site.domain)
        site.title = h1_title
        site.save()
    return HttpResponseRedirect(reverse('office:index'))


def old_lands(request):
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


def requisites(request):
    return render(request, 'office/requisites.html')


def checker(request, site_id):
    if site_id == 666:
        url = 'https://good-markpro.ru/'
    else:
        site = Site.objects.get(pk=site_id)
        url = site.domain
    link_manager = LinkCheckerManager(url=url)
    try:
        link_manager.process()
        result = link_manager.result
    except MyError as exc:
        result = exc
    content = {
               'content': result}
    return render(request, 'office/checker.html', content)


def domains(request):
    b = Beget()
    domains_list = b.get_domains_list()
    beget_doms_id = [dom['id'] for dom in domains_list]
    db_doms_id = [dom.beget_id for dom in Domain.objects.all()]
    to_del = set(db_doms_id) - set(beget_doms_id)
    to_add = set(beget_doms_id) - set(db_doms_id)
    for dom_id in to_del:
        dom = Domain.objects.get(beget_id=dom_id)
        dom.delete()
    for domain in domains_list:
        dom_id = domain['id']
        if dom_id in to_add:
            name = domain['fqdn']
            url = get_url_link_from_name(name)
            dom = Domain(name=name, url=url, beget_id=dom_id)
            dom.save()
    domains_bd = Domain.objects.all()
    content = {'domains': domains_bd}
    return render(request, 'office/domains.html', content)


def domain_change_status(request, dom_id, source, new_status):
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
