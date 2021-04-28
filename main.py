# импортируем библиотек
from flask import Flask, request
import logging
import os

import json

app = Flask(__name__)

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

sessionStorage = {}

animals = [('слон', 'слона'), ('кролик', 'кролика')]
suggests = [
    "Не хочу.",
    "Не буду.",
    "Отстань!"]


# Если понадобится, то вот моё приложение на хероку для теста
# https://test-alice-yl.herokuapp.com/post
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

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': suggests[:]}

        animal = sessionStorage[user_id]['animal'] = animals[0]
        res['response']['text'] = f'Привет! Купи {animal[1]}!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    animal = sessionStorage[user_id].get('animal', animals[0])
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:
        # Пользователь согласился, прощаемся.
        msg = f'{animal[1].capitalize()} можно найти на Яндекс.Маркете!'

        if animal == animals[0]:
            animal = sessionStorage[user_id]['animal'] = animals[1]
            msg += f' А теперь купите {animal[1]}!'
            sessionStorage[user_id]['suggests'] = suggests[:]
            res['response']['buttons'] = get_suggests(user_id)

        elif animal == animals[1]:
            res['response']['end_session'] = True

        res['response']['text'] = msg
        return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {animal[1]}!"
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
            "url": f"https://market.yandex.ru/search?text={sessionStorage[user_id]['animal'][0]}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
