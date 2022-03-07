import os
import MySQLdb
import cloudinary
import cloudinary.uploader
from flask import Flask, jsonify, request, session
from flask_mysqldb import MySQL
from config import config
from flask_login import logout_user
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

#Instancia
app=Flask(__name__)
app=Flask(__name__)
CORS(app)

# cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'B!1w8NAt1T^%kvhUI*S^'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)

#Inicializar app, ejecutar mediante sentencias sql (select, insert...)
db=MySQL(app)
app.config["MYSQL_HOST" ]= 'boappj44csi2jovaxmpy-mysql.services.clever-cloud.com'
app.config["MYSQL_HOST"]= 'boappj44csi2jovaxmpy-mysql.services.clever-cloud.com'
app.config["MYSQL_USER"]= 'un7wcwcqtgb6cod2'
app.config["MYSQL_PASSWORD"]= 'e4HMan3wybvY2gD8S2X4'
app.config["MYSQL_DB"]= 'boappj44csi2jovaxmpy'
app.config["MYSQL_PORT"]= 3306


#ruta raiz
@app.route('/')
def index():
    return jsonify({"mensaje": "SHOPDEV"})
    #redirección al login

@app.route('/registro', methods=['POST'])
def registroUsuario():    
    try:
        passhashRegistro = generate_password_hash(request.json['contraseña'])
        cursor=db.connection.cursor()
        sql = """INSERT INTO clientes (cedula,nombres,telefono,departamento,ciudad,
        direccion,correo,contraseña,rol) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}',
        '{7}',('1'))""".format(request.json['cedula'], request.json['nombres'],
        request.json['telefono'], request.json['departamento'],
        request.json['ciudad'], request.json['direccion'], request.json['correo'],
        passhashRegistro)
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Usuario registrado"})
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

#ruta inicio de sesión


# @app.route('/')
# def home():
#     passhash = generate_password_hash('cairocoders')
#     print(passhash)
    # if 'correo' in session:
    #     correo = session['correo']
    #     return jsonify({'message' : 'You are already logged in', 'correo' : correo})
    # else:
    #     resp = jsonify({'message' : 'Unauthorized'})
    #     resp.status_code = 401
    #     return resp

@app.route('/login', methods=['POST'])
def login():
    _correo = request.json['correo']
    _contraseña = request.json['contraseña']
    if _correo and _contraseña:
        cursor=db.connection.cursor()
        sql="""SELECT cedula,correo,contraseña,rol FROM clientes WHERE correo = '{}'""".format(_correo) #comprueba si el correo existe
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is not None:
            cedula = row[0]
            correo = row[1]
            contraseña = row[2]
            rol = row[3]
        else:
            print("no existe el correo y/o la contraseña")
        if row:
            if check_password_hash(contraseña, _contraseña):
                session['correo'] = correo
                cursor.close()
                return jsonify(row)
            else:
                print(contraseña,_contraseña)
                resp = jsonify({'Mensaje' : 'Contraseña no valida'})
                resp.status_code = 400
                return resp
    else:
        resp = jsonify({'Mensaje' : 'Datos invalidos'})
        resp.status_code = 400
        return resp


#listar y editar datos de usuario
@app.route('/listarCliente/<cedula>', methods=['GET'])
def listarCliente(cedula):
    try:
        cursor=db.connection.cursor()
        sql=  "SELECT nombres,telefono,departamento,ciudad,direccion FROM clientes WHERE cedula ='{}'".format(cedula)
        cursor.execute(sql)
        row = cursor.fetchone()
        return jsonify({"Mensaje": row})
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/modificarCliente/<cedula>',methods=['PUT'])
def modificarCliente(cedula):
    cursor=db.connection.cursor()
    sql = f"""UPDATE clientes SET nombres = '{request.json['nombres']}',telefono = '{request.json['telefono']}',
    departamento = '{request.json['departamento']}', ciudad = '{request.json['ciudad']}',direccion = '{request.json['direccion']}'
    WHERE cedula = '{cedula}'"""
    cursor.execute(sql)
    db.connection.commit()
    return jsonify({"Mensaje": "Cliente modificado"})

#cierre de sesión
@app.route('/logout')
def logout():
    if 'correo' in session:
        session.pop('correo', None)
    return jsonify({"Mensaje": "Cerró sesión exitosamente"})

