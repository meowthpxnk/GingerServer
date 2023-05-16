import os
import random

from app import db

class BaseQuery():
    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def findByID(cls, id):
        item = db.session.query(cls).filter(cls.id==id).first()
        if not item:
            raise Exception('Not found item')
        return item

class User(db.Model, BaseQuery):
    name = db.Column(db.String)
    avatar_id = db.Column(db.Integer, db.ForeignKey('avatar.id'))
    avatar = db.relationship('Avatar', backref=db.backref('users', lazy='dynamic'))

    secret_key = db.Column(db.String)

    def __init__(self, name, avatar_id):
        self.name = name
        self.avatar_id = avatar_id
    
    def __repr__(self):
        return self.name
    
    def updateSecretKey(self, secret_key):
        self.secret_key = secret_key

    def isValidSecretKey(self, secret_key):
        return self.secret_key == secret_key

    @classmethod
    def findByName(cls, name):
        item = db.session.query(cls).filter(cls.name==name).first()
        
        if not item:
            raise Exception('Not found item')

        return item

class Avatar(db.Model, BaseQuery):
    file_name = db.Column(db.String, unique=True)

    def __init__(self, file_name):
        self.file_name = file_name

    @classmethod
    def getAvatars(cls):
        avatars = db.session.query(cls).all()
        return [avatar.file_name for avatar in avatars]

    @classmethod
    def findByFileName(cls, file_name):
        item = db.session.query(cls).filter(cls.file_name==file_name).first()
        
        if not item:
            raise Exception('Not found item')

        return item
    
class Topic(db.Model, BaseQuery):
    title = db.Column(db.String)
    image_file_name = db.Column(db.String)
    questions = db.relationship("Question", back_populates="topic")
    
    def __repr__(self):
        return f'<TopicModel {self.title}>'

    def __init__(self, title, image_file_name):
        self.title = title
        self.image_file_name = image_file_name
        
    def getRandQuestions(self, amount):
        return random.sample(self.questions, amount)

    @classmethod
    def getTopics(cls):
        topics = db.session.query(cls).all()
        return [topic.json() for topic in topics]
    
    def json(self):
        return {
            'title': self.title,
            'image': self.image_file_name
        }
        
    @classmethod
    def findByTitle(cls, title):
        item = db.session.query(cls).filter(cls.title==title).first()
        if not item:
            raise Exception('Not found item')
        return item
        
class Question(db.Model, BaseQuery):
    question = db.Column(db.String)
    answer_1 = db.Column(db.String)
    answer_2 = db.Column(db.String)
    answer_3 = db.Column(db.String)
    answer_4 = db.Column(db.String)
    
    correct = db.Column(db.Integer)
    
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    topic = db.relationship("Topic", back_populates="questions")
    # topic = db.relationship('Topic', backref=db.backref('questions', lazy='dynamic'))
    
    def __init__(self, question, answer_1, answer_2, answer_3, answer_4, correct, topic_id):
        self.question = question
        self.answer_1 = answer_1
        self.answer_2 = answer_2
        self.answer_3 = answer_3
        self.answer_4 = answer_4
        
        self.correct = correct
        
        self.topic_id = topic_id
    
    def json(self):
        return {
            'question': self.question,
            'answers': {
                1: self.answer_1,
                2: self.answer_2,
                3: self.answer_3,
                4: self.answer_4,
            },
            'correct': self.correct
        }