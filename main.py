from functools import wraps
import os
import firebase_admin
from flask import Flask, json, request, session, redirect, jsonify
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from firebase_admin import auth

os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/orenb/AndroidStudioProjects/list_maker/android/app/listmaker-3336d" \
                                        "-a10ff778ab6d.json "

default_app = firebase_admin.initialize_app()
app = Flask(__name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jsonData = request.json
        token = jsonData["token"]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            decodedToken = json.dumps(id_token.verify_firebase_token(id_token=token, request=requests.Request()))
        except:
            print('token is invalid')
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


@app.route('/<endpoint>', methods=['POST'])
@token_required
def mainRoute(endpoint):
    dataFile = open("data.json", "r")
    jsonDataFile = json.load(dataFile)
    jsonParams = request.json
    token = jsonParams["token"]
    decodedToken = json.loads(json.dumps(id_token.verify_firebase_token(id_token=token, request=requests.Request())))
    userId = decodedToken["user_id"]
    listName = ""
    itemName = ""
    companyName = ""
    if "list_name" in jsonParams:
        listName = jsonParams["list_name"]
    if "item_name" in jsonParams:
        itemName = jsonParams["item_name"]
    if "company_name" in jsonParams:
        companyName = jsonParams["company_name"]
    if endpoint == 'create_user':
        return create_user(jsonDataFile, userId)
    if endpoint == 'add_list':
        return add_list(jsonDataFile, userId, listName)
    if endpoint == 'remove_list':
        return remove_list(jsonDataFile, userId, listName)
    if endpoint == 'get_lists':
        return get_lists(jsonDataFile, userId)
    if endpoint == 'add_item':
        return add_item(jsonDataFile, userId, listName, itemName, companyName)
    if endpoint == 'remove_item':
        return remove_item(jsonDataFile, userId, listName, itemName, companyName)
    if endpoint == 'check_item':
        return check_item(jsonDataFile, userId, listName, itemName, companyName)
    if endpoint == 'uncheck_item':
        return uncheck_item(jsonDataFile, userId, listName, itemName, companyName)



def create_user(jsonDataFile, new_user_id):
    for user in jsonDataFile:
        if user["user_id"] == new_user_id:
            return "a user with this id already exists"
    jsonDataFile.append(create_new_user(new_user_id))
    dataFile = open("data.json", "w")
    dataFile.write(json.dumps(jsonDataFile))
    return "user created successfully"


def add_list(jsonData, userId, listName):
    for user in jsonData:
        if user["user_id"] == userId:
            for userList in user["lists"]:
                if userList["list_name"] == listName:
                    return "this user already has a list with this name"
            user["lists"].append(create_empty_list(listName))
            dataFile = open("data.json", "w")
            dataFile.write(json.dumps(jsonData))
            return json.dumps(user["lists"])
    return "this user doesnt exist"


def remove_list(jsonData, userId, listName):
    for user in jsonData:
        if user["user_id"] == userId:
            for userList in user["lists"]:
                if userList["list_name"] == listName:
                    user["lists"].remove(userList)
                    dataFile = open("data.json", "w")
                    dataFile.write(json.dumps(jsonData))
                    return json.dumps(user["lists"])
            return "this user doesnt have a list with this name"
    return "this user doesnt exist"


def get_lists(jsonData, userId):
    for user in jsonData:
        if user["user_id"] == userId:
            return json.dumps(user["lists"])


def add_item(jsonDataFile, userId, listName, itemName, companyName):
    for user in jsonDataFile:
        if user["user_id"] == userId:
            for userList in user["lists"]:
                if userList["list_name"] == listName:
                    userList["uncheckedItems"].append(create_item(itemName, companyName))
                    dataFile = open("data.json", "w")
                    dataFile.write(json.dumps(jsonDataFile))
                    return json.dumps(userList)
            return "this user doesnt have a list with this name"
    return "this user doesnt exist"


def remove_item(jsonDataFile, userId, listName, itemName, companyName):
    for user in jsonDataFile:
        if user["user_id"] == userId:
            for userList in user["lists"]:
                if userList["list_name"] == listName:
                    for item in userList["uncheckedItems"]:
                        if item["item_name"] == itemName and item["company_name"] == companyName:
                            userList["uncheckedItems"].remove(item)
                            dataFile = open("data.json", "w")
                            dataFile.write(json.dumps(jsonDataFile))
                            return json.dumps(userList)
                    for item in userList["checkedItems"]:
                        if item["item_name"] == itemName and item["company_name"] == companyName:
                            userList["checkedItems"].remove(item)
                            dataFile = open("data.json", "w")
                            dataFile.write(json.dumps(jsonDataFile))
                            return json.dumps(userList)
                    return "this item doesnt exist in this list"
            return "this user doesnt have a list with this name"
    return "this user doesnt exist"


def check_item(jsonDataFile, userId, listName, itemName, companyName):
    for user in jsonDataFile:
        if user["user_id"] == userId:
            for userList in user["lists"]:
                if userList["list_name"] == listName:
                    for item in userList["uncheckedItems"]:
                        if item["item_name"] == itemName and item["company_name"] == companyName:
                            userList["checkedItems"].append(item)
                            userList["uncheckedItems"].remove(item)
                            dataFile = open("data.json", "w")
                            dataFile.write(json.dumps(jsonDataFile))
                            return json.dumps(userList)
                    return "there isnt an unchecked item with this name in this list"
            return "this user doesnt have a list with this name"
    return "this user doesnt exist"


# @app.route('/uncheck_item', methods=['POST'])
# @token_required
def uncheck_item(jsonDataFile, userId, listName, itemName, companyName):
    # dataFile = open("data.json", "r")
    # jsonData = json.load(dataFile)
    # jsonParams = request.json
    # token = jsonParams["token"]
    # decodedToken = json.loads(json.dumps(id_token.verify_firebase_token(id_token=token, request=requests.Request())))
    # user_id = decodedToken["user_id"]
    # list_name = jsonParams["list_name"]
    # item_name = jsonParams["item_name"]
    # company_name = jsonParams["company_name"]
    # if request.method == 'POST':
    for user in jsonDataFile:
        if user["user_id"] == userId:
            for userList in user["lists"]:
                if userList["list_name"] == listName:
                    for item in userList["checkedItems"]:
                        if item["item_name"] == itemName and item["company_name"] == companyName:
                            userList["uncheckedItems"].append(item)
                            userList["checkedItems"].remove(item)
                            dataFile = open("data.json", "w")
                            dataFile.write(json.dumps(jsonDataFile))
                            return json.dumps(userList)
                    return "there isnt an unchecked item with this name in this list"
            return "this user doesnt have a list with this name"
    return "this user doesnt exist"


# @app.route('/add_friend', methods=['POST'])
# def add_friend():
#     dataFile = open("data.json", "r")
#     jsonData = json.load(dataFile)
#     params = request.json
#     friend1Added = False
#     friend2Added = False
#     if len(params) != 2:
#         return "wrong params"
#     if request.method == 'POST':
#         for user in jsonData:
#             if user["user_id"] == params[0]:
#                 for friend in user["friends"]:
#                     if friend == params[1]:
#                         return "these users are already friends"
#                 user["friends"].append(params[1])
#                 friend1Added = True
#             if user["user_id"] == params[1]:
#                 for friend in user["friends"]:
#                     if friend == params[1]:
#                         return "these users are already friends"
#                 user["friends"].append(params[0])
#                 friend2Added = True
#         if friend1Added and friend2Added:
#             dataFile = open("data.json", "w")
#             dataFile.write(json.dumps(jsonData))
#             return "friend added successfully"
#         if (not friend1Added) and (not friend2Added):
#             return "these users dont exist"
#         if not friend1Added:
#             return "user id: " + params[0] + " doesnt exist"
#         if not friend2Added:
#             return "user id: " + params[1] + " doesnt exist"
#
#
# @app.route('/remove_friend', methods=['POST'])
# def remove_friend():
#     dataFile = open("data.json", "r")
#     jsonData = json.load(dataFile)
#     params = request.json
#     friend1Added = False
#     friend2Added = False
#     if len(params) != 2:
#         return "wrong params"
#     if request.method == 'POST':
#         for user in jsonData:
#             if user["user_id"] == params[0]:
#                 for friend in user["friends"]:
#                     if friend == params[1]:
#                         return "these users are already friends"
#                 user["friends"].append(params[1])
#                 friend1Added = True
#             if user["user_id"] == params[1]:
#                 for friend in user["friends"]:
#                     if friend == params[1]:
#                         return "these users are already friends"
#                 user["friends"].append(params[0])
#                 friend2Added = True
#         if friend1Added and friend2Added:
#             dataFile = open("data.json", "w")
#             dataFile.write(json.dumps(jsonData))
#             return "friend added successfully"
#         if (not friend1Added) and (not friend2Added):
#             return "these users dont exist"
#         if not friend1Added:
#             return "user id: " + params[0] + " doesnt exist"
#         if not friend2Added:
#             return "user id: " + params[1] + " doesnt exist"
#
#
# # gets a user who owns the list, a user who you share the list with, and the lists name
# @app.route('/share_list', methods=['POST'])
# def share_list():
#     dataFile = open("data.json", "r")
#     jsonData = json.load(dataFile)
#     params = request.json
#     user1Exists = False
#     user2Exists = False
#     listExists = False
#     if len(params) != 3:
#         return "wrong params"
#     if request.method == 'POST':
#         for user in jsonData:
#             if user["user_id"] == params[0]:
#                 user1Exists = True
#             if user["user_id"] == params[1]:
#                 user2Exists = True
#         if (not user1Exists) and (not user2Exists):
#             return "these users dont exist"
#         if not user1Exists:
#             return "user id: " + params[0] + " doesnt exist"
#         if not user2Exists:
#             return "user id: " + params[1] + " doesnt exist"
#         for user in jsonData:
#             if user["user_id"] == params[0]:
#                 for lst in user["lists"]:
#                     if lst["list_name"] == params[2]:
#                         for shared_user in lst["shared_with"]:
#                             if shared_user == params[1]:
#                                 return "this list is already shared with this user"
#                         lst["shared_with"].append(params[1])
#                         listExists = True
#                 if not listExists:
#                     return "the user " + params[0] + " doesnt have a list named '" + params[2] + "'"
#             if user["user_id"] == params[1]:
#                 user["shared_lists"] = add_shared_list(user["shared_lists"], params[0], params[2])
#         dataFile = open("data.json", "w")
#         dataFile.write(json.dumps(jsonData))
#         return "list shared successfully"


def create_empty_list(list_name):
    new_list = {"list_name": list_name, "checkedItems": [], "uncheckedItems": [], "shared_with": []}
    return new_list


def create_new_user(user_id):
    new_user = {"user_id": user_id, "lists": [], "friends": [], "shared_lists": {}}
    return new_user


# def add_shared_list(shared_list_dict, shared_user, shared_list):
#     if shared_user in shared_list_dict:
#         if shared_list in shared_list_dict[shared_user]:
#             return shared_list_dict[shared_user]
#         else:
#             shared_list_dict[shared_user].append(shared_list)
#             return shared_list_dict
#     else:
#         shared_list_dict[shared_user] = [shared_list]
#         return shared_list_dict


def create_item(item_name, company_name):
    new_item = {"item_name": item_name, "company_name": company_name}
    return new_item


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'secret'
    app.run(debug=True)
