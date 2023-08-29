from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_required, login_user, UserMixin
from wtforms import Form, StringField, PasswordField, validators
from  system.fetch import MTGCards
from passlib.hash import bcrypt
from tinydb import TinyDB, Query
from env_ import SECRET_KEY
from json import dumps

app = Flask(__name__)
app.secret_key = SECRET_KEY
db = TinyDB('database/_users.json')
User_db = Query()
fetcher = MTGCards()
login_manager = LoginManager(app=app)
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    user_doc = db.get(doc_id=int(user_id))
    if user_doc:
        return User(user_id)
    return None


def hash_password(password:str) -> str:
    return bcrypt.hash(password)

def verify_password(password:str, hashed:str) -> bool:
    return bcrypt.verify(password, hashed)

def card_register(card, user_id:int) -> None:
    user = db.get(doc_id=user_id)
    user['all_cards'].append(card)# type: ignore
    db.update(user, doc_ids=[user_id]) # type: ignore

def search_card(card_name:str) -> dict:
        cards_results:list[dict] = fetcher.fetch_many_by_name(card_name)
        return cards_results # type: ignore

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='As senhas devem ser iguais')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        user_exists = db.get(User_db.name == username)
        if user_exists:
            return "O usuário já existe"
        
        hashed_password = hash_password(password)
        
        user_data = {
            'name': username,
            'password': hashed_password,
            'decks': [],
            'all_cards': []
        }

        db.insert(user_data)
        
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST']) # type: ignore
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get(User_db.name == username)
        user_obj = User(user.doc_id) # type: ignore
        login_user(user_obj)
        
        if user and verify_password(password, user['password']): # type: ignore
            session['user_id'] = user.doc_id # type: ignore
            return redirect(url_for('dashboard'))
        else:
            return "Usuário ou senha incorretos"
        
    
    return render_template('login.html')

@app.route('/dashboard') # type: ignore
@login_required
def dashboard():
    user_id = session.get('user_id')
    if user_id is not None:
        user = db.get(doc_id=int(user_id))
        return render_template('dashboard.html', user=user)
    
    return redirect(url_for('login'))

@app.route('/dashboard/decks') # type: ignore
@login_required
def decks():
    user_id = session.get('user_id')
    if user_id is not None:
        user = db.get(doc_id=int(user_id))
        return render_template('decks.html', user=user)
    
    return redirect(url_for('login'))

@app.route('/dashboard/mycards') # type: ignore
@login_required
def mycards():
    user_id = session.get('user_id')
    if user_id is not None:
        user = db.get(doc_id=int(user_id))
        return render_template('mycards.html', user=user)
    
    return redirect(url_for('login'))

@app.route('/dashboard/search', methods=['GET', 'POST']) # type: ignore
@login_required
def search():
    card_name = request.args.get('card_name')
    if card_name:
        search_results = fetcher.fetch_many_by_name(card_name)
    else:
        search_results = []

    user_id = session.get('user_id')
    if user_id is not None:
        user = db.get(doc_id=int(user_id))
        return render_template('mycards.html', user=user, search_results=search_results)

    return redirect(url_for('login'))

@app.route('/dashboard/add_card', methods=['GET', 'POST']) # type: ignore
@login_required
def add_card():
    if request.method == 'POST':
        card_id = request.form['card_id']
        card_name = request.form['card_name']
        user_id = session.get('user_id')
        print(card_id, card_name)
        card_data = fetcher.fetch_by_id(card_id, card_name)
        
        card_register(card_data, user_id) # type: ignore
        
        return redirect(url_for('mycards'))
    
    return redirect(url_for('search'))

@app.route('/dashboard/delete_card', methods=['POST']) # type: ignore
@login_required
def delete_card():
    user_id = session.get('user_id')
    card_id = request.form['card_id']
    card_name = request.form['card_name']
    if user_id is not None:
        user = db.get(doc_id=int(user_id))
        cards = user.get('all_cards', []) # type: ignore
        for card in cards:
            if card.get('id') == card_id and card.get('name') == card_name:
                cards.remove(card)
                db.update(user, doc_ids=[user_id]) # type: ignore
                break
    return redirect(url_for('mycards'))

@app.route('/logout') # type: ignore
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(port=3030, debug=True)
