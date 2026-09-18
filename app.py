import os
import random

from flask import Flask, jsonify, render_template, request, session
from flask_session import Session

from score import generate_rankings

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_FILE_DIR"] = "./flask_session/"
Session(app)

with open("wordlist/filtered_oxford_3000.txt") as file:
    word_list = file.read().splitlines()


def start_game():
    session.clear()
    session["target_word"] = random.choice(word_list)
    session["rankings"] = generate_rankings(session["target_word"], word_list)
    session["guesses"] = []


@app.route("/")
def home():
    start_game()
    return render_template("index.html")


@app.route("/guess", methods=["POST"])
def guess():
    if "target_word" not in session:
        return jsonify({"feedback": "no game going. refresh and try again.", "correct": False})

    user_guess = (request.get_json() or {}).get("guess", "").strip().lower()
    if user_guess not in word_list:
        return jsonify({
            "feedback": f"“{user_guess}” isn’t in the word list. try another.",
            "correct": False,
        })

    if user_guess == session["target_word"]:
        session.pop("target_word")
        return jsonify({
            "feedback": f"you got it — the word was “{user_guess}”.",
            "correct": True,
        })

    rankings = session["rankings"]
    rank = rankings.get(user_guess, len(rankings) + 1)
    closeness = max(5, 100 - (rank / len(rankings)) * 95)
    session["guesses"].append({"word": user_guess, "rank": rank, "bar": closeness})
    session["guesses"].sort(key=lambda item: item["rank"])

    return jsonify({
        "feedback": f"“{user_guess}” is #{rank}.",
        "correct": False,
        "guesses": session["guesses"],
    })


@app.route("/hint")
def hint():
    closest = sorted(session["rankings"].items(), key=lambda item: item[1])[1:4]
    return jsonify({"hints": [word for word, _ in closest]})


@app.route("/giveup")
def giveup():
    target = session.get("target_word")
    if not target:
        return jsonify({"answer": "there’s no word to give up on."})
    return jsonify({"answer": f"the word was “{target}”."})


@app.route("/playagain", methods=["POST"])
def play_again():
    start_game()
    return jsonify({"message": "new word. good luck."})


if __name__ == "__main__":
    app.run(debug=True)
