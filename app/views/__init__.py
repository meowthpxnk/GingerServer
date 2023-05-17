from app import app, socket
import os
from flask import send_file, request
from app.models import Avatar
from app.methods.user import create, verifySecretKey
from app.validators import Validator


@app.route('/')
def home():
    return {'ok': True}


@app.route('/images/<directory>/<filename>', methods=['GET'])
def getImage(directory, filename):
    match directory:
        case "avatars":
            pass
        case "topics":
            pass
        case _:
            return {"ok": False, "error": "No such directory"}

    basedir = os.path.abspath(os.path.dirname(""))
    path = os.path.join(
        basedir, app.config["STORAGE"], 'images', directory, filename)

    try:

        return send_file(path)
    except:
        return {"ok": False, "error": "No such file"}


@app.route('/getAvailableImages')
def getAvailableImages():
    return Avatar.getAvatars()


@app.route('/api/authentificate_user', methods=['POST'])
def authUser():
    validator = Validator(request.json)
    data = validator.data
    secret_key = create(data['user_name'], data['avatar'])

    return {
        'status': 'ok',
        'result': {
            'secret_key': secret_key
        }
    }

@app.route('/api/verify_secret_key', methods=['GET'])
def rescan():
    # validator = Validator(request.json)
    # data = validator.data
    data = {
        'user_name': request.args['user_name'],
        'secret_key': request.args['secret_key']
    }

    result = verifySecretKey(data['user_name'], data['secret_key'])

    return {
        'status': 'ok',
        'result': result
    }

from app.methods.avatar import getAllAvatars

@app.route('/api/getAvatars', methods=['GET'])
def getAvatars():

    return {
        'status': 'ok',
        'result': getAllAvatars()
    }

from app.methods.topic import getAllTopics

@app.route('/api/getTopics', methods=['GET'])
def getTopics():

    return {
        'status': 'ok',
        'result': getAllTopics()
    }

from app.lobbies import Lobby

@app.route('/api/generateGame', methods=['POST'])
def generateGame():

    validator = Validator(request.json)
    data = validator.data
    
    print(data['user_name'], data['title'], data['topics'])
    
    Lobby.create(data['user_name'], data['title'], data['topics'])
    
    return {
        'status': 'ok',
    }

@app.route('/api/getLobbies')
def getLobbies():
    lobbies = Lobby.getLoadLobbiesList()
    return {
        'status': 'ok',
        'result': lobbies
    }

@socket.on('create_lobby')
def create_lobby(title):
    socket.emit('lobby_has_been_created', Lobby(title).json())

# from flask_socketio import emit

# @socket.on('message')
# def connect_socket():
#     socket.emit('lobby_has_been_created', {'123': 'test'})

# @socket.on('messages')
# def connect_socket(data):
#     print('received message: ' + data)