from app import app, lm
from flask import request, redirect, render_template, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm
from .auth import Auth


@app.route('/')
def index():
    item = app.config['STAFF'].find()
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['STAFF'].find_one({"email": form.email.data})
        if user and Auth.validate_login(user['password'], form.password.data):
            user_obj = Auth(user['email'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("edit"))
        flash("Wrong username or password!", category='error')
    return render_template('index.html', item=item, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['STAFF'].find_one({"email": form.email.data})
        if user and Auth.validate_login(user['password'], form.password.data):
            user_obj = Auth(user['email'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("edit"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('/'))


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    return render_template('edit.html')


@lm.user_loader
def load_user(email):
    u = app.config['STAFF'].find_one({"email": email})
    if not u:
        return None
    return Auth(u['email'])
