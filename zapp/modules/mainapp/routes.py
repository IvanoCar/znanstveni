from flask import Blueprint, render_template, request, session, redirect
from zapp import mongo

mainapp = Blueprint('main', __name__, template_folder='main-templates')



@mainapp.route('/', methods=['GET'])
@mainapp.route('/login', methods=['POST'])
def login():
    if request.method == 'GET':
        try:
            if not session['logged-in']:
                return render_template('login.html')
            else:
                return redirect('/' + session['role'])
        except KeyError:
            return render_template('login.html')

    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'username': request.form['username'],
                               'password': request.form['password'],
                               'role': request.form['role']}, {'_id': 0})

        if user is None:
            return render_template('login.html', error=True)

        session.permanent = True
        session['user'] = request.form['username']
        session['role'] = request.form['role']
        session['logged-in'] = True
        if request.form['role'] == 'moderator':
            session['preferences-grade'] = user['grading']
        return redirect('/' + request.form['role'])


@mainapp.route('/logout')
def logout():
    try:
        if session['logged-in'] is True:
            session.clear()
            return render_template('login.html', logout=True)
        else:
            return render_template('login.html')
    except KeyError:
        return render_template('login.html')
