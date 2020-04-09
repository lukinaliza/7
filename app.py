from flask import Flask, request, Response, render_template, make_response
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.pool import NullPool

from settings import TOKEN, WEBHOOK
from settings import HELLO_MESSAGE
from viberbot import Api
from settings import SAMPLE_KEYBOARD, START_KEYBOARD
from viberbot.api.messages import TextMessage, KeyboardMessage
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberMessageRequest, ViberConversationStartedRequest
import random
import copy
import json
import sqlite3
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from collections import deque

bot_configuration = BotConfiguration(
	name='EnglishBotLiza',
	avatar='http://viber.com/avatar.jpg',
	auth_token=TOKEN
)
viber = Api(bot_configuration)
app = Flask(__name__)

# engine = create_engine(
#    'postgres://qnakjltyvuqpku:c5f08f5f6d9e839f3a50bb0b84a48a646fed55c9c7709c0a05df1937e6f42703@ec2-54-247-79-178.eu-west-1.compute.amazonaws.com:5432/d7dbjfelqdi0jl', poolclass=NullPool, echo=False)
engine = create_engine('sqlite:///test00.db', poolclass=NullPool, echo = False)
Base = declarative_base()

class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    examples = Column(String, nullable=False)

    var = relationship('User', back_populates = 'curword')

    def __repr__(self):
        return f'{self.id}. {self.word}: {self.translation} [{self.examples}]'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    full_name = Column(String, nullable=False, default='John Doe')
    viber_id = Column(String, nullable=False, unique=True)
    # currentword_id = Column(Integer, nullable=True)
    currentword_id = Column(Integer, ForeignKey('words.id'), nullable=True)
    correct_answers_session = Column(Integer, nullable=False, default=0)
    questionCount_session = Column(Integer, nullable=False, default=0)
    last_answer_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    time_reminder = Column(DateTime)

    words = relationship('Learning', back_populates='user')
    curword = relationship('Word', back_populates = 'var')

    def __repr__(self):
        return f'{self.id}: {self.full_name} [{self.viber_id}]'

class Learning(Base):
    __tablename__ = 'learning'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    word = Column(Integer, nullable=False)
    right_answers = Column(Integer, nullable=False, default=0)
    last_time_answer_word = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    user = relationship('User', back_populates='words')

    def __repr__(self):
        return f'{self.id}: {self.user_id} [{self.word} / {self.right_answers}] {self.last_time_answer_word}'

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    deltatime_reminder = Column(Integer, nullable=False, default=30)
    session_words = Column(Integer, nullable=False, default=10)
    rightanswers_tolearnt = Column(Integer, nullable=False, default=20)

class TokenHolder():

    def __init__(self):
        self.q = deque()

    def add(self, token):
        self.q.append(token)

    def pop(self):
        self.q.popleft()

    def clear(self, num):
        i = 0
        while i < num:
            self.q.popleft()
            i+=1

    def isIn(self, token):
        if token in self.q:
            return True
        return False

    def __len__(self):
        return self.q.__len__()

    def __repr__(self):
        for t in self.q:
            print(t)


Session = sessionmaker(engine)

def initWords():
    session = Session()
    query = session.query(Word)
    if query.all().__len__() < 1:
        with open('english_words.json', encoding='utf-8') as f:
            english_words = json.load(f)
        for word in english_words:
            new_word = Word(word=word['word'], translation=word['translation'], examples = " ".join(word['examples']))
            session.add(new_word)
    session.commit()
    session.close()


def get_four_words_for_user(user_id):
    session = Session()
    set = session.query(Settings).first()
    list = []
    dictSize = session.query(Word).all().__len__()
    while list.__len__() < 4:
        r = random.randint(1, dictSize)
        word = session.query(Word).filter(Word.id == r).first()
        check = session.query(Learning).filter(Learning.user_id == user_id).filter(Learning.word == word.id).first()
        if ((check == None or check.right_answers < set.rightanswers_tolearnt) and word not in list):
            list.append(word)
    session.close()
    return list

