import dota2api
from pymongo import MongoClient

from api_key import API_KEY
api = dota2api.Initialise(API_KEY)

heroes_data = api.get_heroes()

heroes_count = heroes['count']
heroes = heroes['heroes']

client = MongoClient()

for i in heroes['heroes']:
    db.heroes.insert_one({"id":i['id'],"name":i['localized_name']})
