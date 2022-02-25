import flask
from werkzeug.security import check_password_hash
from flask_login import UserMixin

class User(UserMixin):

    def __init__(self,correo,contraseña):
        self.correo = correo
        self.contraseña = contraseña 

    @classmethod #para no instanciar la clase se usa este decorador 
    def check_password_hash(self,hashed_contraseña,contraseña):
        return check_password_hash(hashed_contraseña,contraseña)