def makeQuestion(viber_request_sender_id, portion_words):
    print("make question")
    print(portion_words)
    session = Session()
    # заполнение клавиатуры
    user = session.query(User).filter(User.viber_id == viber_request_sender_id).first()
    curWord = portion_words[0]
    user.currentword_id = curWord.id
    user.last_answer_time = datetime.datetime.utcnow()
    session.commit()

    whichWordMessage = f'Вопрос №{user.questionCount_session + 1}. Как переводится слово: {curWord.word}'
    temp = copy.copy(portion_words)
    random.shuffle(temp)
    for button, w in zip(SAMPLE_KEYBOARD["Buttons"], temp):
        temp_question = {'question_number': f'{user.questionCount_session}',
                         'answer': f"{w.translation}"}
        button["Text"] = w.translation
        button["ActionBody"] = f'{[user.questionCount_session, w.translation]}'
    messageKeyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=SAMPLE_KEYBOARD)
    viber.send_messages(viber_request_sender_id, [
        TextMessage(text=whichWordMessage), messageKeyboard
    ])
    session.close()

def getStat(viber_id):
    session = Session()
    statistics = ""
    user = session.query(User).filter(User.viber_id == viber_id).first()
    wds_learnt = session.query(Learning).filter(Learning.user_id == user.id).filter(Learning.right_answers >=20).all().__len__()
    words_learning = session.query(Learning).filter(Learning.user_id == user.id).all().__len__() - wds_learnt
    statistics += "КВы выучили " + str(wds_learnt) + "слов \n"
    #statistics += "Количество слов на изучении: " + str(words_learning) + "\n"
    statistics += "Время последнего посещения: " + str(user.last_answer_time).replace('-', '.')[:19]
    session.close()
    return statistics

def showExample(viber_id):
    session = Session()
    val = (session.query(Word).join(User).filter(User.viber_id == viber_id)).first().examples
    val=val.split(". ")
    number = random.choice(range(len(val)))
    user = session.query(User).filter(User.viber_id == viber_id).first()
    session.close()
    print('showExample inner')
    temp = copy.copy(portion_words)
    random.shuffle(temp)
    for button, w in zip(SAMPLE_KEYBOARD["Buttons"], temp):
        temp_question = {'question_number': f'{user.questionCount_session}',
                         'answer': f"{w.translation}"}
        button["Text"] = w.translation
        button["ActionBody"] = f'{[user.questionCount_session, w.translation]}'
    messageKeyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=SAMPLE_KEYBOARD)
    viber.send_messages(viber_id, [
        TextMessage(text=val[number]), messageKeyboard
    ])

def checkAnswer(viber_id, text):
    print('checking answer')
    text = eval(text)
    print(text)
    session = Session()
    user = session.query(User).filter(User.viber_id == viber_id).first()
    if text[0] == user.questionCount_session:
        if text[1] == (session.query(Word).join(User).filter(Word.id == user.currentword_id)).first().translation:
            # обновление слова в таблице learning
            str = session.query(Learning).filter(Learning.user_id == user.id) \
                .filter(Learning.word == user.currentword_id).first()
            if (str != None):
                str.last_time_answer_word = datetime.datetime.utcnow()
                str.right_answers += 1
                session.commit()
            else:
                user.words.append(Learning(word=user.currentword_id, right_answers=1))
                session.commit()
            user.correct_answers_session += 1
            session.commit()
            viber.send_messages(viber_id, [TextMessage(text=f"Вопрос №{user.questionCount_session + 1}. Ответ [{text[1]}] верный :)")])
        else:
            viber.send_messages(viber_id, [TextMessage(text=f"Вопрос №{user.questionCount_session + 1}. Ответ [{text[1]}] неверный :(")])
        user.questionCount_session += 1
        # обновление последнего времени ответа
        user.last_answer_time = datetime.datetime.utcnow()
        session.commit()
        session.close()
        return True
    session.close()
    return False

def checkEndSession(viber_id):
    session = Session()
    user = session.query(User).filter(User.viber_id == viber_id).first()
    set = session.query(Settings).first()
    if user.questionCount_session >= set.session_words:
        final = TextMessage(text=f"Вы верно ответили на {user.correct_answers_session} из {set.session_words} Сыграем снова?! ЖМИ НА СТАРТ")
        viber.send_messages(viber_id, [final])
        user.correct_answers_session = 0
        user.questionCount_session = 0
        session.commit()
        session.close()
        return True
    session.close()
    return False

def initSettings():
    session = Session()
    set = session.query(Settings).first()
    if set == None:
        s = Settings()
        session.add(s)
        session.commit()


