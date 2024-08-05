import requests
import urllib.parse
import json
import pandas as pd
from parsel import Selector
from price_parser import Price
import itertools
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv('token')

def get_price(price_raw):
    price_object = Price.fromstring(price_raw)
    return price_object.amount_float

def generate_url(search_text):
    return search_text.replace(' ', '+')

def remaining_request():
    url = f"https://api.Scrape.do/info?token={token}"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)

    if data['RemainingMonthlyRequest'] > 200:
        return True
    else:
        return False

def request_url(q,pagina):
    targetUrl = urllib.parse.quote(f"https://www.amazon.com.br/s?k={generate_url(q)}&page={pagina}")
    url = "http://api.scrape.do?token={}&url={}&geoCode=br".format(token, targetUrl)
    r = requests.request("GET", url)

    return r.text

def extract_data(html):

    selector = Selector(html)

    produtos = selector.css('div[data-component-type="s-search-result"]')

    l = []
    for i,produto in enumerate(produtos):

        try:
            price = get_price(produto.css('.a-price-whole::text').get()+','+produto.css('.a-price-fraction::text').get())
        except:
            price = '0'
        
        d = {
                'ECommerce':'Amazon',
                'Titulo': produto.css('.a-size-base-plus.a-color-base.a-text-normal::text').get(),
                'Preco': price,
                'asin': produto.attrib['data-asin'],
                'link': 'https://www.amazon.com.br/dp/'+produto.attrib['data-asin'],
                'Marca':'Amazon',
                'Quantidade':'--',
                'SellerName':'Amazon'
            }
        
        l.append(d)
        
    return l

def amazon(q,paginas):

    if remaining_request():
        results = []
        for pagina in range(1,paginas+1):
            data = request_url(q,pagina)    
            l = extract_data(data)

            results = list(itertools.chain(results, l))

        return pd.DataFrame(results)
    else:
        return pd.DataFrame()