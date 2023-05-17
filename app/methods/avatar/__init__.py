from app.models import Avatar

def getAllAvatars():
    return Avatar.getAvatars()