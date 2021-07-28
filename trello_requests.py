import requests
import json
import trello_auth


def get_daily_forecast():
    url = "https://api.trello.com/1/cards/"
    forecast_card_id = '60fe9cba105c670979f8b078'
    headers = {
        "Accept": "application/json"
    }

    query = {
        'key': trello_auth.key,
        'token': trello_auth.token
    }

    daily_forecast = requests.request(
        "GET",
        url + forecast_card_id,
        headers=headers,
        params=query
    )

    daily_forecast = daily_forecast.json()
    print(daily_forecast)
    print(daily_forecast["name"])
    print(daily_forecast["dateLastActivity"])
    print(json.dumps(json.loads(daily_forecast.text), sort_keys=True, indent=4, separators=(",", ": ")))
