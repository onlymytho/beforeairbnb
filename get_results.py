# -*- coding: utf-8 -*-

# from botocore.vendored import requests
import sys
sys.path.insert(0, "/lib/site-packages")

import requests
import json
import time
import math
from threading import Thread
from collections import Counter

my_user_api_key = 'd306zoyjsyarp7ifhu67rjxn52tv0t20'
end_point_url = 'https://api.airbnb.com/v2/search_results'


locale='ko'
currency='USD'
_format='for_search_results_with_minimal_pricing'
limit='50'
_offset='0'
guests='2'
ib='false'
min_bathrooms='0'
min_bedrooms='0'
min_beds='1'
min_num_pic_urls='5'
# price_max=10
# price_min=0
sort='1'
user_lat='37.560512'
user_lng='126.908462'
# price_step=4

incremental_search = {'price_min': [1,5,10,15,20,25,30,35,40,45,50,100,200,350,500],
                          'price_max': [5,10,15,20,25,30,35,40,45,50,100,200,350,500,1000],
                          'price_step':[1,1,1,1,1,1,1,1,1,1,10,20,30,30,100]
                          }
location = 'Yeonnamro-3'

listings = []
threads = []
ids = []
result = {'room_type':{}, 'price':{}, 'super_host':{}, 'business_travel':{}, 'family_preferred':{}, 'extra_host_language':{}}

