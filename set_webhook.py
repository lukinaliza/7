from settings import TOKEN, WEBHOOK
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

bot_configuration = BotConfiguration(
	name='EnglishBotLiza',
	avatar='http://viber.com/avatar.jpg',
	auth_token=TOKEN
)
viber = Api(bot_configuration)
print('setting webhook')
viber.set_webhook(WEBHOOK)
# viber.set_webhook("https://7d02005a.ngrok.io/incoming")