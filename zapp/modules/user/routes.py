from flask import Blueprint, request, render_template, redirect, session
from bson.objectid import ObjectId
import bson
from zapp import mongo, essents
from time import gmtime, strftime

userapp = Blueprint('user', __name__, url_prefix='/user', template_folder='user-templates')


@userapp.before_request
def check_session():
    try:
        if not session['logged-in']:
            return render_template('login.html', notlgin=True)
    except KeyError:
        return render_template('login.html', notlgin=True)

    if not essents.check_role('user', session['role']):
        return redirect('/' + session['role'])


@userapp.route('/')
@userapp.route('/applications')
def application_view():
    applications = mongo.db.applications
    apps = applications.find({'aai-email': session['user']})
    ret = list(apps)
    return render_template('dashboard.html', apps=ret, username=session['user'])


@userapp.route('/applications/edit', methods=['GET', 'POST'])
def edit_application():
    edit_id = request.args.get('id', default='0')
    if edit_id == '0':
        return redirect('/user/applications/')

    applications = mongo.db.applications

    if request.method == 'GET':
        valid, aplic = essents.test_id(applications, edit_id)

        if not valid:
            render_template('edit.html', app=None, username=session['user'])

        if aplic['aai-email'] == session['user']:
            return render_template('edit.html', app=aplic, types=essents.applicationTypes, haspermission=True,
                                   username=session['user'])
        return render_template('edit.html', haspermission=False, username=session['user'])

    if request.method == 'POST':
        aplic = applications.find_one({'_id': ObjectId(edit_id)})
        tstamp = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        updated = {
            "input-timestamp": aplic['input-timestamp'],
            "edit-timestamp": tstamp,
            "year": aplic['year'],
            "applicant": request.form['applicant'],
            "pub-title": request.form['pub-title'],
            "is-graded": aplic['is-graded'],
            "assigned-to": aplic['assigned-to'],
            "aai-email": session['user'],
            "type": request.form['type']
        }
        applications.update_one({'_id': ObjectId(edit_id)}, {'$set': updated})

        return redirect('/user/applications')


@userapp.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    if request.method == 'GET':
        return render_template('add.html', types=essents.applicationTypes, username=session['user'])

    if request.method == 'POST':
        tstamp = strftime("%d-%m-%Y %H:%M:%S", gmtime())
        applications = mongo.db.applications
        new = {
            "input-timestamp": tstamp,
            "edit-timestamp": tstamp,
            "year": strftime("%Y", gmtime()),  # DROP DOWN ????? I REQUEST.FORM
            "applicant": request.form['applicant'],
            "pub-title": request.form['pub-title'],
            "is-graded": 'Ne',
            "grade": 0,
            "grade-fields": {},
            "assigned-to": '-',
            "aai-email": session['user'],
            "type": request.form['type']
        }
        applications.insert(new)
        return redirect('/user/applications')


@userapp.route('/applications/view', methods=['GET'])
def view_application():
    vid = request.args.get('id', default='0')
    if vid == '0':
        return redirect('/user/applications')

    applications = mongo.db.applications

    valid, applic = essents.test_id(applications, vid)

    if not valid:
        return render_template('view.html', app=None, username=session['user'])

    if applic['aai-email'] == session['user']:
        return render_template('view.html', app=applic, haspermission=True, username=session['user'])
    return render_template('view.html', haspermission=False, username=session['user'])


@userapp.route('/applications/delete', methods=['GET'])
def delete():
    del_id = request.args.get('id', default='0')
    if del_id == '0':
        return redirect('/user/applications')

    if request.method == 'GET':
        applications = mongo.db.applications
        appl = applications.find_one({'_id': ObjectId(del_id)})
        if appl['aai-email'] == session['user']:
            applications.remove({'_id': ObjectId(del_id)})

        return redirect('/user/applications')
