import requests
from bs4 import BeautifulSoup as bs
import re

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


def getProductPrice(productId, storeId):
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
    price = {'productData': {'name': scrapedData['productName'], 'productId': productId, 'productShopPage': baseurl,'productImageURL': scrapedData['productImageURL'], 'productDescription': scrapedData['productDescription']},  'bestPrice': scrapedData['salePrice'] ,'price': scrapedData['salePrice']}
    pricePerLitre = soup.find_all('span', {'class': 'MoreInfo__UnitPricing'})
    if (pricePerLitre and re.match(config['regex']['pricePerLitre'], pricePerLitre[0].text)):
        pricePerLitre = re.match(config['regex']['pricePerLitre'], pricePerLitre[0].text)[1]
        price['pricePerLitre'] = float(pricePerLitre)*10
        price['bestPricePerLitre'] = float(pricePerLitre)*10
    return price


""" # print(getProductPrice("5011153_ea_000pns?name=energy-drink-can", "3bb30799-82ce-4648-8c02-5113228963ed"))
#productsToCheck = ["5011153_ea_000"]
productsToCheck = [
    "mother-kicked-apple-500ml",
    "monster-ultra-red-500ml",
    "monster-energy-import-550ml",
    "monster-energy-drink-ultra-paradise-500ml",
    "monster-energy-ultra-sunrise-500ml",
    "monster-energy-ultra-zero-500ml",
    "monster-energy-green-500ml",
    "monster-energy-drink-ultra-rosa-500ml",
    "monster-energy-p-line-pnch-500ml",
    "monster-punch-500ml",
    "mother-energy-drink-berry-500ml",
    "mother-energy-drink-black-500ml",
    "mother-energy-drink-6x250ml-cans",
    "mother-energy-drink-passion-500ml",
    "mother-tropical-blast-500ml",
    "mother-can-energy-250ml",
    "mother-epic-swell-energy-drink-twisted-apple-500ml",
    "monster-energy-juice-mango-loco-500ml-can",
    "v-energy-drink-710ml-can",
    "v-energy-drink-guarana-500ml",
    "v-energy-drink-sugarfree-500ml",
    "v-energy-drink-sugar-free-guarana-250ml",
    "v-energy-drink-blue-200ml-10-pack",
    "v-blue-energy-drink-blue-guarana-spritzed-350ml",
    "v-energy-drink-green-guarana-350ml",
    "v-energy-drink-guarana-can-250ml",
    "v-energy-drink-guarana-can-500ml",
    "v-energy-drink-raspberry-lemonade-250ml-can",
    "v-energy-drink-raspberry-lemonade-350ml",
    "v-energy-drink-sugar-free-guarana-500ml",
    "v-energy-drink-skills-cans-275ml-4-pack",
    "v-guarana-energy-drink-fridge-pack-10x200ml",
    "v-blue-energy-drink-bottle-500ml",
    "v-blue-sugarfree-energy-drink-500ml",
    "v-energy-drink-raspberry-lemonade-500ml-can",
    "v-sugarfree-energy-drink-berry-twist-350ml",
    "v-blue-energy-drink-275ml-cans-4-pack",
    "v-blue-energy-drink-blue-guarana-can-250ml",
    "v-blue-energy-drink-blue-guarana-can-500ml",
    "v-iced-coffee-guarana-energy-500ml",
    "v-iced-mocha-guarana-energy-500ml",
    "v-energy-drink-sugar-free-guarana-275ml-4-pack",
    "v-energy-drink-sugar-free-guarana-bottle-350ml",
    "v-pure-energy-drink-250ml",
    "v-energy-drink-raspberry-lemonade-4-x-275ml-cans",
    "v-iced-chocolate-guarana-energy-500ml",
    "v-pure-330ml-bottle",
    "v-green-energy-drink-355ml-6-pack",
    "mother-energy-drink-original-500ml",
    "monster-energy-zero-ultra-4x500ml",
    "monster-energy-ultra-sunrise-500ml-can",
    "monster-super-fuel-zero-sugar-550ml",
    "monster-mule-ginger-brew-500ml",
    "mother-energy-can-250ml-6-pack",
    "monster-energy-4x500ml-cans",
    "monster-super-fuel-purple-passion-550ml",
    "monster-energy-pipeline-punch-500ml",
    "live-plus-persist-500ml",
    "live-plus-ignite-500ml",
    "v-blue-sugarfree-energy-drink-250ml",
    "live-plus-energy-drink-ignite-500ml",
    "live-plus-persist-glass-355ml",
    "live-plus-persist-250ml-6pack",
    "live-plus-energy-drink-persist-glass-355ml",
    "live-plus-live-ignite-energy-drink-6x250ml-cans",
    "rockstar-original-energy-drink-500ml",
    "rockstar-punched-energy-guava-500ml",
    "rockstar-punched-watermelon-freeze-energy-drink-500ml",
    "rockstar-energy-drink-xdurance-blueberry-can-500ml"
]


dataList = []
stores_stuff = getStores()

for a in productsToCheck:
    for x in stores_stuff:
        currentPrice = getProductPrice(a, x['id'])
        productData = currentPrice['productData']
        del currentPrice['productData']
        if (currentPrice['price'] != '0.00'):
            dataList.append({'productData': productData, 'priceData': currentPrice, 'store': x})
        print(currentPrice, x['name'])
if (os.path.isfile('./data/latest.json')):
    with open('./data/latest.json') as json_file:
        data = json.load(json_file)
        if (dataList == data):
            print("latest data saved is the same as the data just gathered. not going to write new file.")
        else:
            with open('./data/' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
                json.dump(dataList, f, ensure_ascii=False, indent=4)
            with open('./data/' + 'latest' + '.json', 'w', encoding='utf-8') as f:
                json.dump(dataList, f, ensure_ascii=False, indent=4)
else:
    with open('./data/' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
        json.dump(dataList, f, ensure_ascii=False, indent=4)
    with open('./data/' + 'latest' + '.json', 'w', encoding='utf-8') as f:
        json.dump(dataList, f, ensure_ascii=False, indent=4)

#I assume this url changes the store (200 response)
#tester = requests.get("https://store.freshchoice.co.nz/5c8f2abb777a4233c400918b/i_choose_you")
#print(tester.url) """