import requests
import json

url = "https://kauth.kakao.com/oauth/token"

data = {
    'grant_type' : 'authorization_code',
    'client_id' : '85ebcb4e804e57268332118b870d5fa4',
    'redirect_url' : 'https://localhost.com',
    'code' : 'Wq6F5TkvIyklIhzu39_0j4_X_hh6t1D9e6bIc_hRf4uUij4GpD6xIMmWfmvqyIQGFS2Nago9c5sAAAF6BSIFtw'

}
response = requests.post(url, data=data)

tokens = response.json()

print(tokens)

with open('kakao_tokens.json','w') as fp:
    json.dump(tokens,fp)