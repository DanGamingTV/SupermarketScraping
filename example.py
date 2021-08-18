import asyncio
import supermarketscraper
import json
import time
import os.path
import datetime

stores = {}

globalTotalTimeCodeStarted = time.time()

globalState = {}
globalState['timeCodeStarted'] = time.time()

print(f"Time started: {globalState['timeCodeStarted']}")
def getTimeSpentRunning():
    timeCodeEnded = time.time()
    timeSpentRunning = timeCodeEnded-globalState['timeCodeStarted']
    globalState['timeCodeStarted'] = time.time()
    return timeSpentRunning
# print(supermarketscraper.countdown.getProductPrice('THISSHOULDFAIL'))
# print(supermarketscraper.freshchoice.getProductPrice('THISSHOULDFAIL', stores['freshchoice'][0]['id']))
# print(supermarketscraper.newworld.getProductPrice('THISSHOULDFAIL', stores['newworld'][0]['id']))
# print(supermarketscraper.paknsave.getProductPrice('THISSHOULDFAIL', stores['paknsave'][0]['id']))
# print(supermarketscraper.supervalue.getProductPrice('THISSHOULDFAIL', stores['supervalue'][0]['id']))
# print(supermarketscraper.thewarehouse.getProductPrice('THISSHOULDFAIL'))

# print(supermarketscraper.paknsave.getProductPrice("5007441_ea_000", "076e8177-943b-41fc-a885-ba3d28297acf"))
# print(supermarketscraper.paknsave.getProductPrice("5003156_ea_000", "076e8177-943b-41fc-a885-ba3d28297acf"))
# print(supermarketscraper.paknsave.getProductPrice("5020662_ea_000", "076e8177-943b-41fc-a885-ba3d28297acf"))

