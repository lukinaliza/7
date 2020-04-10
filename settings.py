TOKEN = "4b246c8a6927de86-51622645a10d620d-b70717213e5fefa5"
URL = "https://viberbotforen.herokuapp.com/"
# URL = "https://605e2f1b.ngrok.io"
WEBHOOK = URL + '/incoming'
HELLO_MESSAGE = "Привет! Я Бот из Англии в седьмом поколении. Я помогу тебе выучить английский язык. "\
               "Для начала введи Start или нажми на кнопку внизу"

START_KEYBOARD = {
"Type": "keyboard",
"Buttons": [
	{
	"Columns": 6,
	"Rows": 1,
	"BgColor": "#e6f5ff",
	"BgMedia": "http://link.to.button.image",
	"BgMediaType": "picture",
	"BgLoop": True,
	"ActionType": "reply",
	"ActionBody": "Start",
	"ReplyType": "message",
	"Text": "Старт"
	}
    ]
}

WAIT_KEYBOARD = {
"Type": "keyboard",
"Buttons": [
	{
	"Columns": 6,
	"Rows": 1,
	"BgColor": "#e6f5ff",
	"BgMedia": "http://link.to.button.image",
	"BgMediaType": "picture",
	"BgLoop": True,
	"ActionType": "reply",
	"ActionBody": "Start",
	"ReplyType": "message",
	"Text": "Старт"
	},
    {"Columns": 6,
    "Rows": 1,
    "BgColor": "#e6f5ff",
    "BgMedia": "http://link.to.button.image",
    "BgMediaType": "picture",
    "BgLoop": True,
    "ActionType": "reply",
    "ActionBody": "Dismiss",
    "ReplyType": "message",
    "Text": "Напомнить позже"
    }
    ]
}

SAMPLE_KEYBOARD = {
"Type": "keyboard",
"Buttons": [
	{
	"Columns": 3,
	"Rows": 1,
	"BgColor": "#e6f5ff",
	"BgMedia": "http://link.to.button.image",
	"BgMediaType": "picture",
	"BgLoop": True,
	"ActionType": "reply",
	"ActionBody": "But1",
	"ReplyType": "message",
	"Text": "Push me!"
	},
    {
        "Columns": 3,
        "Rows": 1,
        "BgColor": "#e6f5ff",
        "BgMedia": "http://link.to.button.image",
        "BgMediaType": "picture",
        "BgLoop": True,
        "ActionType": "reply",
        "ActionBody": "But2",
        "ReplyType": "message",
        "Text": "Push me too!"
    },
    {
        "Columns": 3,
        "Rows": 1,
        "BgColor": "#e6f5ff",
        "BgMedia": "http://link.to.button.image",
        "BgMediaType": "picture",
        "BgLoop": True,
        "ActionType": "reply",
        "ActionBody": "But3",
        "ReplyType": "message",
        "Text": "Push me 3!"
    },
    {
        "Columns": 3,
        "Rows": 1,
        "BgColor": "#e6f5ff",
        "BgMedia": "http://link.to.button.image",
        "BgMediaType": "picture",
        "BgLoop": True,
        "ActionType": "reply",
        "ActionBody": "But4",
        "ReplyType": "message",
        "Text": "Push me 4!"
    },
    {
        "Columns": 6,
        "Rows": 1,
        "BgColor": "#e6f5ff",
        "BgMedia": "http://link.to.button.image",
        "BgMediaType": "picture",
        "BgLoop": True,
        "ActionType": "reply",
        "ActionBody": "showExample",
        "ReplyType": "message",
        "Text": "Пример использования"
    }
    ]
}
