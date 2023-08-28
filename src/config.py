class Config:
    SECRET_KEY = 'B!1w8NAt1T^%kvhUI*S^'
    MSSQL_PASSWORD = '76264238Je'  # Agrega tu contraseña aquí


class DevelopmentConfig(Config):
    DEBUG = True
    MSSQL_SERVER = 'proyectos-bimbo-server.database.windows.net'
    MSSQL_DATABASE = 'Vtas_Autoservicios'
    MSSQL_USERNAME = 'Administrador'
    # Cambiar a 'no' ya que estás usando usuario y contraseña
    MSSQL_TRUSTED_CONNECTION = 'no'


config = {
    'development': DevelopmentConfig
}
