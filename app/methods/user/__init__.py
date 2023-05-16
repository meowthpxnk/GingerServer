from app.models import User, Avatar
from app import db
from ..utils import generateCookieString

def create(user_name, avatar):
    avatar = Avatar.findByFileName(avatar)
    print(avatar)
    user = User(user_name, avatar.id)
    db.session.add(user)

    secret_key = generateCookieString()

    user.updateSecretKey(secret_key)

    db.session.commit()

    return secret_key

def verifySecretKey(user_name, secret_key):
    try:
        user = User.findByName(user_name)
    except:
        return False
    return user.isValidSecretKey(secret_key)