def getresults(event, context):

    global result

    def getneighbors():

        print ('Neighbors calling is started.')

        for n in range(len(incremental_search['price_min'])):
            def getlistingthread():
                global listings
                global threads
                global ids
                neighbors = []
                price_min=incremental_search['price_min'][n]
                price_max=incremental_search['price_max'][n]
                price_step=incremental_search['price_step'][n]

                for price in range(price_min, price_max, price_step):
                    r = requests.get(end_point_url +
                                     '?client_id='+my_user_api_key+
                                     '&locale='+str(locale)+
                                     '&currency='+str(currency)+
                                     '&_format='+str(_format)+
                                     '&_limit='+str(limit)+
                                     '&_offset='+str(_offset)+
                                     '&guests='+str(guests)+
                                     '&ib='+str(ib)+
                                     '&location='+str(event['location'])+
                                     '&min_bathrooms='+str(min_bathrooms)+
                                     '&min_bedrooms='+str(min_bathrooms)+
                                     '&min_beds='+str(min_beds)+
                                     '&min_num_pic_urls='+str(min_num_pic_urls)+
                                     '&price_max='+str(price+price_step)+
                                     '&price_min='+str(price)+
                                     '&sort='+str(sort)+
                                     '&user_lat='+str(user_lat)+
                                     '&user_lng='+str(user_lng)
                                     )

                    datadict = r.json()
                    datajson = json.dumps(datadict, indent=4)
                    listing_result = datadict['search_results']

                    for l in listing_result:
                        id = l['listing'].get('id')
                        if id in ids:
                            pass
                        else:
                            ids.append(id)
                            neighbors.append(l)

                listings = listings + neighbors

            threads.append(Thread(target=getlistingthread))
            threads[n].daemon = True
            threads[n].start()
            time.sleep(0.5)

        for n in range(len(incremental_search['price_min'])):
            threads[n].join()

    def analyze_roomtype():
        # This way is just not to seperate get and analyze functions.
        # You can seperate it by letting apis communicate each other.
        # Hard point is to get data from B function although request is sent to A function.

        global listings
        global result

        print ('Room_type Analysis is started.')


        # Initiate room_type related fileds.
        print ('Initiate room_type related fileds.')
        room_type = {'entire_home':[], 'private_room':[], 'else':[]}
        prices = {'entire_home':[], 'private_room':[], 'else':[]}

        # Distribute listings to its room_type field.
        print ('Distribute listings to its room_type field.')
        for l in listings:
            rtc = l['listing'].get('room_type_category')
            for rt in room_type:
                if rtc == rt:
                    room_type[rt].append(l)
                else:
                    pass

        # Get prices data from each room_type distributed room
        print ('Get prices data from each room_type distributed room')
        for rt in room_type:
            for l in room_type[rt]:
                prices[rt].append(int(l['pricing_quote']['rate'].get('amount_formatted')[1:]))


        # Initiate room_type field to results.
        print ('Initiate room_type field to results.')
        print (result)
        for rt in room_type:
            result['room_type'][rt] = {'price':{}}


        def median(lst):
            sortedLst = sorted(lst)
            lstLen = len(lst)
            index = (lstLen - 1) // 2

            if (lstLen % 2):
                return sortedLst[index]
            else:
                return (sortedLst[index] + sortedLst[index + 1])/2.0

        # Insert analyzed rt room_type data to results.
        print ("Insert analyzed rt room_type data to results.")
        for rt in room_type:

            sum = 0
            for item in prices[rt]:
                sum = sum+float(item)

            if len(prices[rt]) != 0:
                result['room_type'][rt]['price']['len'] = len(prices[rt])
                result['room_type'][rt]['price']['sum'] = sum
                result['room_type'][rt]['price']['avg'] = float(sum/len(prices[rt]))
                result['room_type'][rt]['price']['med'] = median(prices[rt])
                result['room_type'][rt]['price']['std'] = math.sqrt(median(prices[rt]))
                result['room_type'][rt]['price']['min'] = min(prices[rt])
                result['room_type'][rt]['price']['max'] = max(prices[rt])
            else:
                result['room_type'][rt]['len'] = 0
                result['room_type'][rt]['price']['sum'] = 0
                result['room_type'][rt]['price']['avg'] = 0
                result['room_type'][rt]['price']['med'] = 0
                result['room_type'][rt]['price']['std'] = 0
                result['room_type'][rt]['price']['min'] = 0
                result['room_type'][rt]['price']['max'] = 0

        # room_type analysis is done
        print ('room_type analysis is done')

    def analyze_price():
        global listings
        global result

        print ('Price Analysis is started.')

        prices = []
        for l in listings:
            prices.append(int(l['pricing_quote']['rate'].get('amount_formatted')[1:]))

        sum = 0
        for item in prices:
            sum = sum+float(item)

        def median(lst):
            sortedLst = sorted(lst)
            lstLen = len(lst)
            index = (lstLen - 1) // 2

            if (lstLen % 2):
                return sortedLst[index]
            else:
                return (sortedLst[index] + sortedLst[index + 1])/2.0

        if len(prices) != 0:
            result['price']['len'] = len(prices)
            result['price']['sum'] = sum
            result['price']['avg'] = float(sum/len(prices))
            result['price']['med'] = median(prices)
            result['price']['std'] = math.sqrt(median(prices))
            result['price']['min'] = min(prices)
            result['price']['max'] = max(prices)
        else:
            result['price']['len'] = 0
            result['price']['sum'] = 0
            result['price']['avg'] = 0
            result['price']['med'] = 0
            result['price']['std'] = 0
            result['price']['min'] = 0
            result['price']['max'] = 0

    def analyze_super_host():

        print ('Super_Host Analysis is started.')

        global listings
        global result

        super_host = []
        for l in listings:
            sh = (l['listing']['primary_host'].get('is_superhost'))
            if sh:
                super_host.append(sh)
            elif not sh:
                pass
        result['super_host']['count'] = len(super_host)
        result['super_host']['rate'] = round(len(super_host)/result['price']['len']*100, 1)

        print ('Done')

    def analyze_business_travel():

        print ('Business_Travel Analysis is started.')

        global listings
        global result

        business_travel = []
        for l in listings:
            bt = (l['listing'].get('is_business_travel_ready'))
            if bt:
                business_travel.append(bt)
            elif not bt:
                pass
        result['business_travel']['count'] = len(business_travel)
        result['business_travel']['rate'] = round(len(business_travel)/result['price']['len']*100, 1)

        print ('Done')

    def analyze_family_preferred():

        print ('Family_Preferred Analysis is started.')

        global listings
        global result

        family_preferred = []
        for l in listings:
            fp = (l['listing'].get('is_family_preferred'))
            if fp:
                family_preferred.append(fp)
            elif not fp:
                pass
        result['family_preferred']['count'] = len(family_preferred)
        result['family_preferred']['rate'] = round(len(family_preferred)/result['price']['len']*100, 1)

        print ('Done')

    def analyze_extra_host_language():

        print ('Extra_Host_Language Analysis is started.')

        global listings
        global result

        extra_host_languages = []
        for l in listings:
            ehl = (l['listing'].get('extra_host_languages'))
            for lang in ehl:
                extra_host_languages.append(lang)

        keys = list(Counter(extra_host_languages).keys())
        values = list(Counter(extra_host_languages).values())
        for num in range(0, len(keys)):
            result['extra_host_language'][keys[num]] = {}
            result['extra_host_language'][keys[num]]['count'] = values[num]
            result['extra_host_language'][keys[num]]['rate'] = round((values[num]/result['price']['len'])*100, 1)

        print ('Done')

    getneighbors()
    analyze_roomtype()
    analyze_price()
    analyze_super_host()
    analyze_business_travel()
    analyze_family_preferred()
    analyze_extra_host_language()

    return result
    # return {
    #     'statusCode': 200,
    #     'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-*': '*',  },
    #     'body': json.dumps(result)
    # }
