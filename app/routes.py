from app import app
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, AddServerForm, AddKeyForm
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import db
from app.models import User, Server, Partner, Key

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.login == form.login.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(login=form.login.data,
                    email=form.email.data,
                    telegram_id=form.telegram_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/servers')
def servers():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    #  временно все юзеры являются партнерами
    if not current_user.partner:
        partner = Partner(user_id=current_user.id)
        db.session.add(partner)
        current_user.user_type = 'partner'
        db.session.commit()

    servers = Server.query.filter_by(partner_id=current_user.partner.id).all()

    return render_template('servers.html', servers=servers)


@app.route('/add_server', methods=['GET', 'POST'])
def add_server():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    form = AddServerForm()
    if form.validate_on_submit():
        server = Server(name=form.name.data,
                        price=form.price.data,
                        url=form.url.data,
                        panel_login=form.login_panel.data,
                        partner_id=current_user.partner.id)
        server.set_password(form.password_panel.data)
        db.session.add(server)
        db.session.commit()

        flash('Server is created.')
        return redirect(url_for('servers'))

    return render_template('add_server.html', title='add Server', form=form)


#not implemented
@app.route('/edit_server')
def edit_server():
    return redirect(url_for('servers'))


#not implemented
@app.route('/delete_server')
def delete_server():
    return redirect(url_for('servers'))


@app.route('/keys/<int:server_id>')
def keys(server_id):
    server = Server.query.get_or_404(server_id)
    if server.partner_id != current_user.id:
        return redirect(url_for('servers'))

    keys = Key.query.filter_by(server_id=server.id).all()
    return render_template('keys.html', server=server, keys=keys)


@app.route('/keys/<int:server_id>/add_key', methods=['GET', 'POST'])
def add_key(server_id):
    server = Server.query.get_or_404(server_id)
    if server.partner_id != current_user.id:
        return redirect(url_for('servers'))

    form = AddKeyForm()
    if form.validate_on_submit():
        new_key = Key(
            code=form.code.data,
            server_id=server.id,
        )

        db.session.add(new_key)
        db.session.commit()

        flash("Key successfully added!")
        return redirect(url_for('keys', server_id=server.id)) # тут пиздец

    return render_template('add_key.html', title='Add Key', form=form, server=server)


@app.route('/update_key/<int:key_id>', methods=['POST'])
def update_key(key_id):
    key = Key.query.get_or_404(key_id)
    if key.server.partner_id != current_user.id:
        return
    data = request.get_json()
    key.payed = data.get('payed', False)
    db.session.commit()