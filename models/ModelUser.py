# from .entities.User import User
# from flask import jsonify

# class ModelUser():

#     @classmethod
#     #datos para autenticación
#     def login(self,db,user):
#         #por si ocurre una excepción 
#         try:
#             #permite interactuar con la base de datos
#             cursor=db.connection.cursor()
#             sql="""SELECT cedula,nombres,telefono,departamento,ciudad,direccion,correo,contraseña
#                 FROM clientes WHERE correo = '{}' and contraseña = '{}'""".format(user.correo,user.contraseña) #comprueba si el correo existe
#             cursor.execute(sql)
#             row = cursor.fetchone()
#             if row != None:
#                 return jsonify(row)
#             else:
#                 return jsonify({"Mensaje": "Datos invalidos"})             

#         except Exception as ex:
#             raise Exception(ex)

        
#     @classmethod
#     #datos para autenticación
#     def get_by_cedula(self,db,cedula):
#         #por si ocurre una excepción 
#         try:
#             #permite interactuar con la base de datos
#             cursor=db.connection.cursor()
#             sql="""SELECT cedula,nombres,telefono,departamento,ciudad,direccion,correo
#                 FROM clientes WHERE cedula = '{}'""".format(cedula)#comprueba si el correo existe
#             cursor.execute(sql)
#             row = cursor.fetchone()
#             if row != None:
#                 return jsonify(row)
#             else:
#                 return jsonify({"Mensaje": "Datos invalidos"})              

#         except Exception as ex:
#             raise Exception(ex)
