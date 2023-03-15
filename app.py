from flask import Flask, request
from flask import make_response
from tempfile import gettempdir
import json
import os

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def trigger_processing():
    comments = request.json["comments"]
    description = request.json["description"]

    #read the file
    #load the string readed into json object

    #generate the path where you want to save your file (in my case the temp folder)
    #and save the file
    save_path = "comments.json"
    file = open(save_path, encoding='utf-8')
    current_list = json.load(file)
    current_list.extend(comments)

    with open(save_path, 'w', encoding='utf-8') as outfile:
        json.dump(current_list, outfile)

    save_path = "descriptions.json"
    file = open(save_path, encoding='utf-8')
    current_list = json.load(file)
    current_list.extend(comments)

    with open(save_path, 'w', encoding='utf-8') as outfile:
        json.dump(current_list, outfile)

    return make_response(json.dumps({'message': "ok"}), 200)