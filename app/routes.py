from flask import render_template, redirect, url_for, flash
from flask import Blueprint  # Adicione esta linha
from app import db
from app.forms import RegistrationForm, LoginForm
from app.models import User, AutisticPerson
from flask_login import login_user, logout_user, login_required, current_user

# Crie os Blueprints
main_routes = Blueprint('main_routes', __name__)
auth_routes = Blueprint('auth_routes', __name__)
admin_routes = Blueprint('admin_routes', __name__)

# Rotas do Blueprint main_routes


@main_routes.route('/')
def index():
    return render_template('index.html')

# Rotas do Blueprint auth_routes


@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        person = AutisticPerson(
            name=form.name.data,
            email=form.email.data,
            father_name=form.father_name.data,
            mother_name=form.mother_name.data,
            birth_date=form.birth_date.data
        )
        db.session.add(person)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Aguarde aprovação.', 'success')
        return redirect(url_for('main_routes.index'))
    return render_template('register.html', form=form)


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            # Corrigido
            return redirect(url_for('admin_routes.admin_dashboard'))
        else:
            flash('Login falhou. Verifique seu email e senha.', 'danger')
    return render_template('login.html', form=form)


@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_routes.index'))

# Rotas do Blueprint admin_routes


@admin_routes.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('main_routes.index'))
    pending_registrations = AutisticPerson.query.filter_by(
        approved=False).all()
    return render_template('admin_dashboard.html', pending_registrations=pending_registrations)


@admin_routes.route('/admin/approve/<int:person_id>')
@login_required
def approve_registration(person_id):
    if not current_user.is_admin:
        return redirect(url_for('main_routes.index'))
    person = AutisticPerson.query.get_or_404(person_id)
    person.approved = True
    db.session.commit()
    flash('Cadastro aprovado com sucesso!', 'success')
    return redirect(url_for('admin_routes.admin_dashboard'))
