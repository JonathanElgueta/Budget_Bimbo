from .entities.User import User


class ModelUser():
    @classmethod
    def login(cls, db, user):
        try:
            cursor = db.cursor()
            sql = """SELECT ID_Usuario, Email, Contrasena, Nombre, Apellido FROM dbo.Usuario
                     WHERE Email = '{}'""".format(user.email)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is not None:
                user = User(row[0], row[1], row[2])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
