import requests
import json
import pandas as pd
import itertools
from parsel import Selector
from price_parser import Price
import urllib.parse
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("token")


def remaining_request():
    url = f"https://api.Scrape.do/info?token={token}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)

    if data["RemainingMonthlyRequest"] > 200:
        return True
    else:
        return False


def generate_url(search_text):
    return search_text.replace(" ", "+")


def get_price(price_raw):
    price_object = Price.fromstring(price_raw)
    return price_object.amount_float


def request_url(q, pagina):
    targetUrl = urllib.parse.quote(
        f"https://www.magazineluiza.com.br/busca/{generate_url(q)}/?from=submit&page={pagina}"
    )
    url = "http://api.scrape.do?token={}&url={}&geoCode=br".format(token, targetUrl)
    r = requests.request("GET", url)

    return r.text


# def make_request(q,pagina):

#     headers = {
#             "accept": "*/*",
#             "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es-CL;q=0.5,es;q=0.4",
#             "priority": "u=1, i",
#             "referer": "https://www.magazineluiza.com.br/",
#             "sec-ch-ua-mobile": "?0",
#             "sec-fetch-dest": "empty",
#             "sec-fetch-mode": "cors",
#             "sec-fetch-site": "same-origin",
#             "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
#             "x-nextjs-data": "1"
#         }

#     url = f'https://www.magazineluiza.com.br/busca/{generate_url(q)}/?from=submit&page={pagina}'

#     r = requests.get(url,headers=headers)
#     return r.text


def extract_data(data):
    selector = Selector(data)

    data = json.loads(selector.css("#__NEXT_DATA__::text").get())
    l = []
    for produto in data["props"]["pageProps"]["data"]["search"]["products"]:
        d = {
            "ECommerce": "Magazine Luiza",
            "Titulo": produto["title"],
            "Preco": get_price(produto["price"]["bestPrice"]),
            "Marca": produto["brand"]["label"],
            "Quantidade": produto["available"],
            "SellerName": produto["seller"]["description"],
            "link": f"https://www.magazineluiza.com.br/{produto['path']}",
        }

        l.append(d)
    return l


def magalu(q, paginas):

    if remaining_request():
        results = []
        for pagina in range(1, paginas + 1):
            data = request_url(q, pagina)
            # data = make_request(q,pagina)

            l = extract_data(data)
            results = list(itertools.chain(results, l))
        return pd.DataFrame(results)
    else:
        return pd.DataFrame()
