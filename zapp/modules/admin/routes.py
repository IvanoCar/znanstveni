from flask import Blueprint, session, render_template, redirect, request
from zapp import mongo, essents
from bson.objectid import ObjectId
import random
from zapp.essentials import Pdf

adminapp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='admin-templates')


# RJEŠITI YEAR 2018 U PERIOD

@adminapp.before_request
def check_session():
    try:
        if not session['logged-in']:
            return render_template('login.html', notlgin=True)
    except KeyError:
        return render_template('login.html', notlgin=True)

    if not essents.check_role('admin', session['role']):
        return redirect('/' + session['role'])


@adminapp.route('/')
@adminapp.route('/dashboard')
def dash():
    users = mongo.db.users
    applications = mongo.db.applications

    app_no = applications.count({'year': '2018'})
    apps_no_nassigned = applications.count({'assigned-to': '-'})
    apps_not_graded = applications.count({'is-graded': 'Ne'})
    moderator_no = users.count({'role': 'moderator'})

    return render_template('dashboard-a.html', username=session['user'], modNo=moderator_no, appNo=app_no,
                           notAssignedApps=apps_no_nassigned, appsNotGraded=apps_not_graded)


@adminapp.route('/applications', methods=['GET'])
def apps_view():
    criteria = request.args.get('criteria', default='all')
    applications = mongo.db.applications
    if criteria == 'not-graded':
        apps = applications.find({'is-graded': 'Ne'})
        return render_template('applications-a.html', username=session['user'], showGradeButons=True, apps=list(apps),
                               applicationsTitle='Neocjenjene prijave')
    elif criteria == 'not-assigned':
        apps = applications.find({'assigned-to': '-'})
        return render_template('applications-a.html', username=session['user'], showRandomAssignBtn=True,
                               apps=list(apps), applicationsTitle='Nedodijeljene prijave')
    else:
        apps = applications.find({'year': '2018'})
        return render_template('applications-a.html', username=session['user'], showGradeButons=True,
                               showRandomAssignBtn=True, apps=list(apps), applicationsTitle='Sve prijave')


@adminapp.route('/moderators', methods=['GET'])
def moderators():
    users = mongo.db.users
    return_list = list(users.find({'role': 'moderator'}))
    return render_template('moderators-a.html', moderators=return_list, username=session['user'])


@adminapp.route('/moderators/delete', methods=['GET'])
def delete_moderator():
    del_id = request.args.get('id', default='0')
    if del_id == '0':
        return redirect('/admin/moderators')

    settings = mongo.db.settings
    moderator_no = settings.find_one({'document-name': 'SETTINGS'})
    users = mongo.db.users
    users.remove({'_id': ObjectId(del_id)})
    no = moderator_no['moderator-count']
    settings.update_one({'_id': ObjectId(str(moderator_no['_id']))}, {'$set': {'moderator-count': no}})
    return redirect('/admin/moderators')


@adminapp.route('/moderators/add', methods=['GET'])
def add_moderator():
    users = mongo.db.users
    settings = mongo.db.settings
    moderator_no = settings.find_one({'document-name': 'SETTINGS'})
    no = moderator_no['moderator-count'] + 1
    moderator = {
        'username': 'moderator' + str(no),
        'password': essents.generate_pass(8),
        'grading': 'NOT SET',
        'role': 'moderator'
    }

    settings.update_one({'_id': ObjectId(str(moderator_no['_id']))}, {'$set': {'moderator-count': no}})
    users.insert(moderator)
    return redirect('/admin/moderators')


@adminapp.route('/moderators/password-reset', methods=['GET'])
def password_reset():
    users = mongo.db.users
    mods = list(users.find({'role': 'moderator'}))

    for moderator in mods:
        users.update_one({'_id': ObjectId(str(moderator['_id']))}, {'$set': {'password': essents.generate_pass(8)}})

    return redirect('/admin/moderators')


@adminapp.route('/assign', methods=['GET'])
def assign():
    action = request.args.get('action', default='0')

    applications = mongo.db.applications
    users = mongo.db.users
    alla = list(applications.find({'year': '2018'}))

    mods = users.find({'role': 'moderator'})
    mods = list(mods)
    unassign = False
    if len(mods) is 0:
        unassign = True

    random.shuffle(mods)

    napps = []
    other = []
    for a in alla:
        if a['assigned-to'] == '-':
            napps.append(a)
        else:
            other.append(a)

    if action == 'randomize' or action == 'assign':
        if action == 'randomize':
            essents.moderator_assignment(alla, mods, applications, unassign)
        elif action == 'assign':
            if not unassign:
                essents.moderator_assignment(napps, mods, applications)
    return render_template('assign.html', notaApps=napps, otherApps=other, username=session['user'])


@adminapp.route('/rang-list')
def ranglist():
    applications = mongo.db.applications
    apps = applications.find({'year': '2018'}).sort('grade', -1)

    return render_template('rang-list-a.html', username=session['user'], apps=list(apps))


@adminapp.route('/rang-list/pdf')
def ranglistpdf():
    applications = mongo.db.applications
    apps = applications.find({'year': '2018'}).sort('grade', -1)
    apps = list(apps)

    pdf_data = render_template('rang-pdf.html', apps=apps)
    file_class = Pdf()
    pdf = file_class.render_pdf(html=pdf_data)
    headers = {
        'content-type': 'application.pdf',
        'content-disposition': 'attachment; filename=RangList.pdf',
        'charset': 'utf-8'
    }
    return pdf, 200, headers
