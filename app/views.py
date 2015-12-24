from app import app, lm
from flask import request, redirect, render_template, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm, PersonForm
from .auth import Auth
import datetime


def makeform():
    form = LoginForm(request.values, from_url=request.path)
    # print form.errors
    # print form.validate_on_submit()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['STAFF'].find_one({"email": form.email.data})
        if user and Auth.validate_login(user['password'], form.password.data):
            user_obj = Auth(user['email'], user['access'])
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


@app.route('/on_rating/')
def on_rating():
    form = makeform()
    return render_template('on_rating.html', form=form)


@app.route('/card/staff:<email>')
def card(email):
    prs = app.config['STAFF'].find_one({"email": email})
    return render_template('card.html', prs=prs)


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


@app.route('/pubs/staff:<email>', methods=['GET', 'POST'])
def pubs(email):
    prs = app.config['STAFF'].find_one({"email": email})
    return render_template('pubs.html', prs=prs)


@app.route('/edit/staff:<email>', methods=['GET', 'POST'])
@login_required
def edit(email):
    form = PersonForm(request.values)
    if request.method == 'POST' and form.validate_on_submit():
        if form.data:
            bd = datetime.datetime.strptime(str(form.date_of_birth.data), "%Y-%m-%d")
            form.date_of_birth.data = bd
            app.config['STAFF'].update_one({'email': email}, {'$set': form.data})
            flash("Data updated successfully!", category='info')
        else:
            flash("Something wrong happened!", category='error')
    prs = app.config['STAFF'].find_one({"email": email})
    form = PersonForm(request.values, first_name=prs["first_name"], middle_name=prs["middle_name"],
                      surname=prs["surname"], email=prs["email"], graduated=prs["graduated"],
                      graduated_year=prs["graduated_year"], date_of_birth=prs["date_of_birth"],
                      degree=prs["degree"], lab=prs["lab"])
    return render_template('edit.html', prs=prs, form=form)


@lm.user_loader
def load_user(email):
    u = app.config['STAFF'].find_one({"email": email})
    if not u:
        return None
    return Auth(u['email'], u['access'])