#CRUD productos
#agregar nuevo Producto
@app.route('/nuevoProducto', methods=['POST'])
def nuevoProducto():
    try:
        imagen = request.files['imagen']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        talla = request.form['talla']
        precio = request.form['precio']
        categoria = request.form['categoria']
        cantidad = request.form['cantidad']
        color = request.form['color']
        tallaje = request.form['tallaje']
        cursor=db.connection.cursor()
        file = uploadFile(imagen)
        sql = f"""INSERT INTO productos(imagenes,nombre,descripcion,talla,precio,categoria,cantidad,color,tallaje)
        VALUES  ('{file}','{nombre}','{descripcion}','{talla}','{precio}','{categoria}','{cantidad}','{color}','{tallaje}')"""
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Producto registrado"})
    except Exception as ex:
        return jsonify({"Mensaje": ex})


@app.route('/upload', methods=['POST'])
def uploadFile(url):
    try:
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
                return uploadResult['url']
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/listarProductos/<codigo>', methods=['GET'])
def listarProductos(codigo):
    try:
        cursor=db.connection.cursor()
        sql=  "SELECT * FROM productos where codigo='{}'".format(codigo)
        cursor.execute(sql)
        row = cursor.fetchone()
        return jsonify({"Mensaje": row})
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/modificarProducto/<codigo>',methods=['PUT'])
def modificarProducto(codigo):
    try:
        cursor=db.connection.cursor()
        sql = f"""UPDATE productos SET imagenes = '{request.json['imagenes']}',nombre = '{request.json['nombre']}',
        descripcion = '{request.json['descripcion']}', talla = '{request.json['talla']}',precio = '{request.json['precio']}',
        categoria = '{request.json['categoria']}',cantidad = '{request.json['cantidad']}',color = '{request.json['color']}',
        tallaje = '{request.json['tallaje']}' WHERE codigo = '{codigo}'"""
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Producto modificado"})
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/eliminarProducto/<codigo>',methods=['DELETE'])
def eliminarProducto(codigo):
    try:
        cursor=db.connection.cursor()
        sql = ('DELETE FROM productos where codigo = {0}'.format(codigo))
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Producto eliminado"})
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/homeProductos', methods=['GET'])
def homeProductos():
    try:
        cursor=db.connection.cursor()
        sql=  'SELECT * FROM productos'
        cursor.execute(sql)
        row = cursor.fetchall()
        return jsonify({"Mensaje": row})
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

#FiltroS categoria
@app.route('/filtrarCamiseta', methods=['GET'])
def filtrarCamiseta():
    try:
        cursor=db.connection.cursor()
        sql = ("SELECT * FROM productos WHERE categoria = 'Camiseta'")
        cursor.execute(sql)
        row = cursor.fetchall()
        db.connection.commit()
        return jsonify(row)
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/filtrarBuzo', methods=['GET'])
def filtrarBuzo():
    try:
        cursor=db.connection.cursor()
        sql = ("SELECT * FROM productos WHERE categoria = 'Buzo'")
        cursor.execute(sql)
        row = cursor.fetchall()
        db.connection.commit()
        return jsonify(row)
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/filtrarGorra', methods=['GET'])
def filtrarGorra():
    try:
        cursor=db.connection.cursor()
        sql = ("SELECT * FROM productos WHERE categoria = 'Gorra'")
        cursor.execute(sql)
        row = cursor.fetchall()
        db.connection.commit()
        return jsonify(row)
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/filtrarVaso', methods=['GET'])
def filtrarVaso():
    try:
        cursor=db.connection.cursor()
        sql = ("SELECT * FROM productos WHERE categoria = 'Vaso'")
        cursor.execute(sql)
        row = cursor.fetchall()
        db.connection.commit()
        return jsonify(row)
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})

@app.route('/filtrarBotella', methods=['GET'])
def filtrarBotella():
    try:
        cursor=db.connection.cursor()
        sql = ("SELECT * FROM productos WHERE categoria = 'Botella'")
        cursor.execute(sql)
        row = cursor.fetchall()
        db.connection.commit()
        return jsonify(row)
    except Exception as ex:
        return jsonify({"Mensaje": "Error"})









if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()

