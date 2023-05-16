from app.models import Topic

def getAllTopics():
    return Topic.getTopics()