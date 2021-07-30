import json
import requests
import trello_auth
forecast_card = '60fe9cba105c670979f8b078'
board = 'edwtCYIe'
pooling_list ='60e80b27ff95224ceef4cfd3'

headers = {
        "Accept": "application/json"
    }

query = {
        'key': trello_auth.key,
        'token': trello_auth.token
    }


def get_board_lists(board_id):

    url = "https://api.trello.com/1/boards/"+board_id+"/lists"

    response = requests.request(
        "GET",
        url,
        params=query
    )

    response = response.json()

    return response


def get_card_fields(card_id):
    url = "https://api.trello.com/1/cards/"

    card_fields = requests.request(
        "GET",
        url + card_id,
        headers=headers,
        params=query
    )
    card_fields = card_fields.json()
    return card_fields


def get_card_name(card_id):
    card_fields = get_card_fields(card_id)
    card_name = (card_fields["name"])
    return card_name


lists = (get_board_lists(board))
print(json.dumps(lists, indent=4))
daily_forecast = get_card_name(forecast_card)
print(daily_forecast)
