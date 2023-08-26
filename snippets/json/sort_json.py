import json

l = []
with open('CountryCodesES.json', 'rb') as json_file:
    data = json.load(json_file, encoding='utf-8')
    l.extend(int(country['dial_code']) for country in data)
l.sort()

new_json = []
with open('CountryCodesES.json', 'rb') as json_file:
    data = json.load(json_file, encoding='utf-8')
    for i in l:
        new_json.extend(country for country in data if int(country['dial_code']) == i)
with open('CountryCodesES2.json', 'w') as outfile:
    json.dump(new_json, outfile)