import requests
import trello_auth

orgId = "60e7f97643060b58d1ea63c6"
# For instance, if you wanted to get all of the cards for a board you could use: https://api.trello.com/1/boards/{boardId}/cards or https://api.trello.com/1/boards/{boardId}/?cards=all
response = requests.get(
    "https://api.trello.com/1/members/me/boards?key=" + trello_auth.key + "&token=" + trello_auth.token)
print(response.text)
# f = open("response.txt", "x")
# f.write(response.text)
# f.close()
# https://api.trello.com/1/boards/{boardId}/cards
# boards = requests.get("https://api.trello.com/1/organizations /"+orgId+"?boards=open")
# print(boards)
boardTestTvId = "60e80b27ff95224ceef4cfd1"
f = open("cardsTV.json", "w")
f.write(requests.get("https://api.trello.com/1/boards/60e80b27ff95224ceef4cfd1//cards?key=" + trello_auth.key
                     + "&token=" + trello_auth.token).text)
f.close()
