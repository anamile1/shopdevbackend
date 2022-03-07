# class Config:
#     SECRET_KEY = 'B!1w8NAt1T^%kvhUI*S^'

class DevelopmentConfig():
    DEBUG=True
    #Para iniciar el servidor en modo de depuración
    MYSQL_HOST= 'boappj44csi2jovaxmpy-mysql.services.clever-cloud.com'
    MYSQL_USER= 'un7wcwcqtgb6cod2'
    MYSQL_PASSWORD= 'e4HMan3wybvY2gD8S2X4'
    MYSQL_DB= 'boappj44csi2jovaxmpy'
    MYSQL_PORT= 3306
    #Conexión base de datos

#Diccionario
config = {
    'development': DevelopmentConfig
}