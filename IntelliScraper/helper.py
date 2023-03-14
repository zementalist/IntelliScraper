import json

def read_list_companies(filepath):
    file = open(filepath)
    data = json.load(file)
    return data