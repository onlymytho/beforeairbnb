# -*- coding: utf-8 -*-

# from botocore.vendored import requests
import sys
sys.path.insert(0, "/lib/site-packages")

import requests
import json
import time
import math
import operator
from threading import Thread
from collections import Counter
from geopy.distance import vincenty

my_user_api_key = 'd306zoyjsyarp7ifhu67rjxn52tv0t20'
end_point_url = 'https://api.airbnb.com/v2/search_results'


# Default query parameters
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


listings = []
prices = []
threads = []
ids = []
result = {}


neighbors_location = {}
neighbors_diff = []
my_location = {}


retry = 0

def getresults(event, context):


    def getneighbors():

        global threads
        global listings
        global result
        result = {'search_query':event['location'], 'total':{}, 'room_type':{}, 'price':{}, 'super_host':{}, 'business_travel':{}, 'family_preferred':{}, 'extra_host_language':{}}

        print ('BEFORE : ITEM COUNT OF LISTING :' + str(len(listings)))

        threads = []
        listings = []

        print ('INIT : ITEM COUNT OF LISTING :' + str(len(listings)))

        print ('Neighbors calling is started.')

        for n in range(len(incremental_search['price_min'])):
            def getlistingthread():
                global listings
                global threads
                global ids

                neighbors = []
                ids = []
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
                    # print ('ITEM COUNT OF listing_result in %s : '%n + str(len(listing_result)))
                    for l in listing_result:
                        id = l['listing'].get('id')
                        if id in ids:
                            pass
                        else:
                            ids.append(id)
                            neighbors.append(l)
                listings = listings + neighbors
                print ('ITEM COUNT OF NEIGHBORS %s :'%n + str(len(neighbors)))

            threads.append(Thread(target=getlistingthread))
            threads[n].setDaemon(True)
            threads[n].start()

        for n in range(len(incremental_search['price_min'])):
            threads[n].join()

        print ('AFTER : ITEM COUNT OF LISTING :' + str(len(listings)))

    def analyze_roomtype():

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
                result['room_type'][rt]['price']['avg'] = round(float(sum/len(prices[rt])), 0)
                result['room_type'][rt]['price']['med'] = median(prices[rt])
                result['room_type'][rt]['price']['std'] = math.sqrt(median(prices[rt]))
                result['room_type'][rt]['price']['min'] = min(prices[rt])
                result['room_type'][rt]['price']['max'] = max(prices[rt])
            else:
                result['room_type'][rt]['price']['len'] = 0
                result['room_type'][rt]['price']['sum'] = 0
                result['room_type'][rt]['price']['avg'] = 0
                result['room_type'][rt]['price']['med'] = 0
                result['room_type'][rt]['price']['std'] = 0
                result['room_type'][rt]['price']['min'] = 0
                result['room_type'][rt]['price']['max'] = 0

            listing_counts = {}
            listing_counts[rt] = result['room_type'][rt]['price']['len']
        result['room_type']['top'] = max(listing_counts)
        # room_type analysis is done
        print ('room_type analysis is done')

    def analyze_price():
        global listings
        global result
        global prices

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
            result['price']['avg'] = round(float(sum/len(prices)), 0)
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

        if result['super_host']['rate'] > 20:
            result['super_host']['message'] = {
                'ko': '슈퍼 호스트 비율이 상대적으로 높은 편입니다. 마냥 쉽지만은 않지만, 여전히 많은 기회가 있습니다.',
                'en': 'Super host rate is relatively high. But there are lots of opportunity.'
                }
        else:
            result['super_host']['message'] = {
                'ko': '슈퍼 호스트 비율이 상대적으로 낮은 편입니다. 이 지역에서 당신이 최고 호스트가 될 수도 있습니다.',
                'en': 'Super host rate is relatively low. You could be the top host of this area.'
                }
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

        if result['business_travel']['rate'] > 20:
            result['business_travel']['message'] = {
                'ko': '비즈니스 여행 선호 비율이 상대적으로 높은 편입니다. 위기를 기회로 만드세요.',
                'en': 'Business preffred rate is relatively high. Make crisis to an opportunity.'
                }
        else:
            result['business_travel']['message'] = {
                'ko': '비즈니스 여행 선호 비율이 상대적으로 낮은 편입니다. 비즈니스 여행객을 맞을 준비를 하세요.',
                'en': 'Business preffred rate is relatively low. Ready to host business people.'
                }

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

        if result['family_preferred']['rate'] > 20:
            result['family_preferred']['message'] = {
                'ko': '가족 여행 선호 비율이 상대적으로 높은 편입니다. 하지만 가족 여행객은 많습니다.',
                'en': 'Family preffred rate is relatively high. But family need many rooms.'
                }
        else:
            result['family_preferred']['message'] = {
                'ko': '가족 여행 선호 비율이 상대적으로 낮은 편입니다. 가족 여행객을 맞을 준비를 하세요.',
                'en': 'Family preffred rate is relatively low. Ready to host family travelers.'
                }

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
        result['extra_host_language']['list'] = []
        result['extra_host_language']['count'] = {}
        result['extra_host_language']['rate'] = {}
        for num in range(0, len(keys)):
            result['extra_host_language']['count'][str(keys[num])] = values[num]
            result['extra_host_language']['rate'][str(keys[num])] = round((values[num]/result['price']['len'])*100, 1)

        sorted_extra_host_language_count = sorted(result['extra_host_language']['count'].items(), key=operator.itemgetter(1), reverse=True )
        sorted_extra_host_language_rate = sorted(result['extra_host_language']['rate'].items(), key=operator.itemgetter(1), reverse=True)

        print ('BEFORE SORTED (dict) : ' + str(result['extra_host_language']['rate']))
        print ('AFTER SORTED (tuple) : ' + str(sorted_extra_host_language_rate))

        for key, val in sorted_extra_host_language_count:
            result['extra_host_language']['count'][str(key)] = val
        for key, val in sorted_extra_host_language_rate:
            result['extra_host_language']['rate'][str(key)] = val

        print ('AFTER SORTED (dict) : ' + str(result['extra_host_language']['rate']))

        for k in result['extra_host_language']['rate'].keys():
            result['extra_host_language']['list'].append(k)

        print ('Done')


    def analyze_score():
        listing_count = result['price']['len']
        super_host_rate = result['super_host']['rate']
        score = 100 - (int(listing_count/150) + int(super_host_rate/10))
        score_text_ko = ''
        score_text_en = ''

        if score > 95:
            score_text_en = "Perfect. Don't hesitate, just open your airbnb now."
            score_text_ko = "최적의 조건이네요! 지금 당장 에어비엔비 시작해보세요."
        elif score > 85:
            score_text_en = "Fine. You can go with the unique edge of your airbnb."
            score_text_ko = "괜찮네요. 포인트만 잘 잡으면 충분히 성공할 수 있어요."
        elif score > 80:
            score_text_en = "Not easy. But there’s still opportunity. Move on!"
            score_text_ko = "쉽지는 않겠지만 충분히 할 만해요. 도전해보세요!"
        else:
            score_text_en = "Difficult. I think you should find other location."
            score_text_ko = "힘들어요. 하지만 정말 잘 할 자신이 있다면 시작하세요."
        result['total'] = {}
        result['total']['score'] = score
        result['total']['message'] = {'ko':score_text_ko, 'en':score_text_en}



    def analyze_distance():
        global my_location
        global neighbors_location
        global neighbors_diff

        # Get my location
        r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+event['location'])
        rjson = r.json()
        my_location = rjson['results'][0]['geometry']['location']
        my_location = (my_location['lat'], my_location['lng'])
        print ('My location : ' + str(my_location))

        # Get other listings' locations
        for l in listings:
            id = l['listing'].get('id')
            lat = l['listing'].get('lat')
            lng = l['listing'].get('lng')
            neighbors_location[str(id)] = {'lat':lat, 'lng':lng}
        print ('Count of other listings : ' + str(len(neighbors_location)))

        # Calculate distances
        neighbors_diff = []
        for loc in neighbors_location.values():
            loc = (loc['lat'], loc['lng'])
            d = vincenty(my_location, loc).meters
            neighbors_diff.append(d)
        print ("Count of other listings' diff : " + str(len(neighbors_diff)))
        print ("Mininum of diff : " + str(min(neighbors_diff)))
        print ("Maximum of diff : " + str(max(neighbors_diff)))


        # Select listings in distances and insert to the result
        neighbors_by_distances = {}
        result['distance'] = {}

        distances = [10, 20, 50, 100, 200, 300, 500, 1000, 2000, 3000]
        for distance in distances:
            neighbors_by_distances[str(distance)] = []
            for d in neighbors_diff:
                if d < distance:
                    neighbors_by_distances[str(distance)].append(d)
                else:
                    pass
            result['distance'][str(distance)] = len(neighbors_by_distances[str(distance)])


    def getneighborsRETRY():
        global retry

        try:
            getneighbors()
        except RuntimeError as e:
            if retry < 3:
                print(e)
                print("RuntimeError has occured. Trying again.")
                getneighborsRETRY()
                retry += 1
                print ('Retry : ' + str(retry))

    getneighborsRETRY()
    analyze_roomtype()
    analyze_price()
    analyze_super_host()
    analyze_business_travel()
    analyze_family_preferred()
    analyze_extra_host_language()
    analyze_score()
    analyze_distance()

    print (result)
    return result
