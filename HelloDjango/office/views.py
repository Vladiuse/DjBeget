from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Stream, Site
# import os, sys
# sys.path.append('/home/v/vladiuse/.local/lib/python3.6/site-packages/requests')
import requests
from bs4 import BeautifulSoup
DJANGO_SITE = 'https://main-prosale.store/'
NO_CONNECTION_INFP = 'Не удалось подключиться'

def get_url_link(domain_name):
    protokol = 'https'
    if 'beget' in domain_name:
        protokol = 'http'
    return protokol + '://' + domain_name + '/'

def get_domains_api():
    get_list_domains_url = 'https://api.beget.com/api/site/getList?login=vladiuse&passwd=20302030Ab%&output_format=json'
    res = requests.get(get_list_domains_url)
    answer = res.json()
    domains = []
    for site in answer['answer']['result']:
        for domain in site['domains']:
            domain = domain['fqdn']
            domains.append(domain)
    return domains


def get_free_doms():
    get_list_domains_url = 'https://api.beget.com/api/site/getList?login=vladiuse&passwd=20302030Ab%&output_format=json'
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

    get_doms = 'https://api.beget.com/api/domain/getList?login=vladiuse&passwd=20302030Ab%&output_format=json'
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
    return HttpResponse('<h1>'+ result_answer + '</h1>')
    
    
def update_domains(request):
    domains = set(get_domains_api())
    sites = set([site.site_name for site in Site.objects.all()])
    to_del = set(sites) - set(domains)
    to_add = set(domains) - set(sites)
    for site in to_del:
        s = Site.objects.get(site_name=site)
        s.delete()
    for site in to_add:
        url = get_url_link(site)
        s = Site(site_name=site, domain=url, title='None')
        s.save()
    return HttpResponseRedirect(reverse('office:index'))


def get_h1_title(url):
    try:
        res = requests.get(url)
    except:
        return NO_CONNECTION_INFP
    res.encoding = 'utf-8'
    IF_NO_BLOCK = '!!! Нет описания !!!'
    result = IF_NO_BLOCK
    for h_number in range(1, 4):
        soup = BeautifulSoup(res.text, 'lxml')
        title = soup.find_all(f'h{h_number}')
        if len(title) != 0:
            result = title[0].text.strip()
            break
    if len(result) > 50:
        result = result[:50] + '...'
    return result

def get_title(request):
    sites = Site.objects.all()
    for site in sites:
        h1_title = get_h1_title(site.domain)
        site.title = h1_title
        site.save()
    return HttpResponseRedirect(reverse('office:index'))

        
    
    
    
    
    
    
