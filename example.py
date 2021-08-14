import supermarketscraper

stores = {'freshchoice': supermarketscraper.freshchoice.getStores(), 'newworld': supermarketscraper.newworld.getStores(), 'paknsave': supermarketscraper.paknsave.getStores(), 'supervalue': supermarketscraper.supervalue.getStores()}

print(supermarketscraper.countdown.getProductPrice('84822'))
print(supermarketscraper.freshchoice.getProductPrice('84822', stores['freshchoice'][0]['id']))
print(supermarketscraper.newworld.getProductPrice('84822', stores['newworld'][0]['id']))
print(supermarketscraper.paknsave.getProductPrice('84822', stores['paknsave'][0]['id']))
print(supermarketscraper.supervalue.getProductPrice('84822', stores['supervalue'][0]['id']))
print(supermarketscraper.thewarehouse.getProductPrice('84822'))