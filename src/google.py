from flask import Flask, redirect, url_for, request, render_template, flash, session
from flask_login import LoginManager, login_user
from flask_dance.contrib.google import make_google_blueprint, google
from models import GoogleUser, db
import sqlalchemy


google_login = make_google_blueprint(
    scope=["profile", "email"]
)

login_manager = LoginManager()
login_manager.init_app(google_login)

# Route to redirect to Google OAuth page
@google_login.route("/")
def signin_google():
    if google.authorized:
        resp = google.get("/oauth2/v1/userinfo")
        email = resp.json()['email']
        username = resp.json()['given_name']
        picture = resp.json()['picture']
        print(picture, email, username)
        user = GoogleUser.query.filter_by(email=email).first()
        if user:
            login_user(user)
            return redirect(url_for('home.show'))
        else:
            try:
                new_user = GoogleUser(username=username, email=email, picture=picture)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('home.show'))
            except sqlalchemy.exc.IntegrityError as e:
                db.session.rollback()
                print(e)
            finally:
                db.session.close()
    flash("Unauthorized!", "danger")
    return redirect(url_for("login.show"))