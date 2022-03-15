import os
import MySQLdb
import cloudinary
import cloudinary.uploader
from flask import Flask, jsonify, request, session
from flask_mysqldb import MySQL
from config import config
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
            correo = row[1]
            contraseña = row[2]
        else:
            print("no existe el correo y/o la contraseña")
        if row:
            if check_password_hash(contraseña, _contraseña):
                session['correo'] = correo
                cursor.close()
                consultaUsuario={'cedula':row[0], 'correo':row[1], 'contraseña':row[2], 'rol':row[3]}
                return jsonify(consultaUsuario)
            else:
                print(contraseña,_contraseña)
                resp = jsonify({'Mensaje' : 'Contraseña no valida'})
                resp.status_code = 400
                return resp
    else:
        resp = jsonify({'Mensaje' : 'row invalidos'})
        resp.status_code = 400
        return resp

#listar y editar datos de usuario
@app.route('/listarCliente/<string:cedula>', methods=['GET'])
def listarCliente(cedula):
    try:
        cursor=db.connection.cursor()
        sql=  "SELECT nombres,telefono,departamento,ciudad,direccion FROM clientes WHERE cedula ='{}'".format(cedula)
        cursor.execute(sql)
        row = cursor.fetchone()
        consultaCliente = []
        consultaCliente.append({"nombres":row[0], "telefono":row[1], "departamento":row[2], 
        "ciudad":row[3], "direccion":row[4]})
        return jsonify({"Mensaje": consultaCliente})
    except Exception as ex:
        return jsonify({"Mensaje": ex})

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
        cursor=db.connection.cursor()
        file = uploadFile(imagen)
        sql = f"""INSERT INTO productos(imagenes,nombre,descripcion,talla,precio,categoria,cantidad,color)
        VALUES  ('{file}','{nombre}','{descripcion}','{talla}','{precio}','{categoria}','{cantidad}','{color}')"""
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Producto registrado"})
    except Exception as ex:
        return jsonify({"Mensaje": ex})
    

@app.route('/modificarProducto/<codigo>',methods=['PUT'])
def modificarProducto(codigo):
    try:
        imagen = request.files['imagen']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        talla = request.form['talla']
        precio = request.form['precio']
        categoria = request.form['categoria']
        cantidad = request.form['cantidad']
        color = request.form['color']
        cursor=db.connection.cursor()
        file = uploadFile(imagen)
        cursor=db.connection.cursor()
        sql = f"""UPDATE productos SET imagenes = '{file}',nombre = '{nombre}',
        descripcion = '{descripcion}', talla = '{talla}',precio = '{precio}',
        categoria = '{categoria}',cantidad = '{cantidad}',color = '{color}'
        WHERE codigo = '{codigo}'"""
        print(sql)
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Producto modificado"})
    except Exception as ex:
        return jsonify({"Mensaje": ex})


@app.route('/upload', methods=['POST','PUT'])
def uploadFile(url):
    try:
        app.logger.info('in upload route')
        cloudinary.config(cloud_name = os.getenv('CLOUD_NAME'),
        api_key = os.getenv('API_KEY'),
        api_secret = os.getenv('API_SECRET'))
        uploadResult = None
        fileToUpload = url
        app.logger.info('fileToUpload')
        if fileToUpload:
            uploadResult =cloudinary.uploader.upload(fileToUpload)
            app.logger.info('uploadResult')
            return uploadResult['url']
    except Exception as ex:
        return jsonify({"Mensaje": ex})

@app.route('/listarProducto/<string:codigo>', methods=['GET'])
def listarProductos(codigo):
    try:
        cursor=db.connection.cursor()
        sql=  "SELECT * FROM productos where codigo='{}'".format(codigo)
        cursor.execute(sql)
        row = cursor.fetchone()        
        consultaProducto = []
        consultaProducto.append({"codigo":row[0], "imagenes":row[1], "nombre":row[2], "descripcion":row[3], 
        "talla":row[4], "precio":row[5], "categoria":row[6], "cantidad":row[7], "color":row[8]})
        return jsonify({"Consulta Producto": consultaProducto})
    except Exception as ex:
        return jsonify({"Mensaje": ex})

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
        productos =[]
        for i in row:
            productos.append({"codigo":i[0], "imagenes":i[1], "nombre":i[2], "descripcion":i[3], 
            "talla":i[4], "precio":i[5], "categoria":i[6], "cantidad":i[7], "color":i[8]})
        return jsonify({"Mensaje": productos})
    except Exception as ex:
        return jsonify({"Lista de productos": "Error"})

#FiltroS categoria
@app.route('/filtrarCategoria', methods=['GET'])
def filtrarCamiseta():
    try:
        cursor=db.connection.cursor()
        sql = ("SELECT * FROM productos WHERE categoria = 'Camiseta' or 'Buzo' or 'Gorra' or 'Vaso' or 'Botella'")
        cursor.execute(sql)
        row = cursor.fetchall()
        db.connection.commit()
        filtro = []
        for i in row:
            filtro.append({"codigo":i[0], "imagenes":i[1], "nombre":i[2], "descripcion":i[3], 
            "talla":i[4], "precio":i[5], "categoria":i[6], "cantidad":i[7], "color":i[8]})
        return jsonify(filtro)
    except Exception as ex:
        return jsonify({"Mensaje": ex})


