from app import redis_db

import random


t_lobbies_list = 'G.Lobbies'
t_lobby_status = 'G.Lobby.{}.status'
t_lobby_players_list = 'G.Lobby.{}.players'
t_lobby_topics_list = 'G.Lobby.{}.topics'
t_lobby_questions_list = 'G.Lobby.{}.questions'
t_active_players_list = 'G.ActivePlayersList'
t_player_lobby = 'G.Player.{}.lobby'

t_status_load = "LOAD"
t_status_started = "STARTED"
t_status_ended = "ENDED"

from app.models import Question as QuestionDB, Topic as TopicDB
from ..methods.math import createIndexMassive

class Topic:
    title: str

    def __init__(self, title):
        self.title = title

    def getQuestions(self, amount):
        return TopicDB.findByTitle(self.title)\
            .getRandQuestions(amount)

class Question:
    id: int
    
    def __init__(self, id):
        self.id = id
        
    def json(self):
        return QuestionDB.findByID(self.id).json()

class Player:
    name: str
    lobby_title: str | None

    def __init__(self, name):
        self.name = name
        self.lobby_title = redis_db.get(t_player_lobby.format(self.name))

    def __repr__(self):
        return f'<Player {self.name}>'

    def registrate(self, lobby_title):
        if self.isActive():
            raise Exception(f'Player {self.name} already exist in lobby "{self.lobby_title}"')
        self.lobby_title = lobby_title
        redis_db.list_push(t_lobby_players_list.format(lobby_title), self.name)
        redis_db.list_push(t_active_players_list, self.name)
        redis_db.set(t_player_lobby.format(self.name), lobby_title)
    
    def exit(self):
        if not self.isActive():
            raise Exception(f'Player {self.name} not exist in lobby')
        self.lobby_title = None
        redis_db.list_rem(t_lobby_players_list.format(self.lobby_title), self.name)
        redis_db.list_rem(t_active_players_list, self.name)
        redis_db.delete(t_player_lobby.format(self.name))

    @staticmethod
    def active_players():
        return redis_db.list_get(t_active_players_list)
    
    def isActive(self):
        return self.lobby_title != None


class Lobby:
    title: str
    status: str
    topics: list[Topic]
    players: list[Player]
    questions: list[Question] | None

    def __init__(self, title):
        if not self.isExisted(title):
            raise Exception(f'Not found lobby with title {title}')
        self.title = title
        self.status = redis_db.get(t_lobby_status.format(self.title))
        self.topics = [Topic(title) for title in redis_db.list_get(t_lobby_topics_list.format(self.title))]
        self.players = [Player(name) for name in redis_db.list_get(t_lobby_players_list.format(self.title))]
        self.questions = [Question(id) for id in redis_db.list_get(t_lobby_questions_list.format(self.title))] if self.status == t_status_started else None

    def setStatus(self, status):
        self.status = status
        redis_db.set(t_lobby_status.format(self.title), status)

    def setTopics(self, topics):
        for title in topics:
            self.topics.append(Topic(title))
            redis_db.list_push(t_lobby_topics_list.format(self.title), title)

    def registratePlayer(self, player: Player):
        player.registrate(self.title)
        self.players.append(player)

    def exitPlayer(self, player: Player):
        player.exit()

    def json(self):
        return {
            'title': self.title,
            'topics': [topic.title for topic in self.topics],
            'players': [player.name for player in self.players],
            'status': self.status,
        }
    
    def start(self):
        if self.status == t_status_started:
            raise Exception(f'Lobby {self.title} already started')
        self.setStatus(t_status_started)
        self.generateQuestions()

    def next(self):
        if not self.questions:
            self.end()
            return
        
        self.questions.pop(0)
        redis_db.list_pop(t_lobby_questions_list.format(self.title))
        

    def end(self):
        for player in self.players:
            player.exit()
        
        redis_db.delete(t_lobby_status.format(self.title))
        redis_db.delete(t_lobby_players_list.format(self.title))
        redis_db.delete(t_lobby_topics_list.format(self.title))
        redis_db.delete(t_lobby_questions_list.format(self.title))
        redis_db.list_rem(t_lobbies_list, self.title)

    def generateQuestions(self, amount_questions = 4):
        
        amounts = createIndexMassive(amount_questions, len(self.topics))
        
        questions_list = []
        for idx, topic in enumerate(self.topics):
            questions_list += topic.getQuestions(self, amounts[idx])
            
        random.shuffle(questions_list)

        for question in questions_list:
            redis_db.list_push(t_lobby_questions_list.format(self.title), question.id)
        
        questions_list.reverse()
        self.questions = questions_list        
    
    @staticmethod
    def existed_lobbies():
        return redis_db.list_get(t_lobbies_list)

    @classmethod
    def isExisted(cls, title):
        return title in cls.existed_lobbies()
    
    @classmethod
    def create(cls, creator_name, title, topics):
        creator = Player(creator_name)
        if cls.isExisted(title):
            raise Exception(f'This lobby with title {title} already exists')
        if creator.isActive():
            raise Exception('Creator is active already')
        redis_db.list_push(t_lobbies_list, title)
        lobby = cls(title)
        lobby.registratePlayer(creator)
        lobby.setTopics(topics)
        lobby.setStatus(t_status_load)
        return lobby
    
    @staticmethod
    def getLobbiesList():
        lobbies_list = redis_db.list_get(t_lobbies_list)
        return lobbies_list if lobbies_list else []
    
    @classmethod
    def getLoadLobbiesList(cls):
        lobbies = cls.getLobbiesList()
        lobbies = [cls(lobby_title) for lobby_title in lobbies]
        lobbies = list(filter(lambda lobby: lobby.status == t_status_load, lobbies))
        return [lobby.json() for lobby in lobbies]