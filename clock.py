import requests

from settings import WAIT_KEYBOARD
from viberbot.api.messages import TextMessage
from app import  Session, User, viber
import datetime
from settings import TOKEN
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from app import START_KEYBOARD

bot_configuration = BotConfiguration(
    name='EnglishBotLiza',
    avatar='http://viber.com/avatar.jpg',
    auth_token=TOKEN
)
viber = Api(bot_configuration)

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def timed_job():
    session = Session()
    users = session.query(User)
    for u in users:
        if datetime.datetime.utcnow() >= u.time_reminder:
            try:
                viber.send_messages(u.viber_id, [TextMessage(text="Пора повторить слова", keyboard=WAIT_KEYBOARD,
                                                         tracking_data='tracking_data')])
            except:
                print("Пользователь отписался")
                print(u.full_name)
    session.close()

@sched.scheduled_job('interval', minutes=1)
def wake_up():
    r = requests.get('https://viberbotforen.herokuapp.com/')

sched.start()
