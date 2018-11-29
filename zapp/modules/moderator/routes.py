from flask import Blueprint, session, render_template, redirect, request, url_for
from zapp import mongo, essents

moderatorapp = Blueprint('moderator', __name__, url_prefix='/moderator', template_folder='moderator-templates')


@moderatorapp.before_request
def check_session():
    try:
        if not session['logged-in']:
            return render_template('login.html', notlgin=True)
    except KeyError:
        return render_template('login.html', notlgin=True)

    if not essents.check_role('moderator', session['role']):
        return redirect('/' + session['role'])


@moderatorapp.route('/')
@moderatorapp.route('/applications', methods=['GET'])
@moderatorapp.route('/applications/filter', methods=['GET'])
def dashboard():
    criteria = request.args.get('criteria', default='all')
    applications = mongo.db.applications
    if criteria == 'not-graded':
        apps = applications.find({'assigned-to': session['user'], 'is-graded': 'Ne'})
    else:
        apps = applications.find({'assigned-to': session['user']})
    ret = list(apps)
    grpref = session['preferences-grade']
    if grpref in ['paper', 'online']:
        gradingform = False
    else:
        gradingform = True

    return render_template('dashboard-m.html', apps=ret, username=session['user'], gradingform=gradingform,
                           gradingtype=grpref)


@moderatorapp.route('/settings')
def settings():
    return render_template('settings-m.html', username=session['user'])


@moderatorapp.route('/settings/grading', methods=['POST'])
def set_grading_type():
    try:
        t = request.form['grading-type']
    except KeyError:
        return redirect('/logout')

    # if t in ['paper, online']:
    if t == 'online' or t == 'paper':
        session['preferences-grade'] = t
        users = mongo.db.users
        users.update_one({'username': session['user']}, {'$set': {'grading': t}})

    return redirect('moderator/applications')


@moderatorapp.route('/applications/grade', methods=['GET', 'POST'])
def grade():
    if not session['preferences-grade'] == 'online':
        return redirect('moderator/settings')

    gradeid = request.args.get('id', default='0')
    if gradeid == '0':
        return redirect('/moderator/applications')

    applications = mongo.db.applications

    if request.method == 'GET':
        valid, applic = essents.test_id(applications, gradeid)
        if not valid:
            return render_template('grade-m.html', app=None, username=session['user'])

        if applic['assigned-to'] == session['user']:
            return render_template('grade-m.html', app=applic, haspermission=True, username=session['user'])
        return render_template('grade-m.html', haspermission=False, username=session['user'])

    if request.method == 'POST':
        # TODO
        pass


@moderatorapp.route('/applications/view', methods=['GET'])
def view_app():
    vid = request.args.get('id', default='0')
    if vid == '0':
        return redirect('/user/applications')

    applications = mongo.db.applications

    valid, applic = essents.test_id(applications, vid)
    if not valid:
        return render_template('view-m.html', app=None, username=session['user'])

    if applic['assigned-to'] == session['user']:
        return render_template('view-m.html', app=applic, haspermission=True, username=session['user'],
                               gradingtype=session['preferences-grade'])
    return render_template('view-m.html', haspermission=False, username=session['user'])
