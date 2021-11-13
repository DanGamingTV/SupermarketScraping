import requests
from bs4 import BeautifulSoup as bs
import re
import asyncio

config = {'siteMeta': {'name': 'Super Value', 'mainURL': 'supervalue.co.nz', 'productPrefix': ''}, 'regex': {'pricePerLitre': "\(\$(\d{1,}.\d{1,}) (?:per ){0,}100[M-m][L-l]\)"}, 'endpoints': {}}
config.update({'endpoints': {'storeList': f"https://store.{config['siteMeta']['mainURL']}/api/v1/stores"}})

def getStoreIDs():
    storeIDs = []
    r = requests.get(config['endpoints']['storeList'])
    soup = bs(r.content,'html.parser')
    storeLinks = soup.find_all('a', {'class': "StoreLink StoreLink--Default"})
    for store in storeLinks:
        currentStoreId = list(re.match("\/(.{1,})\/i_choose_you", store['href']).groups())[0]
        if (currentStoreId not in storeIDs):
            storeIDs.append(currentStoreId)
    return storeIDs

def getStores():
    stores_list = []
    storeIDsIterated = []
    r = requests.get(config['endpoints']['storeList'])
    soup = bs(r.content,'html.parser')
    storeLinks = soup.find_all('a', {'class': "StoreLink StoreLink--Default"})
    for store in storeLinks:
        currentStoreId = list(re.match("\/(.{1,})\/i_choose_you", store['href']).groups())[0]
        currentStoreName = store.find('span', {'class': 'StoreLink__Name'}).text
        currentStoreDetails = store.find('span', {'class': 'StoreLink__Details'}).text.strip()
        if (currentStoreId not in storeIDsIterated):
            stores_list.append({'id': currentStoreId, 'name': currentStoreName, 'details': currentStoreDetails})
        storeIDsIterated.append(currentStoreId)
    return stores_list


async def getProductPrice(productId, storeId):
    url = f"https://store.{config['siteMeta']['mainURL']}/{storeId}/i_choose_you"
    baseurl = requests.get(url).url
    baseurl = f"{baseurl}lines/{productId}"
    r = requests.get(baseurl)
    soup = bs(r.content,'html.parser')

    scrapedData = {}

    scrapedData['salePrice'] = soup.find('strong', {'class': 'MoreInfo__Price'})
    scrapedData['salePrice'] = scrapedData['salePrice'].text.strip().replace('$', '') if scrapedData['salePrice'] else '0.00'
    scrapedData['productName'] = soup.find_all('div', {'class': "MoreInfo__Banner__Name"})
    scrapedData['productName'] = scrapedData['productName'][0].text.strip() if scrapedData['productName'] else ''
    scrapedData['productImageURL'] = soup.find_all('img', {'class': 'product_image'})
    scrapedData['productImageURL'] = str(scrapedData['productImageURL'][0]['src']) if scrapedData['productImageURL'] else ''
    scrapedData['productDescription'] = soup.find_all('div', {'class': "MoreInfo__Details"})
    scrapedData['productDescription'] = scrapedData['productDescription'][0].text.strip() if scrapedData['productDescription'] else ''
    volume_detect = re.match("(.{1,})(\d{3,}ml)", scrapedData['productName'])
    price = {'productData': {'name': scrapedData['productName'], 'productId': productId, 'productShopPage': baseurl,'productImageURL': scrapedData['productImageURL'], 'productDescription': scrapedData['productDescription']},  'bestPrice': scrapedData['salePrice'] ,'price': scrapedData['salePrice']}
    pricePerLitre = soup.find_all('span', {'class': 'MoreInfo__UnitPricing'})
    if (pricePerLitre and re.match(config['regex']['pricePerLitre'], pricePerLitre[0].text)):
        pricePerLitre = re.match(config['regex']['pricePerLitre'], pricePerLitre[0].text)[1]
        price['pricePerLitre'] = float(pricePerLitre)*10
        price['bestPricePerLitre'] = float(pricePerLitre)*10
    if (volume_detect):
        price['productData']['volume'] = volume_detect.groups()[1]
    if ('volume' in price['productData']):
        mutatedVolume = float(price['productData']['volume'].replace('ml', ''))
        actualVolume = float(mutatedVolume)
        if ('multipack' in price['productData']):
            actualVolume = mutatedVolume*int(price['productData']['multipack']['quantity'])
        calculatedPricePerLitre = float(price['price'])*(1000/actualVolume)
        calculatedBestPricePerLitre = float(price['bestPrice'])*(1000/actualVolume)
        price['pricePerLitre'] = calculatedPricePerLitre
        price['bestPricePerLitre'] = calculatedBestPricePerLitre
    return price