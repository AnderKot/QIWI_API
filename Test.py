import requests
from requests.structures import CaseInsensitiveDict

url = "https://api.qiwi.com/partner/bill/v1/bills/12/reject"

headers = CaseInsensitiveDict()
headers["content-type"] = "application/json"
headers["accept"] = "application/json"
headers["Authorization"] = "Bearer eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6IjY2MnI2eC0wMCIsInVzZXJfaWQiOiI3OTg4NTAyODc3NSIsInNlY3JldCI6ImJiMTBlMDk3NzYyNjhiMTRmOGMzYzFhYzZlMzQ4MzkwNTUyNjY0Mjk3YTZiNjU0MWU5YmVhODQ4M2ZkZjliMzEifX0="

data = ''

print(headers)
resp = requests.post(url, headers=headers, data=data)

print(resp.status_code)
