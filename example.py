import supermarketscraper
import json
import time
import os.path

stores = {'freshchoice': supermarketscraper.freshchoice.getStores(), 'newworld': supermarketscraper.newworld.getStores(), 'paknsave': supermarketscraper.paknsave.getStores(), 'supervalue': supermarketscraper.supervalue.getStores()}

globalTotalTimeCodeStarted = time.time()

timeCodeStarted = time.time()
print(f"Time started: {timeCodeStarted}")
def getTimeSpentRunning():
    timeCodeEnded = time.time()
    timeSpentRunning = timeCodeEnded-timeCodeStarted
    timeCodeStarted = time.time()
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

def scrapePriceData(api, productsToCheck, stores_stuff=None):
  dataList = []
  friendlyStoreName = api.config['siteMeta']['name'].replace(" ", "").lower()
  # print(productsToCheck)
  if (stores_stuff):
      for x in stores_stuff:
        for a in productsToCheck:
          if ((x and ('id' in x))):  
            startTime = float(time.time())
            currentPrice = api.getProductPrice(a, x['id'])
            storeModified = {'id': x['id'], 'name': x['name']}
            productData = currentPrice['productData']
            del currentPrice['productData']
            if (currentPrice['price'] != '0.00'):
                dataList.append({'productData': productData, 'priceData': currentPrice, 'store': storeModified})
                endTime = float(time.time())
                timeTaken = "{:.2f}".format(endTime-startTime)
                print(f"Time taken: {timeTaken}", friendlyStoreName, currentPrice, x['name'], productData['name'])
            time.sleep(0.1)
  else:
      for a in productsToCheck:
            startTime = float(time.time())
            currentPrice = api.getProductPrice(a)
            productData = currentPrice['productData']
            del currentPrice['productData']
            if (currentPrice['price'] != '0.00'):
                dataList.append({'productData': productData, 'priceData': currentPrice})
                endTime = float(time.time())
                timeTaken = "{:.2f}".format(endTime-startTime)
                print(f"Time taken: {timeTaken}", friendlyStoreName, currentPrice, productData['name'])
            time.sleep(0.1)
  pathToWriteLatest = './data/' + friendlyStoreName + '/' + 'latest' + '.json'
  if (os.path.isfile(pathToWriteLatest)):
      with open(pathToWriteLatest) as json_file:
          data = json.load(json_file)
          if (dataList == data):
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


with open('./productsToCheck.json') as json_file:
          data_jsonfilething = json.load(json_file)
          # scrapePriceData(supermarketscraper.countdown, data['countdown'])
          # scrapePriceData(supermarketscraper.thewarehouse, data['thewarehouse'])
          with open('./storesToCheck.json') as stores_fi:
            stores_file = json.load(stores_fi)
            for sus in stores_file['paknsave']:
                print(sus['name'])
            scrapePriceData(supermarketscraper.thewarehouse, data_jsonfilething['thewarehouse'])
            print(f"The Warehouse ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            scrapePriceData(supermarketscraper.countdown, data_jsonfilething['countdown'])
            print(f"Countdown ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            scrapePriceData(supermarketscraper.freshchoice, data_jsonfilething['freshchoice'], stores['freshchoice'])
            print(f"Fresh Choice ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            scrapePriceData(supermarketscraper.supervalue, data_jsonfilething['freshchoice'], stores['supervalue'])
            print(f"SuperValue ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            scrapePriceData(supermarketscraper.paknsave, data_jsonfilething['paknsave'], stores_file['paknsave'])
            print(f"Paknsave ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")
            scrapePriceData(supermarketscraper.newworld, data_jsonfilething['paknsave'], stores['newworld'])
            print(f"New World ran for: {getTimeSpentRunning()} seconds ({getTimeSpentRunning()/60} minutes, {getTimeSpentRunning()/60/60} hours")

            scriptEndTimeTotal = time.time()
            print(f"This script in total ran for: {(scriptEndTimeTotal-globalTotalTimeCodeStarted)} seconds ({(scriptEndTimeTotal-globalTotalTimeCodeStarted)/60} minutes, {(scriptEndTimeTotal-globalTotalTimeCodeStarted)/60/60} hours")
            