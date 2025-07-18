import json
import pytest

import app

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client

def setup_patches(monkeypatch):
    monkeypatch.setattr(app, 'randomWord', lambda: 'apple')
    monkeypatch.setattr(app, 'generate_rankings', lambda target, vocab: {'apple': 1, 'orange': 2, 'cat': 3})
    monkeypatch.setattr(app, 'scorer', lambda word, target, vocab: word == target)


def test_reset_game(client, monkeypatch):
    setup_patches(monkeypatch)
    response = client.get('/')
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess['target_word'] == 'apple'
        assert sess['guesses'] == []
        assert sess['rankings']['apple'] == 1


def test_valid_guess(client, monkeypatch):
    setup_patches(monkeypatch)
    client.get('/')  # start game
    response = client.post('/guess', json={'guess': 'apple'})
    data = response.get_json()
    assert data['correct'] is True
    assert 'apple' in data['feedback']
    with client.session_transaction() as sess:
        assert 'target_word' not in sess


def test_hint_and_giveup(client, monkeypatch):
    setup_patches(monkeypatch)
    client.get('/')
    hint_resp = client.get('/hint')
    hint_data = hint_resp.get_json()
    assert hint_resp.status_code == 200
    assert hint_data['hints'][0]['word'] == 'orange'
    giveup_resp = client.get('/giveup')
    giveup_data = giveup_resp.get_json()
    assert giveup_resp.status_code == 200
    assert giveup_data['answer'] == 'apple'
