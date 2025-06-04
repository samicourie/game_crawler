from flask import Flask, render_template, json

app = Flask(__name__)

@app.route('/')
def home():
    with open('mini.json', 'r', encoding='utf-8') as f:
        games = json.load(f)
    return render_template('index.html', games=games)


@app.route('/game/<game_title>')
def game_detail(game_title):
    screenshots = ['007 - The World Is Not Enough_Cover.jpg',
                "8Doors - Arum's Afterlife Adventure_Cover.jpg",
                '9 Hours, 9 Persons, 9 Doors_Cover.jpg',
                '9 Monkeys of Shaolin_Cover.jpg',
                '9 Years of Shadows_Cover.jpg',
                '9-Bit Armies - A Bit Too Far_Cover.jpg',
                '10,000 Bullets_Cover.jpg',
                '13 Sentinels - Aegis Rim_Cover.jpg',
                '20XX_Cover.jpg',
                '24 Killers_Cover.jpg',
                '30XX_Cover.jpg']

    with open('mini.json', 'r', encoding='utf-8') as f:
        games = json.load(f)
    game = games.get(game_title)
    organised_game = dict()
    if not game:
        return "Game not found", 404
    game['screenshots'] = screenshots
    return render_template('game_2.html', game=game)

if __name__ == '__main__':
    app.run(debug=True)