async def scrapePriceData(api, productsToCheck, delay, stores_stuff=None):
  dataList = []
  pre_list = []
  friendlyStoreName = api.config['siteMeta']['name'].replace(" ", "").lower()
  # print(productsToCheck)
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
      for x in stores_stuff:
        for a in productsToCheck:
          if ((x and ('id' in x))):  
            startTime = float(time.time())
            task = asyncio.create_task(api.getProductPrice(a, x['id']))
            await asyncio.sleep(delay)
            pre_list.append({'p': await task, 's': x})
            # currentPrice = await task
            # storeModified = {'id': x['id'], 'name': x['name']}
            # productData = currentPrice['productData']
            # del currentPrice['productData']
            # if (currentPrice['price'] != '0.00'):
            #     dataList.append({'productData': productData, 'priceData': currentPrice, 'store': storeModified})
            #     endTime = float(time.time())
            #     timeTaken = "{:.2f}".format(endTime-startTime)
            #     print(f"Time taken: {timeTaken}", friendlyStoreName, currentPrice, x['name'], productData['name'])
  else:
      for a in productsToCheck:
            startTime = float(time.time())
            task = asyncio.create_task(api.getProductPrice(a))
            await asyncio.sleep(delay)
            pre_list.append({'p': await task})
            # currentPrice = await task
            # productData = currentPrice['productData']
            # del currentPrice['productData']
            # if (currentPrice['price'] != '0.00'):
            #     dataList.append({'productData': productData, 'priceData': currentPrice})
            #     endTime = float(time.time())
            #     timeTaken = "{:.2f}".format(endTime-startTime)
            #     print(f"Time taken: {timeTaken}", friendlyStoreName, currentPrice, productData['name'])
  
  for i in range(len(pre_list)):
      currentPrice = pre_list[i]
      productData = currentPrice['p']['productData']
      newPriceData = currentPrice['p']
      del newPriceData['productData']
      if (currentPrice['p']['price'] != '0.00'):
        if ('s' in currentPrice):
            currentStore = currentPrice['s']
            storeModified = {'id': currentStore['id'], 'name': currentStore['name']}
            dataList.append({'productData': productData, 'priceData': newPriceData, 'store': storeModified})
            print(friendlyStoreName, newPriceData, storeModified['name'], productData['name'])
        else:
            dataList.append({'productData': productData, 'priceData': newPriceData})
            print(friendlyStoreName, newPriceData, productData['name'])




  pathToWriteLatest = './data/' + friendlyStoreName + '/' + 'latest' + '.json'
  if (os.path.isfile(pathToWriteLatest)):
      with open(pathToWriteLatest) as json_file:
          data = json.load(json_file)
          if (dataList[1:] == data[1:]):
              print("latest data saved is the same as the data just gathered. not going to write new file.")
          else:
              with open('./data/' + friendlyStoreName + '/' + str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
                  json.dump(dataList, f, ensure_ascii=False, indent=4)
              with open(pathToWriteLatest, 'w', encoding='utf-8') as f:
                  json.dump(dataList, f, ensure_ascii=False, indent=4)
  else:
      with open('./data/' + friendlyStoreName + '/' +  str(int(time.time())) + '.json', 'w', encoding='utf-8') as f:
          json.dump(dataList, f, ensure_ascii=False, indent=4)
      with open('./data/' + friendlyStoreName + '/' + 'latest' + '.json', 'w', encoding='utf-8') as f:
          json.dump(dataList, f, ensure_ascii=False, indent=4)

async def main():
    stores.update({'freshchoice': await supermarketscraper.freshchoice.getStores(), 'newworld': await supermarketscraper.newworld.getStores(), 'paknsave': await supermarketscraper.paknsave.getStores(), 'supervalue': await supermarketscraper.supervalue.getStores()})
    with open('./productsToCheck.json') as json_file:
              data_jsonfilething = json.load(json_file)
              # scrapePriceData(supermarketscraper.countdown, data['countdown'])
              # scrapePriceData(supermarketscraper.thewarehouse, data['thewarehouse'])
              with open('./storesToCheck.json') as stores_fi:
                stores_file = json.load(stores_fi)
                for sus in stores_file['paknsave']:
                    print(sus['name'])
                #await scrapePriceData(supermarketscraper.thewarehouse, data_jsonfilething['thewarehouse'], 0)
                #print(f"The Warehouse ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes,   {getTimeSpentRunning()/60/60} hours")
                #await scrapePriceData(supermarketscraper.mightyape, data_jsonfilething['mightyape'], 0)
                #print(f"Mighty Ape ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes,  {getTimeSpentRunning()/60/60} hours")
                await scrapePriceData(supermarketscraper.countdown, data_jsonfilething['countdown'], 2)
                print(f"Countdown ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes,   {getTimeSpentRunning()/60/60} hours")
                # await scrapePriceData(supermarketscraper.paknsave, data_jsonfilething['paknsave'], stores_file['paknsave'], 2)
                # print(f"Paknsave ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes,  {getTimeSpentRunning()/60/60} hours")
                # scrapePriceData(supermarketscraper.freshchoice, data_jsonfilething['freshchoice'], stores['freshchoice'], 1)
                # print(f"Fresh Choice ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes,    {getTimeSpentRunning()/60/60} hours")
                # scrapePriceData(supermarketscraper.supervalue, data_jsonfilething['freshchoice'], stores['supervalue'], 1)
                # print(f"SuperValue ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes,  {getTimeSpentRunning()/60/60} hours")
                # scrapePriceData(supermarketscraper.newworld, data_jsonfilething['paknsave'], stores['newworld'], 2)
                # print(f"New World ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes,   {getTimeSpentRunning()/60/60} hours")

                scriptEndTimeTotal = time.time()
                print(f"This script in total ran for: {(scriptEndTimeTotal-globalTotalTimeCodeStarted)} seconds ({  (scriptEndTimeTotal-globalTotalTimeCodeStarted)/60} minutes, {    (scriptEndTimeTotal-globalTotalTimeCodeStarted)/60/60} hours")
            
asyncio.run(main())