@app.route("/")
def hello():
    return render_template('hello.html')

@app.route("/settings")
def settings():
    session = Session()
    set = session.query(Settings).first()
    if set == None:
        initSettings()
    session.close()
    return render_template('settings.html', deltatime_reminder = set.deltatime_reminder, session_words = set.session_words, rightanswers_tolearnt = set.rightanswers_tolearnt)

@app.route('/set_settings', methods = [ 'GET'] )
def set_settings():
    session = Session()
    set = session.query(Settings).first()
    if set == None:
        initSettings()
    set.deltatime_reminder = int(request.args.get('deltatime_reminder'))
    set.session_words = int(request.args.get('session_words'))
    set.rightanswers_tolearnt = int(request.args.get('rightanswers_tolearnt'))
    session.commit()
    session.close()
    string = render_template('successful.html')
    response = make_response(string)
    return response

# Base.metadata.create_all(engine)

portion_words = []
mes_token = TokenHolder()
init = False
@app.route('/incoming', methods = ['POST'])
def incoming():
    Base.metadata.create_all(engine)
    global init
    if (init == False):
        initWords()
        initSettings()
        init = True
    global portion_words
    viber_request = viber.parse_request(request.get_data())


    if isinstance(viber_request, ViberConversationStartedRequest):
        session = Session()
        if (session.query(User).filter(User.viber_id == viber_request.user.id).first() == None):
            user_0 = User(full_name=viber_request.user.name, viber_id=viber_request.user.id)
            session.add(user_0)
            session.commit()
        user = session.query(User).filter(User.viber_id == viber_request.user.id).first()
        time=str(user.last_answer_time).replace('-', '.')[:19]
        wds_learnt = session.query(Learning).filter(Learning.user_id == user.id).filter(
            Learning.right_answers >= 20).all().__len__()
        viber.send_messages(viber_request.user.id, [
            TextMessage(text = " Привет! это бот предназначенный для изучения английских слов! \n" \
               f'Нажмите старт чтобы начать:).\n' \
               f'Вы выучили {wds_learnt} слов \n' \
               f'Время последнего посещения: {time} '
  , keyboard=START_KEYBOARD, tracking_data='tracking_data')
        ])

    elif isinstance(viber_request, ViberMessageRequest):
        if not mes_token.isIn(viber_request.message_token):
            mes_token.add(viber_request.message_token)
            mes_token.__repr__()
            if mes_token.__len__() > 10000:
                mes_token.clear(100)
            message = viber_request.message
            session = Session()
            user = session.query(User).filter(User.viber_id == viber_request.sender.id).first()
            set = session.query(Settings).first()
            if isinstance(message, TextMessage):
                text = message.text
                print(text)
                if text == "Start":
                    #stat = getStat(viber_request.sender.id)
                    user.time_reminder = datetime.datetime.utcnow() + datetime.timedelta(minutes=set.deltatime_reminder)
                    session.commit()
                    # viber.send_messages(viber_request.sender.id, [TextMessage(text=stat)])
                    print("getting 4 words in the Start")
                    portion_words = get_four_words_for_user(user.id)
                    # заполнение клавиатуры
                    makeQuestion(viber_request.sender.id, portion_words)
                elif text == "showExample":
                    print("!")
                    showExample(viber_request.sender.id)
                elif text == "Dismiss":
                    user.time_reminder = datetime.datetime.utcnow() + datetime.timedelta(minutes=set.deltatime_reminder)
                    session.commit()
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text=f"Жду тебя! Нажми на Start как будешь готов"), KeyboardMessage(tracking_data='tracking_data', keyboard=START_KEYBOARD) ])
                else:
                    # проверка на правильность ответа
                    if checkAnswer(viber_request.sender.id, text):
                        if (checkEndSession(viber_request.sender.id)):
                            willContinue = TextMessage(text=f"Сыграем ещё раз?")
                            messageKeyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=START_KEYBOARD)
                            viber.send_messages(viber_request.sender.id, [willContinue, messageKeyboard])
                        else:
                            print("getting 4 words in the end")
                            portion_words = get_four_words_for_user(user.id)
                            # заполнение клавиатуры
                            makeQuestion(viber_request.sender.id, portion_words)
            session.close()
    return Response(status=200)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port = 82)
