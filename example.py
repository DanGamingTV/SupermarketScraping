import supermarketscraper
import json
import time
import os.path
import datetime
import asyncio

stores = {'freshchoice': supermarketscraper.freshchoice.getStores(), 'newworld': supermarketscraper.newworld.getStores(
), 'paknsave': supermarketscraper.paknsave.getStores(), 'supervalue': supermarketscraper.supervalue.getStores()}

globalTotalTimeCodeStarted = time.time()

globalState = {}
globalState['timeCodeStarted'] = time.time()

print(f"Time started: {globalState['timeCodeStarted']}")


def getTimeSpentRunning():
    timeCodeEnded = time.time()
    timeSpentRunning = timeCodeEnded-globalState['timeCodeStarted']
    globalState['timeCodeStarted'] = time.time()
    return timeSpentRunning


async def scrapePriceData(api, productsToCheck, stores_stuff=None):
    dataList = []
    friendlyStoreName = api.config['siteMeta']['name'].replace(" ", "").lower()
    dataList.append({
        "productData": {
            "name": "FILEMETA",
            "productId": "FILEMETA",
            "productShopPage": "",
            "productImageURL": "",
            "productDescription": "THIS IS NOT A REAL PRODUCT, THIS IS METADATA OF THIS FILE"
        },
        "priceData": {
            "bestPrice": "0.00",
            "price": "0.00",
            "pricePerLitre": 0,
            "bestPricePerLitre": 0
        },
        "timestamp": datetime.datetime.now().isoformat(),
        "siteconfig": api.config
    })
    if (stores_stuff):
        async def per_store1(x_store):
            async def per_product1(a_product):
                startTime = float(time.time())
                currentPrice = await api.getProductPrice(a_product, x_store['id'])
                storeModified = {'id': x_store['id'], 'name': x_store['name']}
                productData = currentPrice['productData']
                del currentPrice['productData']
                if (currentPrice['price'] != '0.00'):
                    dataList.append(
                        {'productData': productData, 'priceData': currentPrice, 'store': storeModified})
                    endTime = float(time.time())
                    timeTaken = "{:.2f}".format(endTime-startTime)
                    print(f"Time taken: {timeTaken}", friendlyStoreName,
                          currentPrice, x_store['name'], productData['name'])
            coros_per_product1 = [per_product1(a) for a in productsToCheck]
            await asyncio.gather(*coros_per_product1)
        coros_per_store1 = [per_store1(x) for x in stores_stuff]
        await asyncio.gather(*coros_per_store1)
    else:
        async def per_product2(a_product):
            startTime = float(time.time())
            currentPrice = await api.getProductPrice(a_product)
            productData = currentPrice['productData']
            del currentPrice['productData']
            if (currentPrice['price'] != '0.00'):
                dataList.append({'productData': productData,
                                'priceData': currentPrice})
                endTime = float(time.time())
                timeTaken = "{:.2f}".format(endTime-startTime)
                print(f"Time taken: {timeTaken}", friendlyStoreName,
                      currentPrice, productData['name'])
        coros_per_product2 = [per_product2(a) for a in productsToCheck]
        await asyncio.gather(*coros_per_product2)
    print('hey hey hey')
    pathToWriteLatest = './data/' + friendlyStoreName + '/' + 'latest' + '.json'
    if (os.path.isfile(pathToWriteLatest)):
        with open(pathToWriteLatest) as json_file:
            data = json.load(json_file)
            if (dataList == data):
                print(
                    "latest data saved is the same as the data just gathered. not going to write new file.")
            else:
                with open('./data/' + friendlyStoreName + '/archive/' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
                    print(f"begin write file for {friendlyStoreName}")
                    json.dump(dataList, f, ensure_ascii=False, indent=4)
                with open(pathToWriteLatest, 'w', encoding='utf-8') as f:
                    print(f"begin write file for {friendlyStoreName}")
                    json.dump(dataList, f, ensure_ascii=False, indent=4)
    else:
        with open('./data/' + friendlyStoreName + '/archive/' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
            print(f"begin write file for {friendlyStoreName}")
            json.dump(dataList, f, ensure_ascii=False, indent=4)
        with open('./data/' + friendlyStoreName + '/' + 'latest' + '.json', 'w', encoding='utf-8') as f:
            print(f"begin write file for {friendlyStoreName}")
            json.dump(dataList, f, ensure_ascii=False, indent=4)


async def main():
    with open('./productsToCheck.json') as json_file:
        data_jsonfilething = json.load(json_file)
        with open('./storesToCheck.json') as stores_fi:
            stores_file = json.load(stores_fi)
            await scrapePriceData(supermarketscraper.thewarehouse, data_jsonfilething['thewarehouse'])
            print(
                f"The Warehouse ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            await scrapePriceData(supermarketscraper.mightyape, data_jsonfilething['mightyape'])
            print(
                f"Mighty Ape ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            # await scrapePriceData(supermarketscraper.countdown, data_jsonfilething['countdown'])
            # print(f"Countdown ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            await scrapePriceData(supermarketscraper.paknsave, data_jsonfilething['paknsave'], stores_file['paknsave'])
            print(
                f"Paknsave ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            await scrapePriceData(supermarketscraper.freshchoice, data_jsonfilething['freshchoice'], stores['freshchoice'])
            print(
                f"Fresh Choice ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            await scrapePriceData(supermarketscraper.supervalue, data_jsonfilething['freshchoice'], stores['supervalue'])
            print(
                f"SuperValue ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            # scrapePriceData(supermarketscraper.newworld, data_jsonfilething['paknsave'], stores['newworld'])
            # print(f"New World ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")

            scriptEndTimeTotal = time.time()
            print(
                f"This script in total ran for: {(scriptEndTimeTotal-globalTotalTimeCodeStarted)} seconds ({(scriptEndTimeTotal-globalTotalTimeCodeStarted)/60} minutes, {(scriptEndTimeTotal-globalTotalTimeCodeStarted)/60/60} hours")
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
