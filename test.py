import supermarketscraper
import json
import time
import os.path
import datetime
import asyncio


async def main():
    # Test countdown scraper
    result = await supermarketscraper.countdown.getProductPrice("178085")
    print(result)

    # Test paknsave scraper
    result = await supermarketscraper.paknsave.getProductPrice("5090618_ea_000", "076e8177-943b-41fc-a885-ba3d28297acf")
    print(result)

    # Test newworld scraper
    result = await supermarketscraper.newworld.getProductPrice("5090618_ea_000", "c3a42e9d-ac58-4abf-be43-17920c720540")
    print(result)

    #Test freshchoice scraper
    result = await supermarketscraper.freshchoice.getProductPrice("v-green-energy-drink-330ml-6", "5e75a5ab60b75a3dea037da2")

    #Test warehouse scraper
    result = await supermarketscraper.thewarehouse.getProductPrice("R1907052")
    print(result)



loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
resultedd = loop.run_until_complete(main())