from flask import Flask, render_template, request, session, jsonify
from flask_session import Session
from randomWord import randomWord
from score import scorer
import os

app = Flask(__name__)


app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './flask_session/'
Session(app)

with open("wordlist/filtered_oxford_3000.txt", "r") as file:
    word_list = file.read().splitlines()

@app.route('/')
def reset_game():
    session.clear()
    session['target_word'] = randomWord()
    session['rankings'] = generate_rankings(session['target_word'], word_list)
    session['guesses'] = []
    return render_template('index.html')

@app.route('/guess', methods=['POST'])
def guess():
    if 'target_word' not in session:
        return jsonify({'feedback': 'Error: No game found. Refresh to start a new game.', 'correct': False})

    data = request.get_json()
    user_guess = data.get('guess', '').strip().lower()

    
    if user_guess not in word_list:
        return jsonify({'feedback': f"'{user_guess}' is not in the vocabulary. Try a different word.", 'correct': False})

    if scorer(user_guess, session['target_word']):
        feedback = f"🎉 Correct! The word was '{session['target_word']}'."
        session.pop('target_word')
        return jsonify({'feedback': feedback, 'correct': True})

    rankings = session['rankings']
    rank = rankings.get(user_guess, len(rankings) + 1)
    bar_width = max(5, 100 - (rank / len(rankings)) * 95)

    session['guesses'].append((user_guess, rank, bar_width))
    session['guesses'].sort(key=lambda x: x[1])

    return jsonify({
        'feedback': f"Your guess '{user_guess}' is ranked #{rank}.",
        'correct': False,
        'guesses': session['guesses']
    })
@app.route('/hint', methods=['GET'])
def hint():


    rankings = session['rankings']
    sorted_words = sorted(rankings.items(), key=lambda x: x[1])[1:4]

    hints = [{'word': word, 'rank': rank} for word, rank in sorted_words]

    return jsonify({
        'feedback': 'Here are some related words:',
        'hints': hints
    })

@app.route('/giveup', methods=['GET'])
def giveup():
    if 'target_word' not in session:
        return jsonify({
            'feedback': 'you cant give up if you already got the right answer what are u doing',
            'answer': None
        }), 400
    return jsonify({
        'feedback': f"The correct word is '{session['target_word']}'.",
        'answer': session['target_word']
    })

@app.route('/playagain', methods=['POST'])
def play_again():
    session.clear()
    session['target_word'] = randomWord()
    session['rankings'] = generate_rankings(session['target_word'], word_list)
    session['guesses'] = []
    return jsonify({
        'message': 'game reset',
    })

def generate_rankings(target_word, vocab):
    from score import cosine_similarity, model
    rankings = {}
    target_vector = model[target_word]
    for word in vocab:
        try:
            word_vector = model[word]
            similarity = cosine_similarity(target_vector, word_vector)
            rankings[word] = similarity
        except KeyError:
            continue

    sorted_words = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    return {word: rank + 1 for rank, (word, _) in enumerate(sorted_words)}

if __name__ == "__main__":
    app.run(debug=True) #get rid of this if i decide to do anything with this later
