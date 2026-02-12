from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db
from app.models.models import User, PasswordResetToken, InviteCode
from app.email_utils import send_password_reset_email, send_invite_email

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember_me') == 'on'

        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)

    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# ---------- Forgot / Reset Password ----------

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        # Always show success to prevent email enumeration
        user = User.query.filter_by(email=email).first()
        if user:
            token = PasswordResetToken.generate(user, hours=1)
            reset_url = url_for('auth.reset_password', token=token.token, _external=True)
            send_password_reset_email(user, reset_url)
        flash('If that email is registered, a reset link has been sent.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    prt = PasswordResetToken.query.filter_by(token=token).first()
    if not prt or not prt.is_valid:
        flash('This reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('auth.reset_password', token=token))

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.reset_password', token=token))

        prt.user.set_password(password)
        prt.used = True
        db.session.commit()
        flash('Password reset successfully. Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


# ---------- Invite-Only Registration ----------

@auth.route('/register/<code>', methods=['GET', 'POST'])
def register_invite(code):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    invite = InviteCode.query.filter_by(code=code).first()
    if not invite or not invite.is_valid:
        flash('This invite link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register_invite', code=code))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('auth.register_invite', code=code))

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register_invite', code=code))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('auth.register_invite', code=code))

        if User.query.filter_by(email=invite.email).first():
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('auth.login'))

        user = User(username=username, email=invite.email)
        user.set_password(password)
        invite.used = True
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_invite.html', invite=invite)


# ---------- Admin: User Management ----------

@auth.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    users = User.query.order_by(User.id).all()
    pending_invites = InviteCode.query.filter_by(used=False).order_by(InviteCode.created_at.desc()).all()
    return render_template('admin/users.html', users=users, pending_invites=pending_invites)


@auth.route('/admin/invite', methods=['POST'])
@login_required
def admin_invite():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    email = request.form.get('email', '').strip().lower()
    if not email:
        flash('Email is required.', 'error')
        return redirect(url_for('auth.admin_users'))

    if User.query.filter_by(email=email).first():
        flash('A user with this email already exists.', 'error')
        return redirect(url_for('auth.admin_users'))

    invite = InviteCode.generate(email, current_user, hours=48)
    invite_url = url_for('auth.register_invite', code=invite.code, _external=True)
    sent = send_invite_email(email, invite_url, current_user.username)

    if sent:
        flash(f'Invite sent to {email}.', 'success')
    else:
        flash(f'Invite created but email failed to send. Share this link manually: {invite_url}', 'error')

    return redirect(url_for('auth.admin_users'))


@auth.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.admin_users'))

    if user.id == current_user.id:
        flash("You can't change your own admin status.", 'error')
        return redirect(url_for('auth.admin_users'))

    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'{"Granted" if user.is_admin else "Revoked"} admin for {user.username}.', 'success')
    return redirect(url_for('auth.admin_users'))


@auth.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.admin_users'))

    if user.id == current_user.id:
        flash("You can't delete your own account.", 'error')
        return redirect(url_for('auth.admin_users'))

    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.', 'success')
    return redirect(url_for('auth.admin_users'))


@auth.route('/admin/invites/<int:invite_id>/revoke', methods=['POST'])
@login_required
def revoke_invite(invite_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    invite = db.session.get(InviteCode, invite_id)
    if invite:
        invite.used = True
        db.session.commit()
        flash('Invite revoked.', 'success')
    return redirect(url_for('auth.admin_users'))


# ---------- User Profile ----------

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not email:
            flash('Email is required.', 'error')
            return redirect(url_for('auth.profile'))

        if not username:
            flash('Username is required.', 'error')
            return redirect(url_for('auth.profile'))

        # Check email uniqueness (if changed)
        if email != current_user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash('That email is already in use.', 'error')
                return redirect(url_for('auth.profile'))

        # Check username uniqueness (if changed)
        if username != current_user.username:
            existing = User.query.filter_by(username=username).first()
            if existing:
                flash('That username is already taken.', 'error')
                return redirect(url_for('auth.profile'))

        # Handle password change (optional)
        if new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('auth.profile'))
            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'error')
                return redirect(url_for('auth.profile'))
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('auth.profile'))
            current_user.set_password(new_password)

        current_user.email = email
        current_user.username = username
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
