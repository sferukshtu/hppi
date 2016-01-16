from app import app, lm
import xlrd
import xlwt
import StringIO
from flask import request, redirect, render_template, url_for, flash, Response
from flask.ext.login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, PersonForm, CalcForm, RatingForm
from .auth import Auth
import datetime
 

def makeform():
    form = LoginForm(request.values, from_url=request.path)
    # print form.errors
    # print form.validate_on_submit()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['STAFF'].find_one({"email": form.email.data})
        if user and Auth.validate_login(user['password'], form.password.data):
            user_obj = Auth(user['email'], user['access'], user['first_name'], user['surname'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            # return redirect(request.args.get("next") or url_for("edit"))
        else:
            flash("Wrong username or password!", category='error')
    return form


@app.route('/')
def index():
    item = app.config['STAFF'].find()
    form = makeform()
    return render_template('index.html', item=item, form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = makeform()
    url = form.from_url.data
    if url is not None and url != "/" and url != "":
        url = url.strip("/")
        return redirect(url_for(url))
    else:
        return redirect("/")


@app.route('/logout/')
def logout():
    logout_user()
    return redirect("/")


@app.route('/on_rating/', methods=['GET', 'POST'])
def on_rating():
    form = makeform()
    cform = CalcForm(request.values)
    item = app.config['RATING'].find()
    if request.method == 'POST' and Auth.is_authenticated and current_user.access == 2 and cform.validate_on_submit():
        app.config['SETTINGS'].update_one({'set_id': "prnd"}, {'$set': cform.data})
        f = request.files['defs']
        if f and extension_ok(f.filename):
            content = f.stream.read()
            rd = xlrd.open_workbook(file_contents=content)
            sheet = rd.sheet_by_index(0)
            header = sheet.row_values(0)  # column headers
            app.config['RATING'].drop()
            for rownum in range(1, sheet.nrows):
                data = xls_to_data(sheet, rd, rownum, header)
                app.config['RATING'].insert(data)
        app.config['SETTINGS'].update({'set_id': "prnd"}, {'$unset': {'defs': ""}})
        flash("Data updated successfully!", category='info')
    return render_template('on_rating.html', item=item, form=form, cform=cform)


@app.route('/card/staff:<email>', methods=['GET', 'POST'])
def card(email):
    form = makeform()
    pform = RatingForm(request.values)
    # print pform.o_num.data
    if request.method == 'POST' and Auth.is_authenticated and (current_user.email == email or current_user.access == 2):
        app.config['STAFF'].update_one({'email': email}, {'$unset': {'prnd_data': []}})
        app.config['STAFF'].update_one({'email': email}, {'$push': {'prnd_data': pform.data}})
        val = app.config['SETTINGS'].find_one()
        math = val["prnd"]
        for k, v in pform.data.iteritems():
            v = int(v) if v else 0
            exec(k + " = v")
        app.config['STAFF'].update_one({'email': email}, {'$set': {'prnd': eval(math)}})
    prs = app.config['STAFF'].find_one({"email": email})
    return render_template('card.html', prs=prs, form=form)


@app.route('/pubs/staff:<email>', methods=['GET', 'POST'])
def pubs(email):
    form = makeform()
    prs = app.config['STAFF'].find_one({"email": email})
    return render_template('pubs.html', prs=prs, form=form)


@app.route('/edit/staff:<email>', methods=['GET', 'POST'])
@login_required
def edit(email):
    prs = app.config['STAFF'].find_one({"email": email})
    form = PersonForm(request.values, first_name=prs["first_name"], middle_name=prs["middle_name"],
                      surname=prs["surname"], email=prs["email"], graduated=prs["graduated"],
                      graduated_year=prs["graduated_year"], date_of_birth=prs["date_of_birth"],
                      degree=prs["degree"], lab=prs["lab"])
    # val_dict = {}
    prnd_data = prs["prnd_data"][0] if prs["prnd_data"] else {}
    pform = RatingForm(request.values)
    # pform = RatingForm(request.values)
    prs = app.config['STAFF'].find_one({"email": email})
    if request.method == 'POST' and form.validate_on_submit() and Auth.is_authenticated and (current_user.email == email or current_user.access == 2):
        if form.data:
            bd = datetime.datetime.strptime(str(form.date_of_birth.data), "%Y-%m-%d")
            form.date_of_birth.data = bd
            error = 0
            f = request.files['publist']
            rownum = 0
            if f and extension_ok(f.filename):
                content = f.stream.read()
                rd = xlrd.open_workbook(file_contents=content)
                sheet = rd.sheet_by_index(0)
                header = sheet.row_values(0)  # column headers
                if fields(set(header)) == 0:
                    app.config['STAFF'].update({'email': email}, {'$unset': {'publist': []}})
                    for rownum in range(1, sheet.nrows):
                        data = xls_to_data(sheet, rd, rownum, header)
                        data["art_id"] = rownum
                        app.config['STAFF'].update({'email': email}, {'$addToSet': {'publist': {'$each': [data]}}}, True, True)
                else:
                    flash("Column names do not correspond to the specification!", category='error')
                    error = 1
            pubsnum = rownum if rownum else prs["pubs"]
            app.config['STAFF'].update_one({'email': email}, {'$set': form.data})
            app.config['STAFF'].update_one({'email': email}, {'$set': {'pubsnum': pubsnum}})
        else:
            error = 1
            flash("Something wrong with data update!", category='error')
        if error == 0:
            flash("Data updated successfully!", category='info')
        else:
            flash("Something wrong happened!", category='error')
    item = app.config['RATING'].find()
    return render_template('edit.html', prs=prs, form=form, item=item, pform=pform, prnd_data=prnd_data)


@app.route('/download/staff:<email>', methods=['GET', 'POST'])
def download(email):
    prs = app.config['STAFF'].find_one({"email": email})
    output = StringIO.StringIO()  # create a file-like object
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet("Publications", cell_overwrite_ok=True)
    sheet.write(0, 0, "title")
    sheet.write(0, 1, "authors")
    sheet.write(0, 2, "abstract")
    sheet.write(0, 3, "url")
    sheet.write(0, 4, "date")
    sheet.write(0, 5, "journal")
    sheet.write(0, 6, "pubinfo")
    r = 1
    for entry in prs["publist"]:
        sheet.write(r, 0, entry["title"])
        sheet.write(r, 1, entry["authors"])
        sheet.write(r, 2, entry["abstract"])
        sheet.write(r, 3, entry["url"])
        sheet.write(r, 4, entry["date"].strftime('%d-%m-%Y'))
        sheet.write(r, 5, entry["journal"])
        sheet.write(r, 6, entry["pubinfo"])
        r += 1
    book.save(output)
    xls = output.getvalue()
    output.close()
    return Response(xls, mimetype='application/vnd.ms-excel', headers={"Content-disposition": "attachment; filename=Publications.xls"})


@lm.user_loader
def load_user(email):
    u = app.config['STAFF'].find_one({"email": email})
    if not u:
        return None
    return Auth(u['email'], u['access'], u['first_name'], u['surname'])


def extension_ok(filename):
    """ return whether file's extension is ok or not"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['FILE_EXTENSIONS']


def fields(titles):
    """ Column names must be named only as below"""
    names = ["title", "authors", "abstract", "url", "date", "journal", "pubinfo"]
    is_identical = titles.union(set(names)) - titles.intersection(set(names))
    return len(is_identical)


def xls_to_data(sheet, rd, rownum, header):
    row = sheet.row_values(rownum)  # row values
    data = {}
    for el in range(len(header)):
        if header[el] == "date":
            dt = datetime.datetime(*xlrd.xldate_as_tuple(row[el], rd.datemode))  # convert date from excel
        else:
            dt = row[el]
        data[header[el]] = dt  # pack data in a dictionary data[name] = value
    return data


def packed(val_dict):
    # vls = ", ".join(['{}={}'.format(k, v) for k, v in val_dict.iteritems()])
    ll = []
    for k, v in val_dict.iteritems():
        exec(k + " = v")
        ll.append(k)
    return ll
