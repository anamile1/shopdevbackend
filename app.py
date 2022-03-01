import os
import cloudinary
import cloudinary.uploader
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config
from flask_login import LoginManager, login_user,logout_user,login_required
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv


#Models:
from models.ModelUser import ModelUser

#Entities:
from models.entities.User import User

load_dotenv()

#Instancia
app=Flask(__name__)
app=Flask(__name__)
CORS(app)


#Inicializar app, ejecutar mediante sentencias sql (select, insert...)
db=MySQL(app)
app.config["MYSQL_HOST" ]= 'boappj44csi2jovaxmpy-mysql.services.clever-cloud.com'
app.config["MYSQL_HOST"]= 'boappj44csi2jovaxmpy-mysql.services.clever-cloud.com'
app.config["MYSQL_USER"]= 'un7wcwcqtgb6cod2'
app.config["MYSQL_PASSWORD"]= 'e4HMan3wybvY2gD8S2X4'
app.config["MYSQL_DB"]= 'boappj44csi2jovaxmpy'
app.config["MYSQL_PORT"]= 3306

login_manager_app=LoginManager(app)
@login_manager_app.user_loader
def load_user(cedula):
    return ModelUser.get_by_cedula(db,cedula)


#ruta raiz
@app.route('/')
def index():
    return jsonify({"mensaje": "SHOPDEV"})
    #redirección al login

@app.route('/registro', methods=['POST'])
def registroUsuario():
    # try:
        cursor=db.connection.cursor()
        sql = """INSERT INTO clientes (cedula,nombres,telefono,departamento,ciudad,
        direccion,correo,contraseña,rol) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}',
        '{7}',('1'))""".format(request.json['cedula'], request.json['nombres'],
        request.json['telefono'], request.json['departamento'],
        request.json['ciudad'], request.json['direccion'], request.json['correo'],
        request.json['contraseña'])
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Usuario registrado"})
    # except Exception as ex:
    #     return jsonify({"Mensaje": "Error"})


#ruta inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    #petición a URL
    if request.method == 'POST':
        user = User(request.form['correo'],request.form['contraseña'])
        logged_user = ModelUser.login(db,user)
        return logged_user
    else:
        return jsonify({"Mensaje": "Datos invalidos"})

#cierre de sesión
@app.route('/logout')
def logout():
    logout_user()
    return jsonify({"Mensaje": "Cerró sesión exitosamente"})

#CRUD productos
#agregar nuevo Producto
@app.route('/nuevoProducto', methods=['POST'])
def nuevoProducto():
    # try:
        imagen = request.form['imagen']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        talla = request.form['talla']
        precio = request.form['precio']
        categoria = request.form['categoria']
        cantidad = request.form['cantidad']
        color = request.form['color']
        tallaje = request.form['tallaje']
        cursor=db.connection.cursor()
        sql = f"""INSERT INTO productos(imagenes,nombre,descripcion,talla,precio,categoria,cantidad,color,tallaje)
        VALUES  ('{imagen}','{nombre}','{descripcion}','{talla}','{precio}','{categoria}','{cantidad}','{color}','{tallaje}')"""
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Producto registrado"})
    # except Exception as ex:
    #     return jsonify({"Mensaje": "Error"})


@app.route('/upload', methods=['POST'])
def uploadFile(url):
    app.logger.info('in upload route')

    cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'),
    api_key = os.getenv('API_KEY'),
    api_secret = os.getenv('API_SECRET'))
    uploadResult = None
    if request.method == 'POST':
        fileToUpload = url
        app.logger.info('fileToUpload')
        if fileToUpload:
            uploadResult =cloudinary.uploader.upload(fileToUpload)
            app.logger.info('uploadResult')
            print(uploadResult)
            return uploadResult['url']

@app.route('/listarProductos', methods=['GET'])
def listarProductos():
    try:
        cursor=db.connection.cursor()
        sql=  'SELECT * FROM productos'
        cursor.execute(sql)
        row = cursor.fetchall()
        return jsonify({"Mensaje": row})
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/modificarProducto/<codigo>',methods=['PUT'])
def modificarProducto(codigo):
    cursor=db.connection.cursor()
    sql = f"""UPDATE productos SET imagenes = '{request.json['imagenes']}',nombre = '{request.json['nombre']}',
    descripcion = '{request.json['descripcion']}', talla = '{request.json['talla']}',precio = '{request.json['precio']}',
    categoria = '{request.json['categoria']}',cantidad = '{request.json['cantidad']}',color = '{request.json['color']}',
    tallaje = '{request.json['tallaje']}' WHERE codigo = '{codigo}'"""
    cursor.execute(sql)
    db.connection.commit()
    return jsonify({"Mensaje": "Producto modificado"})

@app.route('/eliminarProducto/<codigo>',methods=['DELETE'])
def eliminarProducto(codigo):
    cursor=db.connection.cursor()
    sql = ('DELETE FROM productos where codigo = {0}'.format(codigo))
    cursor.execute(sql)
    db.connection.commit()
    return jsonify({"Mensaje": "Producto eliminado"})

#FiltroS categoria
# @app.route('/filtrarCamiseta')
# def filtrarCamiseta():
#     cursor=db.connection.cursor()
#     sql = ('SELECT * FROM productos where categoria like '{categoria}')
#     cursor.execute(sql)
#     db.connection.commit()
#     return jsonify




if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()

