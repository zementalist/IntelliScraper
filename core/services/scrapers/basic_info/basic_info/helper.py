import json

def read_list_companies(filepath):
    file = open(fr'{filepath}')
    data = json.load(file)
    return data