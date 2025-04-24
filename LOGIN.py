import sys
from PyQt5 import QtWidgets, uic

#Iniciar la aplicación
app = QtWidgets.QApplication([])

#Cargar el archivo
Login = uic.loadUi("IniciarSesion.ui")

#Página por defecto
Login.stackedWidget.setCurrentWidget(Login.page)

#Funciones
def login():
    username = Login.Usuario.text()
    password = Login.Contrasena.text()
    if len(username) == 0 or len(password) == 0:
        Login.label_4.setText(" Por favor complete los campos.")
    elif username == "USER" and password == "1234":
        Login.stackedWidget.setCurrentWidget(Login.page_2)
        Login.Usuario.clear()
        Login.Contrasena.clear()
        Login.label_4.clear()
    elif username != "USER" and password == "1234":
        Login.label_4.setText(" Usuario incorrecto.")
        Login.Usuario.clear()
        Login.Contrasena.clear()
    elif password != "1234" and username == "USER":
        Login.label_4.setText(" Contraseña incorrecta.")
        Login.Usuario.clear()
        Login.Contrasena.clear()
    else:
        Login.label_4.setText(" Usuario y contraseña incorrectos.")
        Login.Usuario.clear()
        Login.Contrasena.clear()

def volver():
    Login.stackedWidget.setCurrentWidget(Login.page)

#Conectar Botón
Login.iniciarsesion.clicked.connect(login)

#Ejecutar
Login.show()
sys.exit(app.exec())