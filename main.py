import tweepy
import folium
import pandas as pd
from shapely.geometry import Polygon
import json
import random

consumer_key = "nEfVi8N8KBmcmxWC5KqJxdHdc"
consumer_secret = "tK8853ShfWoTaV7smB9X7Mq7RMZmqX3iv7ElmaRXvPT4FMqaqP"
access_key = "1277992408052105217-9bvcOzqKgTx8YJlG2zf3Wtj0ptBoOy"
access_secret = "WgmkljliSqA6qjqKwY6DLPSbkDdQzHmhZFKS9E0m0bEQR"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAMVGFgEAAAAA%2FYJFSdycowTGFf0tcRP9%2BaerZso%3DF3IahdxCBX6nwp6L1Q4bW6ExUlAuLkMKhEXzyYQjQwThyqAcFv"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)

'''
places = api.geo_search(query="FRANCE", granularity="country")
place_id = places[0].id
tweets = api.search(q="place:%s" % place_id, count=2)
'''

'''
def geoTweets(geoInfo, range):

    tweets = []
    places = api.geo_search(lat=geoInfo['geometry']['location']['lat'], long=geoInfo['geometry']['location']['lng'], range=str(range) + "km", max_results=5)

    for i in places:
        l = api.search(q='place:'+places[0].id, count=100)
        for t in l:
            tweets.append(t)
    return tweets



#geoloactedTweets(api,30,30,3000,5)
'''


def getcodeCoordFromAddr(address):
    import googlemaps
    gmaps = googlemaps.Client('AIzaSyCNPwtdvyRqQrAUIxCUjSDVKXzy3eZj-NI')  # yay la sécurité

    res = gmaps.geocode(address)
    try:
        return res[0]
    except:
        return None

def geoloactedTweets(api, geoInfo, rangeKm, count):
    return api.search(geocode=str(geoInfo['geometry']['location']['lat']) + "," + str(geoInfo['geometry']['location']['lng']) + "," + str(rangeKm) + "km", lang="en", count=count)



lat = []
lng = []
places = []
values = []
types = []
bbox = []
texts = []

orginAddress = input('Address : ')
originGeoInfo = getcodeCoordFromAddr(orginAddress)

if originGeoInfo != None:

    search_range = input('Search range (Km) : ')

    for tweet in geoloactedTweets(api ,originGeoInfo, search_range, 10):
        #print(tweet._json)

        location = tweet._json['user']['location']



        latVal = None
        lngVal = None
        typesVal = None
        bboxVal = None
        text = "Tweet by : " + tweet._json["user"]["screen_name"] + "               " + tweet._json["text"]

        if tweet._json["coordinates"]:
            typesVal = "coordinates"
            latVal = tweet._json["coordinates"]["coordinates"][1]
            lngVal = tweet._json["coordinates"]["coordinates"][0]

        elif tweet._json["place"]:
            typesVal = "bounding_box"
            bboxVal = tweet._json["place"]["bounding_box"]["coordinates"][0]
        else:
            geoInfo = getcodeCoordFromAddr(location)
            if geoInfo != None:
                latVal = geoInfo['geometry']['location']['lat']
                lngVal = geoInfo['geometry']['location']['lng']


        print(latVal,lngVal,orginAddress,typesVal,bboxVal)

        if typesVal != "bounding_box" and latVal != None and lngVal != None:
            lat.append(latVal)
            lng.append(lngVal)
            places.append(orginAddress)
            values.append(1)
            types.append(typesVal)
            bbox.append(bboxVal)
            texts.append(text)






    # Make a data frame with dots to show on the map
    data = pd.DataFrame({
        'lat': lat,
        'lon': lng,
        'name': places,
        'value': values,
        'type': types,
        'bbox': bbox,
        'text': texts
    })
    data

    print(data)

    # Make an empty map
    m = folium.Map()

    folium.Circle(
            location=[originGeoInfo['geometry']['location']['lat'], originGeoInfo['geometry']['location']['lng']],
            popup='Search point',
            radius=search_range * 1000,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)

    # I can add marker one by one on the map
    for i in range(0, len(data)):
        if data.iloc[i]['type'] == 'coordinates' or data.iloc[i]['type'] == None:
            folium.Marker(
                location=[data.iloc[i]['lat'], data.iloc[i]['lon']],
                popup=data.iloc[i]['text'],
                color='crimson',
                fill=True,
                fill_color='crimson'
            ).add_to(m)
        elif data.iloc[i]['type'] == 'bounding_box':
            folium.Marker(
                location=[sum([i[1] for i in data.iloc[i]['bbox']]) / len([i[1] for i in data.iloc[i]['bbox']]) + random.Choice(range(-10,10)), sum([i[0] for i in data.iloc[i]['bbox']]) / len([i[0] for i in data.iloc[i]['bbox']]) + random.Choice(range(-10,10))],
                popup=data.iloc[i]['text'],
                color='crimson',
                fill=True,
                fill_color='crimson'
            ).add_to(m)

    # Save it as html
    m.save('./html/main.html')