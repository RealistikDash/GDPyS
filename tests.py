import requests

url = "http://vliengdps.7m.pl/database/getGJAccountComments20.php"

Data = {
    "gameVersion" : 21,
    "binaryVersion" : 35,
    "gdw" : 0,
    "accountID" : 12,
    "gjp" : "UFZbR1JcWUE=",
    "page" : 0,
    "total" : 0,
    "secret" : "Wmfd2893gb7"
}

data = requests.post(url, data = Data)

print(data.text)
print(data.json())