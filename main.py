import random
from flask import Flask, url_for, render_template, redirect, request
from functions import get_description
from flask_sqlalchemy import SQLAlchemy
from settings import settings

app = Flask(__name__)
path = settings()["DATABASE_PATH"]
app.config["SQLALCHEMY_DATABASE_URI"] = path
db = SQLAlchemy(app)

class Words(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String, unique=True, nullable=False)
    desc = db.Column(db.String)
    prac_time = db.Column(db.Integer)
    practice_point = db.Column(db.Integer)
    search_time = db.Column(db.Integer)

class Pratice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)


@app.route("/")
def main():
    return redirect(url_for("login"))

@app.route("/register", methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if (request.form['username'] == "" or request.form['password'] == ""  or request.form['password2'] == "") is True:
            error = 'Fill all the sections.'
        elif request.form['username'] and request.form['password'] == request.form['password2']:
            response = register_user(request.form['username'], request.form['password'])
            if response:
                return redirect(url_for('login'))
            else:
                error = "This user already exist"
        elif request.form['password'] != request.form['password2']:
            error = "Passwords doesn't match"
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST' and request.form["button"] == "Login":
        response = login_check(request.form['username'], request.form['password'])
        if response is not True:
            error = response
        else:
            return redirect(url_for('search'))
    elif request.method == 'POST' and request.form["button"] == "Register":
        return redirect(url_for("register"))
    return render_template('login.html', error=error)

@app.route("/search", methods=['GET', 'POST'])
def search():
    error = None
    if request.method == 'POST':
        if request.form['search']:
            table = Words.query.filter_by(word=request.form['search']).first()
            if table:
                error = "This keyword already added on library."
                search_time = Words.query.filter_by(word=request.form['search']).first().search_time
                prac_word = Words.query.filter_by(word=request.form['search']).update(dict(prac_time=search_time+1))
                db.session.commit()
            else:
                return redirect(url_for("word", word=request.form['search']))

        elif request.form['search'] == "":
            error = "You didn't write anything"
        else:
            return redirect(url_for('search'))
    
    return render_template('search.html', error=error)

@app.route("/word/<word>", methods=['GET', 'POST'])
def word(word):
    error=None
    if request.method == 'POST':
        if request.form["button"] == "add":
            check = count_word(word)
            if check:
                error = "This word already added."
            else:
                word = Words(
                    word=word.upper(),
                    desc=get_description(word),
                    prac_time=0,
                    practice_point=0,
                    search_time=1,
                )
                db.session.add(word)
                db.session.commit()
                return redirect(url_for('search'))

        elif request.form["button"] == "back":
            return redirect(url_for('search'))

    description = get_description(word)
    return render_template('words.html', error=error, word_name=word.upper(), description=description.capitalize())

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    error = None
    table = Words.query.all()
    if request.method == 'POST':
        if request.form["button"] == "practice":
            if len(table) <10:
                error="To practice you should add at least 10 Word to your library."
                return render_template('dashboard.html',error=error, table=table)
            return redirect(url_for("practice"))
    return render_template('dashboard.html',error=error, table=table)


@app.route("/practice", methods=['GET', 'POST'])
def practice():
    error= None
    table = Words.query.all()
    first_desc = get_rand_desc(table[0].desc)
    firt_word = table[0].word.upper()

    if request.method == 'POST':
        table = Words.query.all()
        number = Pratice.query.filter_by(id=1).first().number
        next_number = number+1

        prac = Pratice.query.filter_by(id=1).update(dict(number=number+1))
        db.session.commit()
        if next_number == len(table)-1:
            return render_template('dashboard.html', table=table) 
        else:
            if request.form["button"] == table[number].desc or request.form["button"] == table[0].desc:
                desc = get_rand_desc(table[next_number].desc)
                word = table[next_number].word.upper()
                add_practice_time(word)
                add_point(word)
                return render_template('practice.html', word=word, desc=desc) 

            elif request.form["button"] == table[number].desc or request.form["button"] == table[0].desc:
                number = Pratice.query.filter_by(id=1).first().number
                desc = get_rand_desc(table[next_number].desc)
                word = table[next_number].word.upper()
                add_practice_time(word)
                add_point(word)
                return render_template('practice.html', word=word, desc=desc)

            elif request.form["button"] == table[number].desc or request.form["button"] == table[0].desc:
                number = Pratice.query.filter_by(id=1).first().number
                desc = get_rand_desc(table[next_number].desc)
                word = table[next_number].word.upper()
                add_practice_time(word)
                add_point(word)
                return render_template('practice.html', word=word, desc=desc)

            elif request.form["button"] == "end":
                return redirect(url_for('dashboard'))

            else:
                desc = get_rand_desc(table[number].desc)
                word = table[number].word.upper()
                add_practice_time(word)
                delete_point(word)
                error = "Wrong Choise. Try Again !"
                return render_template('practice.html',error=error, word=word, desc=desc)

    prac = Pratice.query.filter_by(id=1).first()
    if prac == None:
        prac=Pratice(
            number=0
        )
        db.session.add(prac)
        db.session.commit()
    else:
        prac = Pratice.query.filter_by(id=1).update(dict(number=0))
        db.session.commit()
        
    return render_template('practice.html',error=error, word=firt_word, desc=first_desc)


def count_word(word):
    word = Words.query.filter_by(word=word).first()
    if word:
        return True
    return False

def add_point(word):
    point = Words.query.filter_by(word=word).first().practice_point
    prac = Words.query.filter_by(word=word).update(dict(practice_point=point+1))
    db.session.commit()

def delete_point(word):
    point = Words.query.filter_by(word=word).first().practice_point
    prac = Words.query.filter_by(word=word).update(dict(practice_point=point-1))
    db.session.commit()

def add_practice_time(word):
    prac_time = Words.query.filter_by(word=word).first().prac_time
    prac_word = Words.query.filter_by(word=word).update(dict(prac_time=prac_time+1))
    db.session.commit()

def check_answer(word):
    table = Words.query.filter_by(word).first()
    return table.desc

def get_rand_desc(word_desc):
    table = Words.query.all()
    word_id = (Words.query.filter_by(desc=word_desc).first().id)-1
    number_list = [*range(0,len(table)-1)]
    number_list.pop(word_id)

    f_num, sec_num = random.sample(number_list,2)
    desc = [table[f_num].desc, table[sec_num].desc, word_desc]
    random.shuffle(desc)
    return desc

def login_check(username, password):
    login = User.query.filter_by(username=username).first()
    if login is None:
        return "User couldn't found."
    else:
        if login.password == password:
            return True
        else:
            return "Username or password wrong !!"

def register_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        create_user = User(username=username, password=password)
        db.session.add(create_user)
        db.session.commit()
        return True
    else:
        return "This user already exist"