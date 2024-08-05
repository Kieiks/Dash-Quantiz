import requests
import json
import pandas as pd
import itertools


# Function to get JSON data from the API
def get_json(q, pagina=1):
    API_URL = 'https://api.mercadolibre.com/sites/MLB/search'
    ITEMS_PER_PAGE = 50
    offset = pagina * ITEMS_PER_PAGE - ITEMS_PER_PAGE
    params = {'q': q, 'offset': offset}
    r = requests.get(API_URL, params=params)
    return json.loads(r.text)

# Function to extract attributes from the data
def get_attributes(data):
    lista = []
    for d in data['results']:
        produto = {
            'ECommerce': 'Mercado Livre',
            'ProductID': d['id'],
            'Titulo': d['title'],
            'Preco': d['price'],
            'link': d['permalink'],
            'Quantidade': d['available_quantity'],
            'Condicao': d['condition'],
            'Imagem': d['thumbnail'],
            'Listagem': d['listing_type_id'],
            'SellerID': d['seller']['id'],
            'SellerName': d['seller']['nickname']
        }
        for i in d['attributes']:
            produto[i["name"]] = i['value_name']
        lista.append(produto)
    return pd.DataFrame(lista)

# Function to aggregate data from multiple pages
def mercadolivre(q, paginas):
    df_final = pd.DataFrame()
    for i in range(1, paginas + 1):
        data = get_json(q, i)
        df = get_attributes(data)
        df_final = pd.concat([df_final, df], axis=0)
    return df_final