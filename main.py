from requests import get
from flask import Flask, request
import os
import logging
import json
from deep_translator import GoogleTranslator


LANGUAGE = 'en'

app = Flask(__name__)

sessionStorage = {}


def translate(word):
    # p = {'key': 'trnsl.1.1.20190115T093726Z.65e1460d8d95bd06.р45ор345о3р4о53р45о345р3о',
    #      'lang': LANGUAGE, 'text': word}
    #
    # response = get('https://translate.yandex.net/api/v1.5/tr.json/translate', params=p)
    # print(response.status_code)
    # if not response.__bool__():
    #     return
    # trans_text = response.json()['text'][0]
    try:
        trans = GoogleTranslator(source='auto', target=LANGUAGE)
        text = trans.translate(word)
        return text
    except Exception:
        return


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False,
            'buttons': [{'title': 'Помощь', 'hide': True}]
        }
    }

    handle_dialog(response, request.json)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {}
        return

    if sessionStorage[user_id].get('first_name') is None:
        name = get_first_name(req)
        if name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
            return

        sessionStorage[user_id]['first_name'] = name
        res['response']['text'] = f'Приятно познакомиться, {name.title()}. ' \
                                  f'Я Алиса. Я умею постараюсь перевести заданный вами ' \
                                  f'текст с любого языка на английский! ' \
                                  f'В этом тебе поможет команда:\n\n' \
                                  f'\nПереведи предложение [предложение]\n\n\nПросто ' \
                                  f'отправь эту команду мне!'
        return

    if req['request']['original_utterance'].lower() in ['помощь', 'помоги', 'help', 'помогите']:
        res['response']['text'] = 'Чтобы перевести текст введите команду:\n\n\n' \
                                  'Переведи предложение [предложение]'
        return

    tokens = req['request']['nlu']['tokens']
    if len(tokens) >= 3 and tokens[:2] == ['переведи', 'предложение']:
        text = translate(' '.join(tokens[2:]))
        if text is None:
            res['response']['text'] = 'При переводе произошла непредвиденная ошибка! ' \
                                      'Повторите ввод.'
            return
        res['response']['text'] = text

    else:
        res['response']['text'] = f'{sessionStorage[user_id]["first_name"].title()}, ' \
                                  f'я не понимаю ' \
                                  f'вас! Можете использовать помощь, чтобы узнать ' \
                                  f'корректную команду перевода. Повторите ввод!'


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)