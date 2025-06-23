import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QComboBox, QCheckBox, QListWidgetItem
from PyQt5.QtCore import pyqtSlot, QDateTime
from PyQt5 import uic


# Estas clases representan el modelo y servicios
class Usuario:
    def __init__(self, correo, contraseña, nombre=None, telefono=None, edad=None,
                 genero=None, peso=None, altura=None, objetivo=None,
                 disponibilidad=None, estilo_vida=None, lugar_entrenamiento=None):
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
        self.lugar_entrenamiento = lugar_entrenamiento

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

            # Crear tabla de usuarios con todas las columnas desde el inicio
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
                estilo_vida TEXT,
                lugar_entrenamiento TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Verificar si existen las columnas y agregarlas solo si no existen
            cursor.execute("PRAGMA table_info(usuarios)")
            columnas_existentes = [columna[1] for columna in cursor.fetchall()]

            # Agregar columnas faltantes solo si no existen
            if 'lugar_entrenamiento' not in columnas_existentes:
                cursor.execute('ALTER TABLE usuarios ADD COLUMN lugar_entrenamiento TEXT')

            if 'fecha_registro' not in columnas_existentes:
                cursor.execute('ALTER TABLE usuarios ADD COLUMN fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP')

            # Insertar algunos usuarios de prueba si la tabla está vacía
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                # Usar DATETIME('now') para SQLite
                cursor.execute('''
                INSERT INTO usuarios (nombre, correo, contraseña, peso, altura, objetivo, fecha_registro)
                VALUES 
                    ("Usuario de Prueba", "usuario@ejemplo.com", "contraseña123", 70.0, 175.0, "Mantener peso", DATETIME('now')),
                    ("Usuario de Test", "test@gymsync.com", "test123", 65.0, 160.0, "Adelgazar", DATETIME('now'))
                ''')

            conn.commit()
            conn.close()
            print("Base de datos inicializada correctamente")

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

            # Insertar datos del usuario con fecha actual
            cursor.execute('''
            INSERT INTO usuarios (nombre, correo, contraseña, telefono, edad, genero, 
                                peso, altura, objetivo, disponibilidad, estilo_vida, 
                                lugar_entrenamiento, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))
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
                usuario.estilo_vida,
                usuario.lugar_entrenamiento
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
                # Crear usuario con los datos recuperados
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
                    estilo_vida=datos[11],
                    lugar_entrenamiento=datos[12] if len(datos) > 12 else None
                )
                return usuario

            return None

        except Exception as e:
            print(f"Error al recuperar usuario: {str(e)}")
            return None

    def calcular_dias_uso(self, correo):
        """Calcula los días desde el registro del usuario."""
        try:
            conn = sqlite3.connect(self.db_nombre)
            cursor = conn.cursor()

            # Verificar si la columna fecha_registro existe
            cursor.execute("PRAGMA table_info(usuarios)")
            columnas = [columna[1] for columna in cursor.fetchall()]

            if 'fecha_registro' not in columnas:
                conn.close()
                return 1  # Si no existe la columna, devolver 1 día

            cursor.execute(
                "SELECT fecha_registro FROM usuarios WHERE correo = ?",
                (correo,)
            )

            resultado = cursor.fetchone()
            conn.close()

            if resultado and resultado[0]:
                from datetime import datetime
                try:
                    fecha_registro = datetime.strptime(resultado[0], '%Y-%m-%d %H:%M:%S')
                    dias_uso = (datetime.now() - fecha_registro).days
                    return max(1, dias_uso)  # Mínimo 1 día
                except ValueError:
                    # Si hay error en el formato de fecha, devolver 1 día
                    return 1

            return 1  # Si no hay fecha, devolver 1 día

        except Exception as e:
            print(f"Error al calcular días de uso: {str(e)}")
            return 1


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
            self.abrir_pantalla_principal(usuario)
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

    def abrir_pantalla_principal(self, usuario):
        """Abre la pantalla principal con los datos del usuario."""
        try:
            self.main_screen = MainScreen(usuario)
            self.main_screen.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir la pantalla principal: {str(e)}")


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
        self.cargar_lugar_entrenamiento()
        self.cargar_genero()

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

    def cargar_lugar_entrenamiento(self):
        """Gestiona los lugares de entrenamiento."""
        # En una implementación real, esto podría ser una matriz de checkboxes o un widget más complejo
        # Para simplificar, usaremos un combobox con opciones predefinidas
        lugar_entrenamiento = [
            "Selecciona tu lugar de entrenamiento",
            "Casa sin equipamiento",
            "Casa con equipamiento",
            "Gimnasio"
        ]
        self.cmb_lugar_entrenamiento.clear()
        self.cmb_lugar_entrenamiento.addItems(lugar_entrenamiento)

    def cargar_genero(self):
        """Gestiona los géneros."""
        # En una implementación real, esto podría ser una matriz de checkboxes o un widget más complejo
        # Para simplificar, usaremos un combobox con opciones predefinidas
        genero = [
            "Selecciona tu género",
            "Masculino",
            "Femenino",
            "Otro"
        ]
        self.cmb_genero.clear()
        self.cmb_genero.addItems(genero)

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
        if self.cmb_genero.currentIndex() == 0:
            self.mostrar_error_validacion(
                "Campos incompletos",
                "Por favor, selecciona tu género."
            )
            return False

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

        if self.cmb_lugar_entrenamiento.currentIndex() == 0:
            self.mostrar_error_validacion(
                "Campos incompletos",
                "Por favor, selecciona tu lugar de entrenamiento."
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
            genero=self.cmb_genero.currentText(),
            peso=float(self.txt_peso.text()),
            altura=float(self.txt_altura.text()),
            objetivo=self.cmb_objetivo.currentText(),
            disponibilidad=self.cmb_disponibilidad.currentText(),
            estilo_vida=self.cmb_estilo_vida.currentText(),
            lugar_entrenamiento=self.cmb_lugar_entrenamiento.currentText()
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
        self.main_window = MainScreen(usuario)
        self.main_window.show()
        self.close()

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


class MainScreen(QMainWindow):
    def __init__(self, usuario):
        super(MainScreen, self).__init__()

        # Guardar referencia al usuario logueado
        self.usuario = usuario

        # Cargar el archivo UI de la pantalla principal
        uic.loadUi("main_screen.ui", self)

        # Inicializar el servicio de base de datos
        self.db_service = BaseDatosGymSync()

        # Configurar la pantalla con los datos del usuario
        self.configurar_pantalla_usuario()

        # Conectar señales a slots
        self.setupConnections()

    def setupConnections(self):
        """Configura las conexiones entre los widgets y los métodos."""
        # Conectar botones de la interfaz
        self.btn_datos_perfil.clicked.connect(self.abrir_datos_perfil)
        self.btn_expandir_progreso.clicked.connect(self.expandir_progreso)

    def configurar_pantalla_usuario(self):
        """Configura todos los elementos de la pantalla con los datos del usuario."""
        # Configurar información del perfil
        self.configurar_seccion_perfil()

        # Configurar sección de progreso
        self.configurar_seccion_progreso()

        # Configurar sesión de entrenamiento actual
        self.configurar_sesion_actual()

        # Configurar próximas sesiones
        self.configurar_proximas_sesiones()

        # Configurar notificaciones
        self.configurar_notificaciones()

    def configurar_seccion_perfil(self):
        """Configura la sección del perfil del usuario."""
        # Establecer el correo del usuario
        self.lbl_correo_usuario.setText(self.usuario.correo)

        # Configurar avatar (por ahora texto, después se puede cambiar por imagen)
        iniciales = self.obtener_iniciales(self.usuario.nombre)
        self.lbl_avatar_usuario.setText(iniciales)

    def configurar_seccion_progreso(self):
        """Configura la sección de progreso del usuario."""
        #Calcular días de uso
        dias_uso = self.db_service.calcular_dias_uso(self.usuario.correo)
        self.lbl_dias_uso.setText(str(dias_uso))

        # Calcular días para siguiente nivel (ejemplo: cada 30 días es un nivel)
        dias_siguiente_nivel = 30 - (dias_uso % 30)
        if dias_siguiente_nivel == 30:
            dias_siguiente_nivel = 0
        self.lbl_dias_siguiente_nivel.setText(str(dias_siguiente_nivel))

        # Mostrar diferencia de peso (simulado por ahora)
        diferencia_peso = self.calcular_diferencia_peso()
        self.lbl_diferencia_peso.setText(diferencia_peso)

    def configurar_sesion_actual(self):
        """Configura la sesión de entrenamiento actual."""
        # Obtener día actual
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_actual = QDateTime.currentDateTime().date().dayOfWeek()
        nombre_dia = dias_semana[dia_actual - 1]

        self.lbl_dia_actual.setText(nombre_dia)

        # Configurar tipo de sesión según el día y objetivo del usuario
        tipo_sesion = self.obtener_tipo_sesion(dia_actual)
        self.lbl_tipo_sesion_actual.setText(tipo_sesion)

        # Configurar ejercicios de la sesión actual
        self.configurar_ejercicios_actuales(tipo_sesion)

    def configurar_proximas_sesiones(self):
        """Configura las próximas sesiones de entrenamiento."""
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_actual = QDateTime.currentDateTime().date().dayOfWeek()

        # Configurar próxima sesión 1 (mañana)
        dia_proximo1 = (dia_actual % 7) + 1
        nombre_dia1 = dias_semana[dia_proximo1 - 1]
        self.lbl_dia_proximo1.setText(nombre_dia1)
        tipo_sesion1 = self.obtener_tipo_sesion(dia_proximo1)
        self.lbl_tipo_sesion_proximo1.setText(tipo_sesion1)

        #Configurar próxima sesión 2 (pasado mañana)
        dia_proximo2 = ((dia_actual + 1) % 7) + 1
        nombre_dia2 = dias_semana[dia_proximo2 - 1]
        self.lbl_dia_proximo2.setText(nombre_dia2)
        tipo_sesion2 = self.obtener_tipo_sesion(dia_proximo2)
        self.lbl_tipo_sesion_proximo2.setText(tipo_sesion2)

    def configurar_notificaciones(self):
        """Configura las notificaciones personalizadas."""
        notificaciones = self.generar_notificaciones_personalizadas()

        if len(notificaciones) > 0:
            self.lbl_notif_1.setText(f"• {notificaciones[0]}")
        if len(notificaciones) > 1:
            self.lbl_notif_2.setText(f"• {notificaciones[1]}")
        if len(notificaciones) > 2:
            self.lbl_notif_3.setText(f"• {notificaciones[2]}")

    def obtener_iniciales(self, nombre):
        """Obtiene las iniciales del nombre del usuario."""
        if not nombre:
            return "US"

        palabras = nombre.split()
        if len(palabras) >= 2:
            return f"{palabras[0][0]}{palabras[1][0]}".upper()
        else:
            return palabras[0][:2].upper()

    def calcular_diferencia_peso(self):
        """Calcula la diferencia de peso (simulado por ahora)."""
        # En una implementación real, esto vendría de un historial de pesos
        # Por ahora, simularemos basándose en el objetivo
        if self.usuario.objetivo == "Adelgazar":
            return "-2.3 kg"
        elif self.usuario.objetivo == "Ganar masa muscular":
            return "+1.8 kg"
        else:
            return "0.0 kg"

    def obtener_tipo_sesion(self, dia):
        """Obtiene el tipo de sesión según el día y objetivo del usuario."""
        tipos_push_pull_legs = {
            1: "PULL DAY",  # Lunes
            2: "PUSH DAY",  # Martes
            3: "LEGS DAY",  # Miércoles
            4: "PULL DAY",  # Jueves
            5: "PUSH DAY",  # Viernes
            6: "CARDIO",  # Sábado
            7: "DESCANSO"  # Domingo
        }

        tipos_cardio = {
            1: "CARDIO HIIT",
            2: "FUERZA",
            3: "CARDIO BAJO",
            4: "FUERZA",
            5: "CARDIO HIIT",
            6: "YOGA",
            7: "DESCANSO"
        }

        if self.usuario.objetivo in ["Adelgazar", "Mejorar resistencia"]:
            return tipos_cardio.get(dia, "ENTRENAMIENTO")
        else:
            return tipos_push_pull_legs.get(dia, "ENTRENAMIENTO")

    def configurar_ejercicios_actuales(self, tipo_sesion):
        """Configura la lista de ejercicios para la sesión actual."""
        ejercicios = self.obtener_ejercicios_por_tipo(tipo_sesion)

        # Limpiar la lista actual
        self.lista_ejercicios_actuales.clear()

        # Agregar ejercicios a la lista
        for ejercicio in ejercicios:
            item = QListWidgetItem(ejercicio)
            self.lista_ejercicios_actuales.addItem(item)

    def obtener_ejercicios_por_tipo(self, tipo_sesion):
        """Retorna una lista de ejercicios según el tipo de sesión."""
        ejercicios_por_tipo = {
            "PULL DAY": [
                "Pull-ups - 3x8-12",
                "Remo con barra - 3x8-10",
                "Dominadas asistidas - 3x6-8",
                "Curl de bíceps - 3x10-12",
                "Remo con mancuernas - 3x8-10"
            ],
            "PUSH DAY": [
                "Press de banca - 3x8-10",
                "Press militar - 3x8-10",
                "Flexiones - 3x10-15",
                "Fondos en paralelas - 3x8-12",
                "Press inclinado - 3x8-10"
            ],
            "LEGS DAY": [
                "Sentadillas - 3x10-12",
                "Peso muerto - 3x6-8",
                "Prensa de piernas - 3x12-15",
                "Zancadas - 3x10 c/pierna",
                "Elevación de gemelos - 3x15-20"
            ],
            "CARDIO HIIT": [
                "Calentamiento - 5 min",
                "Burpees - 30s ON/30s OFF x8",
                "Mountain climbers - 30s ON/30s OFF x8",
                "Jumping jacks - 30s ON/30s OFF x8",
                "Enfriamiento - 5 min"
            ],
            "CARDIO BAJO": [
                "Caminata rápida - 30 min",
                "Bicicleta estática - 20 min",
                "Elíptica - 15 min",
                "Estiramientos - 10 min"
            ],
            "FUERZA": [
                "Sentadilla con peso - 4x6-8",
                "Press de banca - 4x6-8",
                "Peso muerto - 4x5-6",
                "Press militar - 3x6-8",
                "Remo con barra - 3x6-8"
            ],
            "DESCANSO": [
                "Día de descanso activo",
                "Estiramientos suaves - 15 min",
                "Caminata ligera - 20 min",
                "Movilidad articular - 10 min"
            ]
        }

        return ejercicios_por_tipo.get(tipo_sesion, ["Entrenamiento personalizado"])

    def generar_notificaciones_personalizadas(self):
        """Genera notificaciones personalizadas según el usuario."""
        notificaciones = []

        # Notificación basada en el objetivo
        if self.usuario.objetivo == "Adelgazar":
            notificaciones.append("RECORDATORIO: Mantén tu déficit calórico")
        elif self.usuario.objetivo == "Ganar masa muscular":
            notificaciones.append("TIP: Consume suficiente proteína hoy")
        else:
            notificaciones.append("MOTIVACIÓN: ¡Sigue así, lo estás haciendo genial!")

        # Notificación basada en el IMC
        if hasattr(self.usuario, 'categoria_imc'):
            if self.usuario.categoria_imc == "Sobrepeso":
                notificaciones.append("SALUD: Considera aumentar tu actividad cardiovascular")
            elif self.usuario.categoria_imc == "Bajo peso":
                notificaciones.append("NUTRICIÓN: Asegúrate de comer suficientes calorías")

        # Notificación general
        notificaciones.append("HYDRATACIÓN: Recuerda beber agua regularmente")

        return notificaciones[:3]  # Máximo 3 notificaciones

    @pyqtSlot()
    def abrir_datos_perfil(self):
        """Abre una ventana con los datos detallados del perfil."""
        datos_perfil = f"""
        DATOS DEL PERFIL

        Nombre: {self.usuario.nombre}
        Correo: {self.usuario.correo}
        Teléfono: {self.usuario.telefono}
        Edad: {self.usuario.edad} años
        Género: {self.usuario.genero}
        Peso: {self.usuario.peso} kg
        Altura: {self.usuario.altura} cm

        OBJETIVOS Y PREFERENCIAS

        Objetivo: {self.usuario.objetivo}
        Disponibilidad: {self.usuario.disponibilidad}
        Estilo de vida: {self.usuario.estilo_vida}
        Lugar de entrenamiento: {self.usuario.lugar_entrenamiento}
        """

        if hasattr(self.usuario, 'imc'):
            datos_perfil += f"\nIMC: {self.usuario.imc} ({self.usuario.categoria_imc})"

        if hasattr(self.usuario, 'recomendacion'):
            datos_perfil += f"\nRecomendación: {self.usuario.recomendacion}"

        QMessageBox.information(self, "Datos del Perfil", datos_perfil)

    @pyqtSlot()
    def expandir_progreso(self):
        """Muestra el progreso detallado del usuario."""
        dias_uso = self.db_service.calcular_dias_uso(self.usuario.correo)
        nivel_actual = (dias_uso // 30) + 1


    



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