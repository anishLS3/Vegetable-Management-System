from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from DeliverySystem import login_manager
from flask_login import UserMixin
import pickle

@login_manager.user_loader
def load_user(email):
    return User.get_by_email(email) if email else None

def load_admins(email):
    return Admin.get_by_email(email) if email else None

class User(UserMixin):

    def __init__(self, username, email, password, role):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = 'user'

    def save(self, hashed_password=None):
        users = User.load_users()
        user_data = next((user for user in users if user['email'] == self.email), None)

        if user_data:
            user_data['username'] = self.username
            user_data['email'] = self.email
            if hashed_password:
                user_data['password'] = hashed_password
            else:
                user_data['password'] = self.password
            user_data['role'] = self.role
        else:
            users.append({'username': self.username, 'email': self.email, 'password': hashed_password or self.password, 'role': self.role})

        User.save_users(users)

    
    @staticmethod
    def get_by_username(username):
        users = User.load_users()
        return next((user for user in users if user['username'] == username), None)

    @classmethod
    def get_by_email(cls, email):
        users = cls.load_users()
        for user in users:
            if user['email'] == email:
                return cls(user['username'], user['email'], user['password'], user.get('role', 'user'))
        return None

    def get_reset_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'],  expires_in)
        return s.dumps({'email': self.email}, salt='reset_token')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        data = s.loads(token, salt='reset_token', max_age=3600)
        user = User.get_by_email(data['email'])
        return user

    @staticmethod
    def load_users():
        try:
            with open('users.pkl', 'rb') as file:
                return pickle.load(file, encoding='latin1')
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading users: {e}")
            return []

    @staticmethod
    def save_users(users):
        try:
            with open('users.pkl', 'wb') as file:
                pickle.dump(users, file)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Admin(UserMixin):
    def __init__(self, username , email, password):
        self.id = id  
        self.username = username
        self.email = email
        self.password = password
        self.role = 'admin'  

    def save(self, hashed_password=None):
        admins = Admin.load_admins()
        admin_data = next((admin for admin in admins if admin['email'] == self.email), None)

        if admin_data:
            admin_data['username'] = self.username
            admin_data['email'] = self.email
            if hashed_password:
                admin_data['password'] = hashed_password
            else:
                admin_data['password'] = self.password
        else:
            admins.append({'username': self.username, 'email': self.email, 'password': hashed_password or self.password})

        Admin.save_admins(admins)

    @staticmethod
    def get_by_username(username):
        admins = Admin.load_admins()
        return next((admin for admin in admins if admin['username'] == username), None)

    @classmethod
    def get_by_email(cls, email):
        admins = cls.load_admins()
        for admin in admins:
            if admin['email'] == email:
                return cls(admin['username'], admin['email'], admin['password'])
        return None

    @staticmethod
    def load_admins():
        try:
            with open('admin.pkl', 'rb') as file:
                return pickle.load(file, encoding='latin1')
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading admins: {e}")
            return []

    @staticmethod
    def save_admins(admins):
        print("Data to be saved:", admins)
        try:
            with open('admin.pkl', 'wb') as file:
                pickle.dump(admins, file)
            print("Data successfully pickled.")
        except Exception as e:
            print(f"Error saving admins: {e}")

    def __repr__(self):
        return f"Admin('{self.username}', '{self.email}')"


