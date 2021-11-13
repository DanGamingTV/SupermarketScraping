import requests
from bs4 import BeautifulSoup as bs
import re
import json
import asyncio

config = {'siteMeta': {'name': 'countdown', 'mainURL': 'shop.countdown.co.nz'}, 'regex': {
    'multiPack': "(\d{1,})pk", 'packageType': "(.{1,}ml) cans", 'volumeSize': "(.{1,}ml)", 'productNameVolume': ". (\d{1,}ml)"}}


async def getProductPrice(productId):
    baseurl = f"https://{config['siteMeta']['mainURL']}/api/v1/products/{productId}"
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "OnlineShopping.WebApp"
    }

    with requests.session() as s:
        r = s.get(baseurl, headers=header)
        try:
            data = json.loads(r.content)
        except json.decoder.JSONDecodeError:
            return {'error': {'message': 'Error decoding JSON'}}
        if ('Error' in data):
            return {'error': {'message': data['Message']}}
        price = {'productData': {'name': data['name'], 'productShopPage': f"https://{config['siteMeta']['mainURL']}/shop/productdetails?stockcode="+data['sku']},
                 'bestPrice': data['price']['salePrice'], 'price': data['price']['salePrice'], 'pricePerLitre': data['size']['cupPrice']*10, 'bestPricePerLitre': data['size']['cupPrice']*10}
        for x in data['productTags']:
            if("multibuy" in x['tagType'].lower()):
                price['multiBuy'] = {'quantity': x['multiBuy']['quantity'], 'value': x['multiBuy']
                                     ['value'], 'perUnit': x['multiBuy']['value']/x['multiBuy']['quantity']}
                price['bestPrice'] = x['multiBuy']['value'] / \
                    x['multiBuy']['quantity']
                price['bestPricePerLitre'] = price['bestPrice'] / \
                    (price['price'] / price['pricePerLitre'])
        if (data['size']['packageType'] != "single can"):
            matchMultipack = re.match(
                config['regex']['multiPack'], data['size']['volumeSize'])
            if(matchMultipack):
                price['productData']['multiPack'] = {
                    'quantity': list(matchMultipack.groups())[0]}
                matchPackageType = re.match(
                    config['regex']['packageType'], data['size']['packageType'])
                if (matchPackageType):
                    price['productData']['volume'] = list(
                        matchPackageType.groups())[0]
        matchVolumeSize = re.match(
            config['regex']['volumeSize'], data['size']['volumeSize'])
        if (matchVolumeSize != None):
            price['productData']['volume'] = list(matchVolumeSize.groups())[0]
        price['productData']['productId'] = data['sku']
        price['productData']['productDescription'] = data['description']
        productImageURL = data['images']
        if (len(productImageURL) > 0):
            productImageURL = productImageURL[0]['big']
        else:
            productImageURL = ''
        price['productData']['productImageURL'] = productImageURL
        matchVolumeFromProductName = re.findall(
            config['regex']['productNameVolume'], data['name'])
        if (len(matchVolumeFromProductName) > 0):
            price['productData']['volume'] = matchVolumeFromProductName[0]
        return price
