import bson
from bson import ObjectId
import string
import random
from xhtml2pdf import pisa
from io import StringIO, BytesIO


class Essentials:
    def __init__(self):
        self.applicationTypes = [
            'Tip 1',
            'Tip 2',
            'Tip 3',
        ]

    @staticmethod
    def check_role(allowed, current):
        return allowed == current

    @staticmethod
    def test_id(collection, id):
        try:
            applic = collection.find_one({'_id': ObjectId(id)})
            if applic is None:
                return False, None
            return True, applic
        except bson.errors.InvalidId:
            return False, None

    @staticmethod
    def generate_pass(size=7):
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def moderator_assignment(apps, mods, applications, unassign=False):
        c = 0
        if unassign:
            for a in apps:
                applications.update_one({'_id': ObjectId(str(a['_id']))}, {'$set': {'assigned-to': '-'}})
        else:
            for a in apps:
                try:
                    chosenmod = mods[c]['username']
                except IndexError:
                    c = 0
                    chosenmod = mods[c]['username']
                applications.update_one({'_id': ObjectId(str(a['_id']))}, {'$set': {'assigned-to': chosenmod}})
                c += 1


class Pdf:
    @staticmethod
    def render_pdf(html):
        pdf = BytesIO()
        try:
            pisa.CreatePDF(StringIO(html), pdf)
        except TypeError:
            pass
        return pdf.getvalue()