#seccion de gestion del carrito = listar - seleccionar unidad - delete - edit - resgistrar - subTotal
@app.route('/ingresarProductoCarrito', methods=['POST']) 
def ingresarProductoCarrito():
    #en esta ruta podre ingresar un producto mas al carrito
    try:
        cursor = db.connection.cursor()
        sql="""INSERT INTO carrito(idProducto, cantidad, precioUni, imagen, nombre, descripcion, talla, idCliente, categoria) 
        VALUES ('{}','{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(request.json['idProducto'], request.json['cantidad'],
        request.json['precioUni'],request.json['imagen'],request.json['nombre'], request.json['descripcion'], request.json['talla'],
        request.json['idCliente'], request.json['categoria'])
        cursor.execute(sql)
        db.connection.commit()
        ingresarProducto={'cedula':row[0], 'correo':row[1], 'contraseña':row[2], 'rol':row[3]}
        return jsonify({'mensaje':"Producto ingresado al carrito"})
    except Exception as ex:
        #mostrar  el error
        return jsonify({'mensaje':str(ex)})

@app.route('/listarCarritoCompras/<idCliente>', methods=['GET']) #lista
def listarCarrito(idCliente):
    #en esta ruta deplagare la informacion inicial que va a mostrar el carrito
    try: 
        cursor=db.connection.cursor()
        sql="SELECT * FROM carrito WHERE idCliente ='{0}'".format(idCliente)
        cursor.execute(sql)
        row=cursor.fetchall()
        #confirmacion de consulta        
        listarCarrito =[]
        for i in row:
            listarCarrito.append({"id":i[0], "idProducto":i[1], "cantidad":i[2], "precioUni":i[3], 
            "imagen":i[4], "nombre":i[5], "descripcion":i[6], "talla":i[7], "idCliente":i[8], "categoria":i[9]})
        return jsonify({'Lista de':listarCarrito, 'mensaje': "Carrito listado."})
    except Exception as ex:
        #mostrar el error
        return jsonify({'mensaje':str(ex)})

@app.route('/actualizaProductoCarrito', methods=['PUT'])
def actualizar_cantidad():
    #en esta funcion puedo actualizar la cantidad del producto del carrito
    try:
        cursor = db.connection.cursor()
        sql = "UPDATE carrito SET cantidad = '{0}' WHERE id = '{1}'".format(request.json['cantidad'], request.json['id'])
        cursor.execute(sql)
        db.connection.commit()  # Confirma la acción de actualización.
        return jsonify({'mensaje': "Producto actualizado."})
    except Exception as ex:
            return jsonify({'mensaje':str(ex)})

@app.route('/guardarPedidos/<id>', methods=['POST', 'DELETE'])
def enviarPedidos(id):
    try:
        cursor= db.connection.cursor()
        if request.method == 'POST':
        #enviar pedidos de la tabla carrito a tabla pedidos
            sql="INSERT INTO pedidos(id_cliente, id_producto, total) SELECT idCliente, idProducto, sum(cantidad * precioUni) FROM carrito WHERE idCliente ='{0}'".format(id)
            cursor.execute(sql)
        else:
        #limpiar datos de la tabla carrito
            sql2="DELETE FROM carrito WHERE idCliente ='{0}'".format(id)
            cursor.execute(sql2)
        db.connection.commit()
        return("funciona")
        # return jsonify({'pedidos registrados exitosamente'})
    except Exception as ex:
        return jsonify({'mensaje':str(ex)})

@app.route('/eliminarProductoCarrito/<idCarrito>', methods=['DELETE'])
def eliminarProductoCarrito(id):
    try:
        cursor = db.connection.cursor()
        sql = "DELETE FROM carrito WHERE id ='{0}'".format(id)
        cursor.execute(sql)
        db.connection.commit()  # Confirma la acción de eliminación.
        return jsonify({'mensaje': "Producto eliminado.", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje':str(ex)})

@app.route('/listarPedidos', methods=["GET"])
def listarPedidos():
    try: 
        cursor=db.connection.cursor()
        sql="SELECT* FROM pedidos"
        cursor.execute(sql)
        row=cursor.fetchall()    
        listarPedidos = []   
        for i in row:
            listarPedidos.append({"idPedido":i[0], "idCliente":i[1], "idProducto":i[2], "total":i[3], 
            "estado":i[4]})
            return jsonify(listarPedidos)
        else:
            return "none"
    except Exception as ex:
        #mostrar el error
        return jsonify({'mensaje':str(ex)})

@app.route('/eliminarPedido/<id_pedido>',methods=['DELETE'])
def eliminarPedido(id_pedido):
    try:
        cursor=db.connection.cursor()
        sql = ('DELETE FROM pedidos where id_pedido = {0}'.format(id_pedido))
        cursor.execute(sql)
        db.connection.commit()
        return jsonify({"Mensaje": "Pedido eliminado"})
    except Exception as ex:
        return jsonify({"Mensaje": ex})

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()

