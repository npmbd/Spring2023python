import time
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, request, abort
import random
import requests

app = Flask(__name__)

db = [
    {
        'time': time.time(),
        'name': 'Bot',
        'text': 'Привет! Меня зовут Bot, я могу предложить тебе случайный фильм из подборки "IMDb Top 250". Введи "/movie" в сообщении, чтобы я нашел фильм.',
    },
]

@app.route("/")
def hello():
    return "Hello world!"


@app.route("/send", methods=['POST'])
def send_message():
    data = request.json

    if not isinstance(data, dict):
        return abort(400)

    if 'name' not in data or 'text' not in data:
        return abort(400)
    if len(data) != 2:
        return abort(400)

    name = data['name']
    text = data['text']

    if not isinstance(name, str) or not isinstance(text, str) or name == '' or text == '':
        return abort(400)

    if text == '/movie':
        page = requests.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250')
        IMDb_url = 'https://www.imdb.com'
        soup = BeautifulSoup(page.text, "html.parser")
        movies = soup.find_all('tr')
        random_number = random.randint(1, 250)
        choosen_movie = movies[random_number]
        link_to_movie = IMDb_url + choosen_movie.find_all('a')[1]['href']
        answer = ('Фильм: ' + choosen_movie.find_all('a')[1].text + '\n' +
                  'Рейтинг IMDb: ' + choosen_movie.strong.text + '\n' +
                  'Подробнее о фильме: ' + link_to_movie)
        message = {
            'time': time.time(),
            'name': 'Bot',
            'text': answer,
        }
    else:
        message = {
            'time': time.time(),
            'name': name,
            'text': text,
        }
    db.append(message)
    return {'ok': True}


@app.route("/messages")
def get_messages():
    try:
        after = float(request.args['after'])
    except:
        return abort(400)

    result = []
    for message in db:
        if message['time'] > after:
            result.append(message)
            if len(result) >= 100:
                break

    return {'messages': result}


@app.route("/status")
def status():
    users = []
    for message in db:
        if message['name'] not in users:
            users.append(message['name'])
    return {
        'name': 'Messenger',
        'status': True,
        'time': datetime.now().strftime("%H:%M"),
        'Number of messages': len(db),
        'Number of users': len(users),
        'Users': users
    }

app.run()
