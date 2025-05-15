import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QComboBox, QCheckBox
from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic


# Estas clases representan el modelo y servicios
class Usuario:
    def __init__(self, correo, contraseña, nombre=None, telefono=None, edad=None,
                 genero=None, peso=None, altura=None, objetivo=None,
                 disponibilidad=None, estilo_vida=None):
        self.correo = correo
        self.contraseña = contraseña
        self.nombre = nombre
        self.telefono = telefono
        self.edad = edad
        self.genero = genero
        self.peso = peso
        self.altura = altura
        self.objetivo = objetivo
        self.disponibilidad = disponibilidad
        self.estilo_vida = estilo_vida

        # Calcular IMC si altura y peso están disponibles
        if peso and altura:
            altura_m = altura / 100  # Convertir cm a m
            self.imc = round(peso / (altura_m * altura_m), 2)

            # Determinar categoría de IMC
            if self.imc < 18.5:
                self.categoria_imc = 'Bajo peso'
            elif self.imc < 25:
                self.categoria_imc = 'Peso normal'
            elif self.imc < 30:
                self.categoria_imc = 'Sobrepeso'
            else:
                self.categoria_imc = 'Obesidad'

            # Generar recomendaciones básicas según el objetivo
            if objetivo == 'Adelgazar':
                self.recomendacion = 'Enfoque en déficit calórico y ejercicio cardiovascular'
            elif objetivo == 'Ganar masa muscular':
                self.recomendacion = 'Enfoque en superávit calórico y entrenamiento de fuerza'
            elif objetivo == 'Mantener peso':
                self.recomendacion = 'Equilibrio entre ingesta calórica y ejercicio regular'
            else:
                self.recomendacion = 'Programa personalizado según objetivo específico'


