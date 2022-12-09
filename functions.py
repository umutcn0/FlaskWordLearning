import requests
import json
from settings import settings
def get_description(word):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word.upper()}/definitions"
    key = settings()["API_KEY"]

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers)
    response = json.loads(response.text)
    if "definitions" in response:
        return response["definitions"][0]["definition"]
    else:
        return "No such a word on the dictionary"