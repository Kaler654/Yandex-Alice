# импортируем библиотеки
from flask import Flask, request
import logging
import os
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}

items = ['слона', 'кролика', 'утку']


def get_next_item(user_id):
    n = items.index(sessionStorage[user_id]['item'])
    if n != -1:
        return items[n + 1]


@app.route('/')
def hello():
    return "Hello, world!"


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!"
            ],
            'item': 'слона'
        }
        res['response']['text'] = f'Привет! Купи {sessionStorage[user_id]["item"]}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я куплю',
        'я покупаю'
    ]:
        item = get_next_item(user_id)
        if item is not None:
            sessionStorage[user_id]['item'] = item
            res['response'][
                'text'] = f'{sessionStorage[user_id]["item"].capitalize()}' \
                          f' можно найти на Яндекс.Маркете! Не хотите ли купить {sessionStorage[user_id]["item"]}?'
        else:
            res['response'][
                'text'] = f'{sessionStorage[user_id]["item"].capitalize()}' \
                          f' можно найти на Яндекс.Маркете!'
        return res

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {sessionStorage[user_id]['item']}!"
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    # app.run()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
