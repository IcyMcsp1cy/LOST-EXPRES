from .extensions import mongo, mail
from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager
import uuid
import random

class User:

    def start_session(self, user):
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    def signup(self, email, firstName, lastName, institution):
        print(request.form)

        user = {
            "_id": uuid.uuid4().hex,
            "email": email,
            "firstName": firstName,
            "lastName": lastName,
            "institution": institution,
            "password": random.randrange(1, 1000, 1),
            "type": "researcher",
        }
        #TODO ADD ENCRYPTION
        #user['password'] = pbkdf2_sha256.encrypt(user['password'])
        user['password'] = "password"
        if mongo.db.user.find_one({ "email": user['email'] }):
            return jsonify({ "error": "Email address in use!"}), 400

        mongo.db.user.insert_one(user)

        return jsonify(user), 200

    def signout(self):
        session.clear()
        return redirect('/')