class BaseDatosGymSync:
    def __init__(self, db_nombre='gymsync.db'):
        self.db_nombre = db_nombre
        self.inicializar_bd()

    def inicializar_bd(self):
        """Crea las tablas necesarias si no existen."""
        try:
            conn = sqlite3.connect(self.db_nombre)
            cursor = conn.cursor()

            # Crear tabla de usuarios si no existe
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT UNIQUE NOT NULL,
                contraseña TEXT NOT NULL,
                telefono TEXT,
                edad INTEGER,
                genero TEXT,
                peso REAL,
                altura REAL,
                objetivo TEXT,
                disponibilidad TEXT,
                estilo_vida TEXT
            )
            ''')

            # Insertar algunos usuarios de prueba si la tabla está vacía
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                INSERT INTO usuarios (nombre, correo, contraseña)
                VALUES 
                    ("Usuario de Prueba", "usuario@ejemplo.com", "contraseña123"),
                    ("Usuario de Test", "test@gymsync.com", "test123")
                ''')

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error al inicializar la base de datos: {str(e)}")

    def validar_credenciales(self, correo, contraseña):
        """Verifica si las credenciales ingresadas corresponden a un usuario registrado."""
        try:
            conn = sqlite3.connect(self.db_nombre)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM usuarios WHERE correo = ? AND contraseña = ?",
                (correo, contraseña)
            )

            usuario = cursor.fetchone()
            conn.close()

            return usuario is not None

        except Exception as e:
            print(f"Error al validar credenciales: {str(e)}")
            return False

    def guardar_usuario(self, usuario):
        """Guarda un nuevo usuario en la base de datos."""
        try:
            conn = sqlite3.connect(self.db_nombre)
            cursor = conn.cursor()

            # Insertar datos del usuario
            cursor.execute('''
            INSERT INTO usuarios (nombre, correo, contraseña, telefono, edad, genero, 
                                peso, altura, objetivo, disponibilidad, estilo_vida)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                usuario.nombre,
                usuario.correo,
                usuario.contraseña,
                usuario.telefono,
                usuario.edad,
                usuario.genero,
                usuario.peso,
                usuario.altura,
                usuario.objetivo,
                usuario.disponibilidad,
                usuario.estilo_vida
            ))

            # Guardar cambios y cerrar conexión
            conn.commit()
            conn.close()

            return True

        except sqlite3.IntegrityError:
            # Error de duplicación de correo (UNIQUE constraint)
            return False

        except Exception as e:
            print(f"Error al guardar usuario: {str(e)}")
            return False

    def obtener_usuario_por_correo(self, correo):
        """Recupera toda la información de un usuario por su correo."""
        try:
            conn = sqlite3.connect(self.db_nombre)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM usuarios WHERE correo = ?",
                (correo,)
            )

            datos = cursor.fetchone()
            conn.close()

            if datos:
                # Asumimos que el orden de las columnas coincide con la estructura de Usuario
                usuario = Usuario(
                    correo=datos[2],
                    contraseña=datos[3],
                    nombre=datos[1],
                    telefono=datos[4],
                    edad=datos[5],
                    genero=datos[6],
                    peso=datos[7],
                    altura=datos[8],
                    objetivo=datos[9],
                    disponibilidad=datos[10],
                    estilo_vida=datos[11]
                )
                return usuario

            return None

        except Exception as e:
            print(f"Error al recuperar usuario: {str(e)}")
            return None


class LoginScreen(QMainWindow):
    def __init__(self):
        super(LoginScreen, self).__init__()

        # Cargar el archivo UI diseñado con Qt Designer
        uic.loadUi("login_screen.ui", self)

        # Inicializar el servicio de base de datos
        self.db_service = BaseDatosGymSync()

        # Conectar señales a slots
        self.setupConnections()

    def setupConnections(self):
        """Configura las conexiones entre los widgets y los métodos."""
        # Los nombres de los objetos en el archivo UI son:
        # - btn_iniciar_sesion: para el botón "Iniciar sesión"
        # - lnk_registrate: para el enlace "Regístrate"
        # - txt_correo: para el campo de correo
        # - txt_contraseña: para el campo de contraseña

        self.btn_iniciar_sesion.clicked.connect(self.iniciar_sesion)
        self.lnk_registrate.linkActivated.connect(self.abrir_pantalla_registro)

    @pyqtSlot()
    def iniciar_sesion(self):
        """Se ejecuta al hacer clic en el botón 'Iniciar sesión'."""
        # Verificamos que los campos no estén vacíos
        if not self.comprobar_campos_requeridos():
            return

        correo = self.txt_correo.text()
        contraseña = self.txt_contraseña.text()

        if self.db_service.validar_credenciales(correo, contraseña):
            # Usuario autenticado correctamente
            usuario = self.db_service.obtener_usuario_por_correo(correo)
            nombre_mostrar = usuario.nombre if usuario and usuario.nombre else correo

            QMessageBox.information(self, "Éxito", f"Bienvenido a GymSync, {nombre_mostrar}")
            # En una aplicación real, aquí se cargaría la pantalla principal
            # self.abrir_pantalla_principal(usuario)
        else:
            # Credenciales incorrectas
            self.mostrar_error_autenticacion()

    def comprobar_campos_requeridos(self):
        """Verifica que no haya campos vacíos antes de enviar."""
        correo = self.txt_correo.text()
        contraseña = self.txt_contraseña.text()

        if not correo or not contraseña:
            QMessageBox.warning(self, "Campos incompletos",
                                "Por favor, rellena todos los campos.")
            return False

        return True

    def mostrar_error_autenticacion(self):
        """Muestra mensajes de error si las credenciales son incorrectas."""
        QMessageBox.critical(self, "Error de autenticación",
                             "Correo o contraseña incorrectos. Por favor, intenta de nuevo.")

    @pyqtSlot(str)
    def abrir_pantalla_registro(self, link):
        """Se activa al hacer clic en 'Regístrate', abre la pantalla de registro."""
        self.registro_screen = RegistroScreen(self)
        self.registro_screen.show()
        self.hide()


class RegistroScreen(QMainWindow):
    def __init__(self, login_screen=None):
        super(RegistroScreen, self).__init__()

        # Guardar referencia a la pantalla de login para volver a ella
        self.login_screen = login_screen

        # Cargar el archivo UI diseñado con Qt Designer
        uic.loadUi("registro_screen.ui", self)

        # Inicializar el servicio de base de datos
        self.db_service = BaseDatosGymSync()

        # Cargar las opciones de los desplegables
        self.cargar_opciones_objetivo()
        self.cargar_disponibilidad_horaria()
        self.cargar_estilos_vida()

        # Conectar señales a slots
        self.setupConnections()

    def setupConnections(self):
        """Configura las conexiones entre los widgets y los métodos."""
        # Suponiendo que los nombres de los objetos en el archivo UI son:
        # - btn_guardar: para el botón "GUARDAR"
        # - btn_salir: para el icono de salida

        self.btn_guardar.clicked.connect(self.registrar_usuario)
        self.btn_salir.clicked.connect(self.volver_a_login)

    def cargar_opciones_objetivo(self):
        """Carga las opciones del desplegable de objetivos."""
        objetivos = [
            "Selecciona un objetivo",
            "Adelgazar",
            "Mantener peso",
            "Ganar masa muscular",
            "Mejorar resistencia",
            "Tonificar",
            "Preparación para competición"
        ]
        self.cmb_objetivo.clear()
        self.cmb_objetivo.addItems(objetivos)

    def cargar_disponibilidad_horaria(self):
        """Gestiona las opciones de disponibilidad para cada día de la semana."""
        # En una implementación real, esto podría ser una matriz de checkboxes o un widget más complejo
        # Para simplificar, usaremos un combobox con opciones predefinidas
        disponibilidad = [
            "Selecciona tu disponibilidad",
            "Lunes a Viernes (mañanas)",
            "Lunes a Viernes (tardes)",
            "Solo fines de semana",
            "Lunes, Miércoles y Viernes (todo el día)",
            "Martes y Jueves (todo el día)",
            "Todos los días (flexible)"
        ]
        self.cmb_disponibilidad.clear()
        self.cmb_disponibilidad.addItems(disponibilidad)

    def cargar_estilos_vida(self):
        """Carga las opciones de estilo de vida en el desplegable correspondiente."""
        estilos_vida = [
            "Selecciona tu estilo de vida",
            "Sedentario (poco o nada de ejercicio)",
            "Ligeramente activo (ejercicio ligero 1-3 días/semana)",
            "Moderadamente activo (ejercicio moderado 3-5 días/semana)",
            "Muy activo (ejercicio intenso 6-7 días/semana)",
            "Extremadamente activo (ejercicio intenso diario o físicamente exigente)"
        ]
        self.cmb_estilo_vida.clear()
        self.cmb_estilo_vida.addItems(estilos_vida)

    @pyqtSlot()
    def registrar_usuario(self):
        """Método principal que coordina el proceso de registro completo."""
        # Primero validamos todos los campos obligatorios
        if not self.validar_campos_obligatorios():
            return

        # Luego validamos que las contraseñas coincidan
        contraseña = self.txt_contraseña.text()
        confirmacion = self.txt_confirmar_contraseña.text()

        if not self.confirmar_contraseñas_iguales(contraseña, confirmacion):
            self.mostrar_error_validacion(
                "Error de contraseña",
                "Las contraseñas no coinciden. Por favor, verifica."
            )
            return

        # Si todo está correcto, generamos el perfil y guardamos los datos
        try:
            # Crear objeto de usuario
            usuario = self.crear_objeto_usuario()

            # Guardar datos en la base de datos
            if self.db_service.guardar_usuario(usuario):
                QMessageBox.information(
                    self,
                    "Registro exitoso",
                    f"¡Bienvenido/a a GymSync, {usuario.nombre}!\n\nTu cuenta ha sido creada correctamente."
                )

                # Redirigir a la pantalla principal
                self.redirigir_a_pantalla_principal(usuario)
            else:
                self.mostrar_error_validacion(
                    "Error de registro",
                    "Ya existe una cuenta con este correo electrónico. Por favor, utiliza otro correo."
                )

        except Exception as e:
            self.mostrar_error_validacion(
                "Error en el registro",
                f"Ha ocurrido un error al registrar el usuario: {str(e)}"
            )

    def validar_campos_obligatorios(self):
        """Verifica que todos los campos requeridos estén completados."""
        # Validamos los campos de texto
        campos_texto = {
            "Nombre y apellidos": self.txt_nombre.text(),
            "Correo": self.txt_correo.text(),
            "Contraseña": self.txt_contraseña.text(),
            "Confirmar contraseña": self.txt_confirmar_contraseña.text(),
            "Número de teléfono": self.txt_telefono.text(),
            "Edad": self.txt_edad.text(),
            "Género": self.txt_genero.text(),
            "Peso": self.txt_peso.text(),
            "Altura": self.txt_altura.text()
        }

        # Verificar que no haya campos de texto vacíos
        for campo, valor in campos_texto.items():
            if not valor:
                self.mostrar_error_validacion(
                    "Campos incompletos",
                    f"El campo '{campo}' es obligatorio. Por favor, complétalo."
                )
                return False

        # Validamos los desplegables (que no estén en la opción default)
        if self.cmb_objetivo.currentIndex() == 0:
            self.mostrar_error_validacion(
                "Campos incompletos",
                "Por favor, selecciona un objetivo."
            )
            return False

        if self.cmb_disponibilidad.currentIndex() == 0:
            self.mostrar_error_validacion(
                "Campos incompletos",
                "Por favor, selecciona tu disponibilidad de horario."
            )
            return False

        if self.cmb_estilo_vida.currentIndex() == 0:
            self.mostrar_error_validacion(
                "Campos incompletos",
                "Por favor, selecciona tu estilo de vida."
            )
            return False

        # Validamos formato de correo (básico)
        if "@" not in campos_texto["Correo"] or "." not in campos_texto["Correo"]:
            self.mostrar_error_validacion(
                "Formato incorrecto",
                "Por favor, introduce un correo electrónico válido."
            )
            return False

        # Validamos que edad, peso y altura sean numéricos
        try:
            edad = int(campos_texto["Edad"])
            if edad <= 0 or edad > 120:
                raise ValueError("La edad debe estar entre 1 y 120 años.")

            peso = float(campos_texto["Peso"])
            if peso <= 0 or peso > 300:
                raise ValueError("El peso debe estar entre 1 y 300 kg.")

            altura = float(campos_texto["Altura"])
            if altura <= 0 or altura > 250:
                raise ValueError("La altura debe estar entre 1 y 250 cm.")

        except ValueError as e:
            self.mostrar_error_validacion("Formato incorrecto", str(e))
            return False

        return True

    def confirmar_contraseñas_iguales(self, contraseña, confirmacion):
        """Comprueba que ambas contraseñas coincidan."""
        return contraseña == confirmacion

    def crear_objeto_usuario(self):
        """Crea un objeto Usuario con los datos del formulario."""
        return Usuario(
            correo=self.txt_correo.text(),
            contraseña=self.txt_contraseña.text(),
            nombre=self.txt_nombre.text(),
            telefono=self.txt_telefono.text(),
            edad=int(self.txt_edad.text()),
            genero=self.txt_genero.text(),
            peso=float(self.txt_peso.text()),
            altura=float(self.txt_altura.text()),
            objetivo=self.cmb_objetivo.currentText(),
            disponibilidad=self.cmb_disponibilidad.currentText(),
            estilo_vida=self.cmb_estilo_vida.currentText()
        )

    def redirigir_a_pantalla_principal(self, usuario):
        """Cambia a la pantalla principal tras un registro exitoso."""
        # En una aplicación real, aquí cerraríamos esta ventana y se abriría la principal
        # pasando la información del usuario recién registrado

        QMessageBox.information(
            self,
            "Navegación",
            f"Redirigiendo a la pantalla principal...\n"
            f"¡Bienvenido/a a GymSync, {usuario.nombre}!"
        )

        # Código para cambiar de pantalla (comentado porque depende de la estructura de la app)
        # self.main_window = MainScreen(usuario)
        # self.main_window.show()
        # self.close()

    def mostrar_error_validacion(self, tipo_error, mensaje):
        """Muestra errores específicos cuando la validación falla."""
        QMessageBox.warning(self, tipo_error, mensaje)

    def volver_a_login(self):
        """Vuelve a la pantalla de inicio de sesión."""
        if self.login_screen:
            self.login_screen.show()
            self.close()
        else:
            # Si no hay referencia a login_screen, crear una nueva instancia
            self.login_window = LoginScreen()
            self.login_window.show()
            self.close()


# Clase principal para manejar la navegación entre pantallas
class GymSyncApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.mostrar_login()

    def mostrar_login(self):
        self.login_screen = LoginScreen()
        self.login_screen.show()

    def ejecutar(self):
        return self.app.exec_()


# Este es el código necesario para ejecutar la aplicación
def main():
    app = GymSyncApp()
    sys.exit(app.ejecutar())


if __name__ == '__main__':
    main()