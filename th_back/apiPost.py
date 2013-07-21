import requests

#login
r = requests.post('http://127.0.0.1:8800/login/',data={'username':'ihkey','password':'123456'})
api_key = r.headers['api_key']
print r