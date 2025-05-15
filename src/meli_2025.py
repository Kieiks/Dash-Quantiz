from curl_cffi import requests
from parsel import Selector
import json
import pandas as pd


def extract_info(data, info_required):

    if info_required == 'price':
        for j in data['polycard']['components']:
            if info_required in j:
                return j[info_required]['current_price']['value']


    for j in data['polycard']['components']:
        if info_required in j:
            return j[info_required]['text']

def extract_product_info(data):
    produtos = []
    for i in data['pageStoreState']['search']['results']:
        if i['id'] == 'POLYCARD':
            produto = {
                    "ECommerce": "Mercado Livre",
                    "ProductID": i['polycard']['metadata'].get('product_id', i['polycard']['metadata']['id']),
                    "Titulo": extract_info(i, 'title'),
                    "Preco": extract_info(i, 'price'),
                    'Marca': extract_info(i, 'brand'),
                    "link": i['polycard']['metadata'].get('url') + i['polycard']['metadata'].get('url_params', ''),
                    "SellerName": (extract_info(i, 'seller') or '').replace(' {icon_cockade}', '').replace('Por ',''),
                }
            produtos.append(produto)
    return produtos

def get_data(url):
    r = requests.get(url, impersonate='chrome120')
    selector = Selector(r.text)
    data = selector.css('#__PRELOADED_STATE__::text').get()
    return json.loads(data)

def mercadolivre(q, paginas):
    resultados = []
    q = '-'.join(q.split())

    url = f'https://lista.mercadolivre.com.br/{q}'

    data = get_data(url)

    produtos = extract_product_info(data)
    resultados.extend(produtos)

    if paginas == 2:

        new_url = data['pageStoreState']['search']['pagination']['next_page']['url']
        data = get_data(new_url)
        produtos = extract_product_info(data)
        resultados.extend(produtos)
    
    return pd.DataFrame(resultados)

# print(mercadolivre('pampers xg', 2))