import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QComboBox, QCheckBox, QListWidgetItem
from PyQt5.QtCore import pyqtSlot, QDateTime
from PyQt5 import uic
from datetime import datetime


class Usuario:
    def __init__(self, correo, contraseña, nombre=None, telefono=None, edad=None,
                 genero=None, peso=None, altura=None, objetivo=None,
                 disponibilidad=None, estilo_vida=None, lugar_entrenamiento=None, fecha_registro=None):
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
        self.fecha_registro = fecha_registro

        # Calcular IMC si altura y peso están disponibles
        if peso and altura:
            altura_m = altura / 100  # Convertir cm a m
            self.imc = round(peso / (altura_m * altura_m), 2)

            if self.imc < 18.5:
                self.categoria_imc = 'Bajo peso'
            elif self.imc < 25:
                self.categoria_imc = 'Peso normal'
            elif self.imc < 30:
                self.categoria_imc = 'Sobrepeso'
            else:
                self.categoria_imc = 'Obesidad'

import sqlite3
from datetime import datetime

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
                estilo_vida TEXT,
                lugar_entrenamiento TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            cursor.execute("PRAGMA table_info(usuarios)")
            columnas = [columna[1] for columna in cursor.fetchall()]

            if 'lugar_entrenamiento' not in columnas:
                cursor.execute('ALTER TABLE usuarios ADD COLUMN lugar_entrenamiento TEXT')

            if 'fecha_registro' not in columnas:
                cursor.execute('ALTER TABLE usuarios ADD COLUMN fecha_registro DATETIME')

                cursor.execute('''
                    UPDATE usuarios 
                    SET fecha_registro = DATETIME('now') 
                    WHERE fecha_registro IS NULL
                ''')

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")

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

        except Exception:
            return False

    def guardar_usuario(self, usuario):
        """Guarda un nuevo usuario en la base de datos."""
        try:
            conn = sqlite3.connect(self.db_nombre)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM usuarios WHERE correo = ?", (usuario.correo,))
            if cursor.fetchone():
                conn.close()
                print(f"El usuario con correo {usuario.correo} ya existe")
                return False
            if hasattr(usuario, 'fecha_registro') and usuario.fecha_registro:
                fecha_registro = usuario.fecha_registro
            else:
                fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
            INSERT INTO usuarios (nombre, correo, contraseña, telefono, edad, genero, 
                                peso, altura, objetivo, disponibilidad, estilo_vida, lugar_entrenamiento, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                usuario.lugar_entrenamiento,
                fecha_registro
            ))

            conn.commit()
            conn.close()

            return True

        except sqlite3.IntegrityError:
            return False

        except Exception as e:
            print(f"Error al guardar usuario: {e}")
            return False

    def actualizar_usuario(self, usuario):
        """Actualiza los datos de un usuario existente en la base de datos."""
        try:
            conn = sqlite3.connect(self.db_nombre)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM usuarios WHERE correo = ?", (usuario.correo,))
            if not cursor.fetchone():
                conn.close()
                print(f"El usuario con correo {usuario.correo} no existe")
                return False

            cursor.execute('''
            UPDATE usuarios SET 
                nombre = ?,
                contraseña = ?,
                telefono = ?,
                edad = ?,
                genero = ?,
                peso = ?,
                altura = ?,
                objetivo = ?,
                disponibilidad = ?,
                estilo_vida = ?,
                lugar_entrenamiento = ?
            WHERE correo = ?
            ''', (
                usuario.nombre,
                usuario.contraseña,
                usuario.telefono,
                usuario.edad,
                usuario.genero,
                usuario.peso,
                usuario.altura,
                usuario.objetivo,
                usuario.disponibilidad,
                usuario.estilo_vida,
                usuario.lugar_entrenamiento,
                usuario.correo  # WHERE correo = ?
            ))
            if cursor.rowcount == 0:
                conn.close()
                print(f"No se pudo actualizar el usuario con correo {usuario.correo}")
                return False

            conn.commit()
            conn.close()

            print(f"Usuario {usuario.correo} actualizado correctamente")
            return True

        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
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
                usuario = Usuario(
                    correo=datos[2],
                    contraseña=datos[3],
                    nombre=datos[1],
                    telefono=datos[4] if len(datos) > 4 else None,
                    edad=datos[5] if len(datos) > 5 else None,
                    genero=datos[6] if len(datos) > 6 else None,
                    peso=datos[7] if len(datos) > 7 else None,
                    altura=datos[8] if len(datos) > 8 else None,
                    objetivo=datos[9] if len(datos) > 9 else None,
                    disponibilidad=datos[10] if len(datos) > 10 else None,
                    estilo_vida=datos[11] if len(datos) > 11 else None,
                    lugar_entrenamiento=datos[12] if len(datos) > 12 else None,
                    fecha_registro=datos[13] if len(datos) > 13 else None
                )
                return usuario

            return None

        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None

    def calcular_dias_uso(self, correo):
        """Calcula los días desde el registro del usuario."""
        try:
            conn = sqlite3.connect(self.db_nombre)
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(usuarios)")
            columnas = [columna[1] for columna in cursor.fetchall()]

            if 'fecha_registro' not in columnas:
                conn.close()
                return 1

            cursor.execute(
                "SELECT fecha_registro FROM usuarios WHERE correo = ?",
                (correo,)
            )

            resultado = cursor.fetchone()
            conn.close()

            if resultado and resultado[0]:
                try:
                    fecha_str = resultado[0]
                    formatos = [
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d %H:%M:%S.%f',  # Con microsegundos
                        '%Y-%m-%d',
                        '%d/%m/%Y %H:%M:%S',
                        '%d/%m/%Y'
                    ]
                    fecha_registro = None
                    for formato in formatos:
                        try:
                            fecha_registro = datetime.strptime(fecha_str, formato)
                            break
                        except ValueError:
                            continue

                    if fecha_registro:
                        fecha_actual = datetime.now()
                        diferencia = fecha_actual - fecha_registro
                        dias_uso = diferencia.days

                        # Si es el mismo día, mostrar 1, sino mostrar los días reales + 1
                        if dias_uso == 0:
                            return 1
                        else:
                            return dias_uso + 1
                    else:
                        return 1

                except Exception:
                    return 1

            return 1

        except Exception:
            return 1

class LoginScreen(QMainWindow):
    def __init__(self):
        super(LoginScreen, self).__init__()

        uic.loadUi("login_screen.ui", self)

        self.db_service = BaseDatosGymSync()

        self.setupConnections()

    def setupConnections(self):
        """Configura las conexiones entre los widgets y los métodos."""
        self.btn_iniciar_sesion.clicked.connect(self.iniciar_sesion)
        self.lnk_registrate.linkActivated.connect(self.abrir_pantalla_registro)

    @pyqtSlot()
    def iniciar_sesion(self):
        """Se ejecuta al hacer clic en el botón 'Iniciar sesión'."""
        if not self.comprobar_campos_requeridos():
            return

        correo = self.txt_correo.text()
        contraseña = self.txt_contraseña.text()

        if self.db_service.validar_credenciales(correo, contraseña):
            usuario = self.db_service.obtener_usuario_por_correo(correo)
            nombre_mostrar = usuario.nombre if usuario and usuario.nombre else correo

            QMessageBox.information(self, "Éxito", f"Bienvenido a GymSync, {nombre_mostrar}")
            self.abrir_pantalla_principal(usuario)
        else:
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

        self.login_screen = login_screen

        uic.loadUi("registro_screen.ui", self)

        self.db_service = BaseDatosGymSync()

        self.cargar_opciones_objetivo()
        self.cargar_disponibilidad_horaria()
        self.cargar_estilos_vida()
        self.cargar_lugar_entrenamiento()
        self.cargar_genero()

        self.setupConnections()

    def setupConnections(self):
        """Configura las conexiones entre los widgets y los métodos."""
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
        if not self.validar_campos_obligatorios():
            return

        contraseña = self.txt_contraseña.text()
        confirmacion = self.txt_confirmar_contraseña.text()

        if not self.confirmar_contraseñas_iguales(contraseña, confirmacion):
            self.mostrar_error_validacion(
                "Error de contraseña",
                "Las contraseñas no coinciden. Por favor, verifica."
            )
            return

        try:
            usuario = self.crear_objeto_usuario()

            if self.db_service.guardar_usuario(usuario):
                QMessageBox.information(
                    self,
                    "Registro exitoso",
                    f"¡Bienvenido/a a GymSync, {usuario.nombre}!\n\nTu cuenta ha sido creada correctamente."
                )
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

        for campo, valor in campos_texto.items():
            if not valor:
                self.mostrar_error_validacion(
                    "Campos incompletos",
                    f"El campo '{campo}' es obligatorio. Por favor, complétalo."
                )
                return False

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

        if "@" not in campos_texto["Correo"] or "." not in campos_texto["Correo"]:
            self.mostrar_error_validacion(
                "Formato incorrecto",
                "Por favor, introduce un correo electrónico válido."
            )
            return False

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
        QMessageBox.information(
            self,
            "Navegación",
            f"Redirigiendo a la pantalla principal...\n"
            f"¡Bienvenido/a a GymSync, {usuario.nombre}!"
        )

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
            self.login_window = LoginScreen()
            self.login_window.show()
            self.close()


class MainScreen(QMainWindow):
    def __init__(self, usuario):
        super(MainScreen, self).__init__()

        self.usuario = usuario

        uic.loadUi("main_screen.ui", self)

        self.db_service = BaseDatosGymSync()

        self.configurar_pantalla_usuario()

        self.setupConnections()

    def setupConnections(self):
        """Configura las conexiones entre los widgets y los métodos."""
        self.btn_datos_perfil.clicked.connect(self.abrir_datos_perfil)

    def configurar_pantalla_usuario(self):
        """Configura todos los elementos de la pantalla con los datos del usuario."""
        self.configurar_seccion_perfil()

        self.configurar_seccion_progreso()

        self.configurar_sesion_actual()

        self.configurar_proximas_sesiones()

        self.configurar_notificaciones()

    def configurar_seccion_perfil(self):
        """Configura la sección del perfil del usuario."""
        self.lbl_correo_usuario.setText(self.usuario.correo)

        iniciales = self.obtener_iniciales(self.usuario.nombre)
        self.lbl_avatar_usuario.setText(iniciales)

    def configurar_seccion_progreso(self):
        """Configura la sección de progreso del usuario."""
        dias_uso = self.db_service.calcular_dias_uso(self.usuario.correo)
        self.lbl_dias_uso.setText(str(dias_uso))
        dias_siguiente_nivel = 30 - (dias_uso % 30)
        if dias_siguiente_nivel == 30:
            dias_siguiente_nivel = 0
        self.lbl_dias_siguiente_nivel.setText(str(dias_siguiente_nivel))
        diferencia_peso = self.calcular_diferencia_peso()
        self.lbl_diferencia_peso.setText(diferencia_peso)

    def configurar_sesion_actual(self):
        """Configura la sesión de entrenamiento actual."""
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_actual = QDateTime.currentDateTime().date().dayOfWeek()
        nombre_dia = dias_semana[dia_actual - 1]
        self.lbl_dia_actual.setText(nombre_dia)
        tipo_sesion = self.obtener_tipo_sesion(dia_actual)
        self.lbl_tipo_sesion_actual.setText(tipo_sesion)
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

        # Configurar próxima sesión 2 (pasado mañana)
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
            return "YO"
        palabras = nombre.split()
        if len(palabras) >= 2:
            return f"{palabras[0][0]}{palabras[1][0]}".upper()
        else:
            return palabras[0][:2].upper()

    def calcular_diferencia_peso(self):
        """Calcula la diferencia de peso."""
        return "0.0 kg"

    def obtener_tipo_sesion(self, dia):
        """Obtiene el tipo de sesión según el día y objetivo del usuario."""

        # ADELGAZAR
        if self.usuario.objetivo == "Adelgazar":
            if self.usuario.disponibilidad == "Lunes a Viernes (mañanas)" or self.usuario.disponibilidad == "Lunes a Viernes (tardes)":
                if self.usuario.estilo_vida == "Sedentario (poco o nada de ejercicio)":
                    tipos_adelgazar_sedentario_5dias = {
                        1: "EASY CARDIO", 2: "LIGHT STRENGTH", 3: "EASY CARDIO", 4: "LIGHT STRENGTH", 5: "EASY CARDIO",
                        6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_adelgazar_sedentario_5dias.get(dia, "ENTRENAMIENTO")
                elif self.usuario.estilo_vida in ["Ligeramente activo", "Moderadamente activo"]:
                    tipos_adelgazar_moderado_5dias = {
                        1: "CARDIO HIIT", 2: "FULL BODY STRENGTH", 3: "CARDIO BAJO", 4: "FULL BODY STRENGTH",
                        5: "CARDIO HIIT", 6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_adelgazar_moderado_5dias.get(dia, "ENTRENAMIENTO")
                else:  # Muy activo, Extremadamente activo
                    tipos_adelgazar_intenso_5dias = {
                        1: "HARD CARDIO", 2: "STRENGTH CIRCUIT", 3: "CARDIO HIIT", 4: "STRENGTH CIRCUIT",
                        5: "HARD CARDIO", 6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_adelgazar_intenso_5dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Solo fines de semana":
                if self.usuario.estilo_vida == "Sedentario (poco o nada de ejercicio)":
                    tipos_adelgazar_sedentario_finde = {
                        1: "DESCANSO", 2: "DESCANSO", 3: "DESCANSO", 4: "DESCANSO", 5: "DESCANSO", 6: "EASY FULL BODY",
                        7: "LIGHT CARDIO"
                    }
                    return tipos_adelgazar_sedentario_finde.get(dia, "ENTRENAMIENTO")
                else:
                    tipos_adelgazar_activo_finde = {
                        1: "DESCANSO", 2: "DESCANSO", 3: "DESCANSO", 4: "DESCANSO", 5: "DESCANSO", 6: "CARDIO HIIT",
                        7: "FULL BODY STRENGTH"
                    }
                    return tipos_adelgazar_activo_finde.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Lunes, Miércoles y Viernes (todo el día)":
                if self.usuario.estilo_vida == "Sedentario (poco o nada de ejercicio)":
                    tipos_adelgazar_sedentario_3dias = {
                        1: "EASY CARDIO", 2: "DESCANSO", 3: "LIGHT STRENGTH", 4: "DESCANSO", 5: "EASY CARDIO",
                        6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_adelgazar_sedentario_3dias.get(dia, "ENTRENAMIENTO")
                else:
                    tipos_adelgazar_activo_3dias = {
                        1: "CARDIO HIIT", 2: "DESCANSO", 3: "FULL BODY STRENGTH", 4: "DESCANSO", 5: "CARDIO HIIT",
                        6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_adelgazar_activo_3dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Martes y Jueves (todo el día)":
                if self.usuario.estilo_vida == "Sedentario (poco o nada de ejercicio)":
                    tipos_adelgazar_sedentario_2dias = {
                        1: "DESCANSO", 2: "EASY FULL BODY", 3: "DESCANSO", 4: "LIGHT CARDIO", 5: "DESCANSO",
                        6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_adelgazar_sedentario_2dias.get(dia, "ENTRENAMIENTO")
                else:
                    tipos_adelgazar_activo_2dias = {
                        1: "DESCANSO", 2: "CARDIO HIIT", 3: "DESCANSO", 4: "FULL BODY STRENGTH", 5: "DESCANSO",
                        6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_adelgazar_activo_2dias.get(dia, "ENTRENAMIENTO")

            else:  # Todos los días (flexible)
                if self.usuario.estilo_vida == "Sedentario (poco o nada de ejercicio)":
                    tipos_adelgazar_sedentario_diario = {
                        1: "EASY CARDIO", 2: "LIGHT STRENGTH", 3: "EASY CARDIO", 4: "LIGHT STRENGTH", 5: "EASY CARDIO",
                        6: "YOGA", 7: "DESCANSO"
                    }
                    return tipos_adelgazar_sedentario_diario.get(dia, "ENTRENAMIENTO")
                else:
                    tipos_adelgazar_activo_diario = {
                        1: "CARDIO HIIT", 2: "FULL BODY STRENGTH", 3: "CARDIO BAJO", 4: "UPPER BODY", 5: "CARDIO HIIT",
                        6: "LOWER BODY", 7: "YOGA"
                    }
                    return tipos_adelgazar_activo_diario.get(dia, "ENTRENAMIENTO")

        # GANAR MASA MUSCULAR
        elif self.usuario.objetivo == "Ganar masa muscular":
            if self.usuario.disponibilidad == "Lunes a Viernes (mañanas)" or self.usuario.disponibilidad == "Lunes a Viernes (tardes)":
                if self.usuario.estilo_vida == "Sedentario (poco o nada de ejercicio)":
                    tipos_masa_sedentario_5dias = {
                        1: "UPPER BODY", 2: "LOWER BODY", 3: "PUSH DAY", 4: "PULL DAY", 5: "LEGS DAY", 6: "DESCANSO",
                        7: "DESCANSO"
                    }
                    return tipos_masa_sedentario_5dias.get(dia, "ENTRENAMIENTO")
                else:
                    tipos_masa_activo_5dias = {
                        1: "PUSH DAY", 2: "PULL DAY", 3: "LEGS DAY", 4: "PUSH DAY", 5: "PULL DAY", 6: "DESCANSO",
                        7: "DESCANSO"
                    }
                    return tipos_masa_activo_5dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Solo fines de semana":
                tipos_masa_finde = {
                    1: "DESCANSO", 2: "DESCANSO", 3: "DESCANSO", 4: "DESCANSO", 5: "DESCANSO", 6: "FULL BODY STRENGTH",
                    7: "FULL BODY POWER"
                }
                return tipos_masa_finde.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Lunes, Miércoles y Viernes (todo el día)":
                tipos_masa_3dias = {
                    1: "FULL BODY STRENGTH", 2: "DESCANSO", 3: "UPPER BODY", 4: "DESCANSO", 5: "LOWER BODY",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_masa_3dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Martes y Jueves (todo el día)":
                tipos_masa_2dias = {
                    1: "DESCANSO", 2: "FULL BODY STRENGTH", 3: "DESCANSO", 4: "FULL BODY POWER", 5: "DESCANSO",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_masa_2dias.get(dia, "ENTRENAMIENTO")

            else:  # Todos los días
                tipos_masa_diario = {
                    1: "PUSH DAY", 2: "PULL DAY", 3: "LEGS DAY", 4: "PUSH DAY", 5: "PULL DAY", 6: "LEGS DAY",
                    7: "DESCANSO"
                }
                return tipos_masa_diario.get(dia, "ENTRENAMIENTO")

        # MANTENER PESO
        elif self.usuario.objetivo == "Mantener peso":
            if self.usuario.disponibilidad == "Lunes a Viernes (mañanas)" or self.usuario.disponibilidad == "Lunes a Viernes (tardes)":
                tipos_mantener_5dias = {
                    1: "FULL BODY STRENGTH", 2: "CARDIO BAJO", 3: "UPPER BODY", 4: "CARDIO BAJO", 5: "LOWER BODY",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_mantener_5dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Solo fines de semana":
                tipos_mantener_finde = {
                    1: "DESCANSO", 2: "DESCANSO", 3: "DESCANSO", 4: "DESCANSO", 5: "DESCANSO", 6: "FULL BODY STRENGTH",
                    7: "CARDIO BAJO"
                }
                return tipos_mantener_finde.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Lunes, Miércoles y Viernes (todo el día)":
                tipos_mantener_3dias = {
                    1: "FULL BODY STRENGTH", 2: "DESCANSO", 3: "CARDIO BAJO", 4: "DESCANSO", 5: "FULL BODY STRENGTH",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_mantener_3dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Martes y Jueves (todo el día)":
                tipos_mantener_2dias = {
                    1: "DESCANSO", 2: "FULL BODY STRENGTH", 3: "DESCANSO", 4: "CARDIO BAJO", 5: "DESCANSO",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_mantener_2dias.get(dia, "ENTRENAMIENTO")

            else:  # Todos los días
                tipos_mantener_diario = {
                    1: "FULL BODY STRENGTH", 2: "CARDIO BAJO", 3: "UPPER BODY", 4: "CARDIO BAJO", 5: "LOWER BODY",
                    6: "YOGA", 7: "DESCANSO"
                }
                return tipos_mantener_diario.get(dia, "ENTRENAMIENTO")

        # MEJORAR RESISTENCIA
        elif self.usuario.objetivo == "Mejorar resistencia":
            if self.usuario.disponibilidad == "Lunes a Viernes (mañanas)" or self.usuario.disponibilidad == "Lunes a Viernes (tardes)":
                if self.usuario.estilo_vida == "Sedentario (poco o nada de ejercicio)":
                    tipos_resistencia_sedentario_5dias = {
                        1: "CARDIO BAJO", 2: "LIGHT STRENGTH", 3: "CARDIO BAJO", 4: "LIGHT STRENGTH", 5: "CARDIO BAJO",
                        6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_resistencia_sedentario_5dias.get(dia, "ENTRENAMIENTO")
                else:
                    tipos_resistencia_activo_5dias = {
                        1: "CARDIO HIIT", 2: "STRENGTH ENDURANCE", 3: "CARDIO BAJO", 4: "STRENGTH ENDURANCE",
                        5: "CARDIO HIIT", 6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_resistencia_activo_5dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Solo fines de semana":
                tipos_resistencia_finde = {
                    1: "DESCANSO", 2: "DESCANSO", 3: "DESCANSO", 4: "DESCANSO", 5: "DESCANSO", 6: "CARDIO HIIT",
                    7: "CARDIO BAJO"
                }
                return tipos_resistencia_finde.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Lunes, Miércoles y Viernes (todo el día)":
                tipos_resistencia_3dias = {
                    1: "CARDIO HIIT", 2: "DESCANSO", 3: "STRENGTH ENDURANCE", 4: "DESCANSO", 5: "CARDIO BAJO",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_resistencia_3dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Martes y Jueves (todo el día)":
                tipos_resistencia_2dias = {
                    1: "DESCANSO", 2: "CARDIO HIIT", 3: "DESCANSO", 4: "STRENGTH ENDURANCE", 5: "DESCANSO",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_resistencia_2dias.get(dia, "ENTRENAMIENTO")

            else:  # Todos los días
                tipos_resistencia_diario = {
                    1: "CARDIO HIIT", 2: "STRENGTH ENDURANCE", 3: "CARDIO BAJO", 4: "STRENGTH ENDURANCE",
                    5: "CARDIO HIIT", 6: "CARDIO BAJO", 7: "YOGA"
                }
                return tipos_resistencia_diario.get(dia, "ENTRENAMIENTO")

        # TONIFICAR
        elif self.usuario.objetivo == "Tonificar":
            if self.usuario.disponibilidad == "Lunes a Viernes (mañanas)" or self.usuario.disponibilidad == "Lunes a Viernes (tardes)":
                if self.usuario.estilo_vida == "Sedentario (poco o nada de ejercicio)":
                    tipos_tonificar_sedentario_5dias = {
                        1: "TONING UPPER", 2: "EASY CARDIO", 3: "TONING LOWER", 4: "EASY CARDIO", 5: "TONING FULL",
                        6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_tonificar_sedentario_5dias.get(dia, "ENTRENAMIENTO")
                else:
                    tipos_tonificar_activo_5dias = {
                        1: "TONING CIRCUIT", 2: "CARDIO HIIT", 3: "TONING UPPER", 4: "CARDIO BAJO", 5: "TONING LOWER",
                        6: "DESCANSO", 7: "DESCANSO"
                    }
                    return tipos_tonificar_activo_5dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Solo fines de semana":
                tipos_tonificar_finde = {
                    1: "DESCANSO", 2: "DESCANSO", 3: "DESCANSO", 4: "DESCANSO", 5: "DESCANSO", 6: "TONING CIRCUIT",
                    7: "CARDIO BAJO"
                }
                return tipos_tonificar_finde.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Lunes, Miércoles y Viernes (todo el día)":
                tipos_tonificar_3dias = {
                    1: "TONING UPPER", 2: "DESCANSO", 3: "TONING LOWER", 4: "DESCANSO", 5: "TONING FULL", 6: "DESCANSO",
                    7: "DESCANSO"
                }
                return tipos_tonificar_3dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Martes y Jueves (todo el día)":
                tipos_tonificar_2dias = {
                    1: "DESCANSO", 2: "TONING CIRCUIT", 3: "DESCANSO", 4: "CARDIO BAJO", 5: "DESCANSO", 6: "DESCANSO",
                    7: "DESCANSO"
                }
                return tipos_tonificar_2dias.get(dia, "ENTRENAMIENTO")

            else:  # Todos los días
                tipos_tonificar_diario = {
                    1: "TONING UPPER", 2: "CARDIO BAJO", 3: "TONING LOWER", 4: "CARDIO BAJO", 5: "TONING FULL",
                    6: "YOGA", 7: "DESCANSO"
                }
                return tipos_tonificar_diario.get(dia, "ENTRENAMIENTO")

        # PREPARACIÓN PARA COMPETICIÓN
        elif self.usuario.objetivo == "Preparación para competición":
            if self.usuario.disponibilidad == "Lunes a Viernes (mañanas)" or self.usuario.disponibilidad == "Lunes a Viernes (tardes)":
                tipos_competicion_5dias = {
                    1: "PUSH DAY", 2: "PULL DAY", 3: "LEGS DAY", 4: "PUSH DAY", 5: "PULL DAY", 6: "DESCANSO",
                    7: "DESCANSO"
                }
                return tipos_competicion_5dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Solo fines de semana":
                tipos_competicion_finde = {
                    1: "DESCANSO", 2: "DESCANSO", 3: "DESCANSO", 4: "DESCANSO", 5: "DESCANSO", 6: "FULL BODY POWER",
                    7: "COMPETITION PREPARATION"
                }
                return tipos_competicion_finde.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Lunes, Miércoles y Viernes (todo el día)":
                tipos_competicion_3dias = {
                    1: "FULL BODY POWER", 2: "DESCANSO", 3: "COMPETITION PREPARATION", 4: "DESCANSO", 5: "FULL BODY STRENGTH",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_competicion_3dias.get(dia, "ENTRENAMIENTO")

            elif self.usuario.disponibilidad == "Martes y Jueves (todo el día)":
                tipos_competicion_2dias = {
                    1: "DESCANSO", 2: "FULL BODY POWER", 3: "DESCANSO", 4: "COMPETITION PREPARATION", 5: "DESCANSO",
                    6: "DESCANSO", 7: "DESCANSO"
                }
                return tipos_competicion_2dias.get(dia, "ENTRENAMIENTO")

            else:  # Todos los días
                tipos_competicion_diario = {
                    1: "PUSH DAY", 2: "PULL DAY", 3: "LEGS DAY", 4: "PUSH DAY", 5: "PULL DAY", 6: "LEGS DAY",
                    7: "COMPETITION PREPARATION"
                }
                return tipos_competicion_diario.get(dia, "ENTRENAMIENTO")

        # Fallback
        return "ENTRENAMIENTO"

    def configurar_ejercicios_actuales(self, tipo_sesion):
        """Configura la lista de ejercicios para la sesión actual."""
        ejercicios = self.obtener_ejercicios_por_tipo_completo(tipo_sesion)

        self.lista_ejercicios_actuales.clear()
        for ejercicio in ejercicios:
            item = QListWidgetItem(ejercicio)
            self.lista_ejercicios_actuales.addItem(item)

    def obtener_ejercicios_por_tipo_completo(self, tipo_sesion):
        """Retorna una lista de ejercicios según el tipo de sesión y lugar de entrenamiento."""

        if self.usuario.lugar_entrenamiento == "Casa sin equipamiento":
            ejercicios_por_tipo = {
                "PULL DAY": [
                    "Pull-ups en barra de puerta - 3x8-12",
                    "Remo invertido con mesa - 3x8-10",
                    "Superman - 3x12-15",
                    "Plancha inversa - 3x30s",
                    "Curl de bíceps isométrico - 3x10"
                ],
                "PUSH DAY": [
                    "Flexiones - 3x10-15",
                    "Flexiones diamante - 3x6-10",
                    "Pike push-ups - 3x8-12",
                    "Fondos en silla - 3x8-12",
                    "Flexiones inclinadas - 3x10-12"
                ],
                "LEGS DAY": [
                    "Sentadillas - 3x15-20",
                    "Zancadas - 3x12 c/pierna",
                    "Sentadilla sumo - 3x15-18",
                    "Elevación de gemelos - 3x20-25",
                    "Glute bridge - 3x15-20"
                ],
                "CARDIO HIIT": [
                    "Calentamiento - 5 min",
                    "Burpees - 30s ON/30s OFF x8",
                    "Mountain climbers - 30s ON/30s OFF x8",
                    "Jumping jacks - 30s ON/30s OFF x8",
                    "Enfriamiento - 5 min"
                ],
                "HARD CARDIO": [
                    "Calentamiento - 5 min",
                    "Burpees - 45s ON/15s OFF x10",
                    "Mountain climbers - 45s ON/15s OFF x10",
                    "High knees - 45s ON/15s OFF x10",
                    "Squat jumps - 45s ON/15s OFF x10",
                    "Enfriamiento - 5 min"
                ],
                "EASY CARDIO": [
                    "Marcha en el sitio - 15 min",
                    "Jumping jacks suaves - 2x30s",
                    "Estiramientos dinámicos - 10 min",
                    "Respiración profunda - 5 min"
                ],
                "CARDIO BAJO": [
                    "Marcha en el sitio - 20 min",
                    "Estiramientos - 10 min",
                    "Movimientos articulares - 10 min"
                ],
                "LIGHT STRENGTH": [
                    "Sentadillas - 2x10-12",
                    "Flexiones de rodillas - 2x8-10",
                    "Plancha - 2x20s",
                    "Glute bridge - 2x12-15"
                ],
                "FULL BODY STRENGTH": [
                    "Sentadillas - 3x12-15",
                    "Flexiones - 3x8-12",
                    "Plancha - 3x30s",
                    "Zancadas - 3x10 c/pierna",
                    "Glute bridge - 3x12-15"
                ],
                "UPPER BODY": [
                    "Flexiones - 3x10-12",
                    "Pike push-ups - 3x8-10",
                    "Plancha - 3x30s",
                    "Superman - 3x12-15"
                ],
                "LOWER BODY": [
                    "Sentadillas - 3x15-18",
                    "Zancadas - 3x12 c/pierna",
                    "Glute bridge - 3x15-18",
                    "Elevación de gemelos - 3x20"
                ],
                "STRENGTH CIRCUIT": [
                    "Circuito: Flexiones + Sentadillas + Plancha - 3 rondas",
                    "30s trabajo/15s descanso por ejercicio",
                    "Descanso 2min entre rondas"
                ],
                "STRENGTH ENDURANCE": [
                    "Sentadillas - 4x20",
                    "Flexiones - 4x15",
                    "Plancha - 4x45s",
                    "Mountain climbers - 4x30s"
                ],
                "TONING UPPER": [
                    "Flexiones lentas - 3x8-10",
                    "Plancha lateral - 3x20s c/lado",
                    "Superman - 3x12-15",
                    "Flexiones diamante - 2x5-8"
                ],
                "TONING LOWER": [
                    "Sentadillas lentas - 3x12-15",
                    "Zancadas estáticas - 3x10 c/pierna",
                    "Glute bridge - 3x15-18",
                    "Calf raises - 3x20"
                ],
                "TONING FULL": [
                    "Burpees lentos - 3x8-10",
                    "Plancha con movimiento - 3x30s",
                    "Sentadilla a flexión - 3x8-10"
                ],
                "TONING CIRCUIT": [
                    "Circuito tonificación - 3 rondas",
                    "Sentadillas + Flexiones + Plancha",
                    "45s trabajo/15s descanso"
                ],
                "EASY FULL BODY": [
                    "Sentadillas suaves - 2x10",
                    "Flexiones de rodillas - 2x8",
                    "Plancha - 2x20s",
                    "Estiramientos - 10 min"
                ],
                "FULL BODY POWER": [
                    "Squat jumps - 3x10-12",
                    "Burpees - 3x8-10",
                    "Mountain climbers - 3x30s",
                    "Plank to downward dog - 3x10"
                ],
                "COMPETITION PREPARATION": [
                    "Rutina específica competición - 45 min",
                    "Técnica y precisión - 20 min",
                    "Resistencia específica - 15 min",
                    "Estiramientos - 10 min"
                ],
                "YOGA": [
                    "Saludo al sol - 5 rondas",
                    "Posturas de pie - 10 min",
                    "Posturas sentado - 10 min",
                    "Relajación - 10 min"
                ],
                "DESCANSO": [
                    "Día de descanso activo",
                    "Estiramientos suaves - 15 min",
                    "Meditación - 10 min",
                    "Movilidad articular - 10 min"
                ],
                # Añadir los nuevos tipos de entrenamiento
                "PUSH HEAVY": [
                    "Flexiones diamante - 4x8-12",
                    "Flexiones archer - 3x6 c/lado",
                    "Flexiones elevadas (pies) - 4x8-10",
                    "Handstand push-ups asistidas - 3x5-8",
                    "Fondos en silla - 4x10-12",
                    "Pike push-ups - 3x8-10"
                ],
                "PULL HEAVY": [
                    "Dominadas en barra de puerta - 4x6-10",
                    "Remo invertido bajo mesa - 4x8-12",
                    "Superman - 4x12-15",
                    "Reverse flies acostado - 3x15",
                    "Wall angels - 3x20",
                    "Isométrico de dominada - 3x20s"
                ],
                "LEGS HEAVY": [
                    "Sentadillas pistol asistidas - 3x5 c/pierna",
                    "Sentadillas con salto - 4x12-15",
                    "Zancadas bulgáras - 3x10 c/pierna",
                    "Single leg deadlift - 3x8 c/pierna",
                    "Wall sit - 4x45s",
                    "Elevación de pantorrillas - 4x20"
                ],
                "HIIT EXTREME": [
                    "Burpees - 40s ON/20s OFF x8",
                    "Sentadillas con salto - 30s ON/10s OFF x10",
                    "Mountain climbers - 45s ON/15s OFF x6",
                    "High knees - 20s ON/10s OFF x12",
                    "Jumping lunges - 30s ON/30s OFF x8"
                ],
                "BASIC STRENGTH": [
                    "Flexiones - 3x8-12",
                    "Sentadillas - 3x12-15",
                    "Plancha - 3x30s",
                    "Glute bridge - 3x12-15",
                    "Wall sit - 3x30s",
                    "Superman - 3x10-12"
                ]
            }

        elif self.usuario.lugar_entrenamiento == "Casa con equipamiento":
            ejercicios_por_tipo = {
                "PULL DAY": [
                    "Remo con mancuernas - 3x8-12",
                    "Pull-ups asistidas - 3x6-8",
                    "Curl de bíceps - 3x10-12",
                    "Face pulls con banda - 3x12-15",
                    "Peso muerto rumano - 3x8-10"
                ],
                "PUSH DAY": [
                    "Press de pecho con mancuernas - 3x8-10",
                    "Press militar con mancuernas - 3x8-10",
                    "Flexiones con peso - 3x10-12",
                    "Press inclinado - 3x8-10",
                    "Extensiones de tríceps - 3x10-12"
                ],
                "LEGS DAY": [
                    "Sentadillas con mancuernas - 3x12-15",
                    "Peso muerto - 3x8-10",
                    "Zancadas con peso - 3x10 c/pierna",
                    "Elevación de gemelos con peso - 3x15-20",
                    "Sentadilla búlgara - 3x8 c/pierna"
                ],
                "CARDIO HIIT": [
                    "Calentamiento - 5 min",
                    "Thrusters con mancuernas - 30s ON/30s OFF x8",
                    "Burpees - 30s ON/30s OFF x8",
                    "Swings con kettlebell - 30s ON/30s OFF x8",
                    "Enfriamiento - 5 min"
                ],
                "HARD CARDIO": [
                    "Calentamiento - 5 min",
                    "Thrusters - 45s ON/15s OFF x10",
                    "Burpees con peso - 45s ON/15s OFF x10",
                    "Swings pesados - 45s ON/15s OFF x10",
                    "Mountain climbers - 45s ON/15s OFF x10",
                    "Enfriamiento - 5 min"
                ],
                "EASY CARDIO": [
                    "Caminata en cinta - 20 min",
                    "Movimientos con mancuernas ligeras - 10 min",
                    "Estiramientos con banda - 10 min"
                ],
                "CARDIO BAJO": [
                    "Caminata en cinta - 25 min",
                    "Ejercicios con banda elástica - 15 min",
                    "Estiramientos - 10 min"
                ],
                "LIGHT STRENGTH": [
                    "Goblet squat - 2x10-12",
                    "Press de pecho ligero - 2x8-10",
                    "Remo con mancuerna - 2x8-10",
                    "Plancha - 2x30s"
                ],
                "FULL BODY STRENGTH": [
                    "Goblet squat - 3x12-15",
                    "Press de pecho con mancuernas - 3x8-12",
                    "Remo con mancuernas - 3x8-12",
                    "Press militar - 3x8-10",
                    "Peso muerto rumano - 3x10-12"
                ],
                "UPPER BODY": [
                    "Press de pecho - 3x10-12",
                    "Remo con mancuernas - 3x10-12",
                    "Press militar - 3x8-10",
                    "Curl de bíceps - 3x10-12",
                    "Extensiones de tríceps - 3x10-12"
                ],
                "LOWER BODY": [
                    "Sentadillas con peso - 3x12-15",
                    "Peso muerto rumano - 3x10-12",
                    "Zancadas con mancuernas - 3x10 c/pierna",
                    "Elevación de gemelos - 3x15-20",
                    "Hip thrust - 3x12-15"
                ],
                "STRENGTH CIRCUIT": [
                    "Circuito con mancuernas - 3 rondas",
                    "Thrusters + Remo + Sentadillas",
                    "45s trabajo/15s descanso por ejercicio"
                ],
                "STRENGTH ENDURANCE": [
                    "Thrusters - 4x15-20",
                    "Remo con mancuernas - 4x15-20",
                    "Goblet squat - 4x20-25",
                    "Swings con kettlebell - 4x30s"
                ],
                "TONING UPPER": [
                    "Press de pecho controlado - 3x12-15",
                    "Remo con pausa - 3x12-15",
                    "Elevaciones laterales - 3x12-15",
                    "Curl de bíceps lento - 3x12-15"
                ],
                "TONING LOWER": [
                    "Sentadillas con pausa - 3x15-18",
                    "Peso muerto lento - 3x12-15",
                    "Zancadas estáticas - 3x12 c/pierna",
                    "Hip thrust con pausa - 3x15-18"
                ],
                "TONING FULL": [
                    "Thrusters lentos - 3x10-12",
                    "Remo a sentadilla - 3x10-12",
                    "Burpees con mancuernas - 3x8-10"
                ],
                "TONING CIRCUIT": [
                    "Circuito tonificación con peso - 3 rondas",
                    "Movimientos controlados y lentos",
                    "45s trabajo/15s descanso"
                ],
                "EASY FULL BODY": [
                    "Goblet squat ligero - 2x10",
                    "Press de pecho suave - 2x8",
                    "Remo ligero - 2x8",
                    "Estiramientos con banda - 10 min"
                ],
                "FULL BODY POWER": [
                    "Thrusters explosivos - 3x8-10",
                    "Swings pesados - 3x12-15",
                    "Burpees con peso - 3x6-8",
                    "Clean and press - 3x6-8"
                ],
                "COMPETITION PREPARATION": [
                    "Rutina específica con peso - 45 min",
                    "Técnica avanzada - 20 min",
                    "Potencia y velocidad - 15 min",
                    "Recuperación activa - 10 min"
                ],
                "YOGA": [
                    "Saludo al sol - 5 rondas",
                    "Posturas con apoyo - 15 min",
                    "Flexibilidad profunda - 15 min",
                    "Relajación - 10 min"
                ],
                "DESCANSO": [
                    "Día de descanso activo",
                    "Estiramientos con banda - 15 min",
                    "Foam rolling - 10 min",
                    "Movilidad articular - 10 min"
                ],
                # Añadir los nuevos tipos de entrenamiento
                "PUSH HEAVY": [
                    "Press con mancuernas en suelo - 5x6-8",
                    "Press militar con mancuernas - 4x6-8",
                    "Flexiones con mancuernas - 4x8-10",
                    "Elevaciones laterales - 3x10-12",
                    "Press francés con mancuernas - 3x8-10",
                    "Fondos en silla - 3x10-12"
                ],
                "PULL HEAVY": [
                    "Peso muerto con mancuernas - 5x6-8",
                    "Remo inclinado con mancuernas - 4x8-10",
                    "Pullover con mancuerna - 3x10-12",
                    "Curl con mancuernas - 4x8-10",
                    "Remo unilateral - 3x8-10 c/brazo",
                    "Shrugs con mancuernas - 3x12-15"
                ],
                "HIIT MODERATE": [
                    "Burpees modificados - 30s ON/30s OFF x6",
                    "Sentadillas con salto - 20s ON/40s OFF x8",
                    "Mountain climbers - 30s ON/30s OFF x6",
                    "Jumping jacks - 45s ON/15s OFF x6"
                ]
            }

        else:  # Gimnasio
            ejercicios_por_tipo = {
                "PULL DAY": [
                    "Pull-ups - 3x8-12",
                    "Remo con barra - 3x8-10",
                    "Dominadas asistidas - 3x6-8",
                    "Curl de bíceps - 3x10-12",
                    "Remo con cable - 3x10-12",
                    "Face pulls - 3x12-15"
                ],
                "PUSH DAY": [
                    "Press de banca - 3x8-10",
                    "Press militar - 3x8-10",
                    "Press inclinado - 3x8-10",
                    "Fondos en paralelas - 3x8-12",
                    "Press francés - 3x10-12",
                    "Elevaciones laterales - 3x12-15"
                ],
                "LEGS DAY": [
                    "Sentadillas - 3x10-12",
                    "Peso muerto - 3x6-8",
                    "Prensa de piernas - 3x12-15",
                    "Zancadas - 3x10 c/pierna",
                    "Curl femoral - 3x10-12",
                    "Elevación de gemelos - 3x15-20"
                ],
                "CARDIO HIIT": [
                    "Calentamiento en cinta - 5 min",
                    "Sprints en cinta - 30s ON/90s OFF x8",
                    "Burpees - 30s ON/30s OFF x6",
                    "Battle ropes - 30s ON/30s OFF x6",
                    "Enfriamiento - 5 min"
                ],
                "HARD CARDIO": [
                    "Calentamiento - 5 min",
                    "Sprints intensos - 45s ON/15s OFF x12",
                    "Battle ropes - 45s ON/15s OFF x8",
                    "Box jumps - 45s ON/15s OFF x8",
                    "Rowing machine - 45s ON/15s OFF x8",
                    "Enfriamiento - 5 min"
                ],
                "EASY CARDIO": [
                    "Caminata en cinta - 25 min",
                    "Bicicleta estática suave - 15 min",
                    "Estiramientos en colchoneta - 10 min"
                ],
                "CARDIO BAJO": [
                    "Caminata en cinta - 30 min",
                    "Bicicleta estática - 20 min",
                    "Elíptica - 15 min",
                    "Estiramientos - 10 min"
                ],
                "LIGHT STRENGTH": [
                    "Sentadilla en multipower - 2x10-12",
                    "Press de pecho en máquina - 2x8-10",
                    "Remo en máquina - 2x8-10",
                    "Leg press ligero - 2x12-15"
                ],
                "FULL BODY STRENGTH": [
                    "Sentadillas - 3x8-10",
                    "Press de banca - 3x8-10",
                    "Peso muerto - 3x6-8",
                    "Press militar - 3x8-10",
                    "Remo con barra - 3x8-10"
                ],
                "UPPER BODY": [
                    "Press de banca - 3x8-10",
                    "Remo con barra - 3x8-10",
                    "Press militar - 3x8-10",
                    "Pull-ups - 3x6-10",
                    "Fondos en paralelas - 3x8-12"
                ],
                "LOWER BODY": [
                    "Sentadillas - 3x10-12",
                    "Peso muerto rumano - 3x8-10",
                    "Prensa de piernas - 3x12-15",
                    "Curl femoral - 3x10-12",
                    "Extensión de cuádriceps - 3x12-15"
                ],
                "STRENGTH CIRCUIT": [
                    "Circuito estaciones - 4 rondas",
                    "Kettlebell swings + Pull-ups + Thrusters + Box jumps",
                    "45s trabajo/15s descanso por estación"
                ],
                "STRENGTH ENDURANCE": [
                    "Thrusters con barra - 4x15-20",
                    "Pull-ups - 4x máx repeticiones",
                    "Burpees con barra - 4x12-15",
                    "Rowing machine - 4x500m"
                ],
                "TONING UPPER": [
                    "Press de pecho en máquina - 3x15-18",
                    "Remo en polea - 3x15-18",
                    "Elevaciones laterales - 3x15-18",
                    "Curl de bíceps en cable - 3x15-18"
                ],
                "TONING LOWER": [
                    "Leg press alto rep - 3x20-25",
                    "Sentadillas en multipower - 3x18-20",
                    "Curl femoral - 3x15-18",
                    "Extensión de cuádriceps - 3x18-20"
                ],
                "TONING FULL": [
                    "Circuito máquinas - 3 rondas",
                    "12-15 reps por ejercicio",
                    "Descanso mínimo entre ejercicios"
                ],
                "TONING CIRCUIT": [
                    "Circuito funcional - 3 rondas",
                    "Estaciones variadas gimnasio",
                    "45s trabajo/15s descanso"
                ],
                "EASY FULL BODY": [
                    "Máquinas básicas - 2x10 cada una",
                    "Press de pecho + Remo + Leg press + Extensiones",
                    "Estiramientos - 15 min"
                ],
                "FULL BODY POWER": [
                    "Clean and press - 3x5-6",
                    "Sentadilla con salto - 3x8-10",
                    "Pull-ups explosivos - 3x5-8",
                    "Thrusters pesados - 3x6-8"
                ],
                "COMPETITION PREPARATION": [
                    "Rutina específica competición - 60 min",
                    "Técnica perfecta con peso - 25 min",
                    "Potencia explosiva - 20 min",
                    "Acondicionamiento específico - 15 min"
                ],
                "YOGA": [
                    "Sala de yoga/estiramiento",
                    "Vinyasa flow - 20 min",
                    "Posturas de fuerza - 15 min",
                    "Relajación profunda - 15 min"
                ],
                "DESCANSO": [
                    "Día de descanso activo",
                    "Sauna - 15 min",
                    "Estiramientos en sala - 20 min",
                    "Caminar en cinta suave - 15 min"
                ],
                # MASA MUSCULAR - GIMNASIO
                "PUSH HEAVY": [
                    "Press banca - 5x3-5 (peso alto)",
                    "Press inclinado con mancuernas - 4x6-8",
                    "Press militar - 4x5-6",
                    "Fondos en paralelas - 4x8-10",
                    "Press frances - 3x8-10",
                    "Extensiones de tríceps en polea - 3x10-12"
                ],
                "PULL HEAVY": [
                    "Peso muerto - 5x3-5 (peso alto)",
                    "Dominadas con peso - 4x6-8",
                    "Remo con barra - 4x6-8",
                    "Pullover con mancuerna - 3x8-10",
                    "Curl con barra - 4x8-10",
                    "Curl martillo - 3x10-12"
                ],
                "LEGS HEAVY": [
                    "Sentadilla - 5x5 (peso alto)",
                    "Peso muerto rumano - 4x6-8",
                    "Prensa de piernas - 4x12-15",
                    "Zancadas con barra - 3x10 c/pierna",
                    "Hip thrust - 4x10-12",
                    "Elevación de gemelos - 4x15-20"
                ],
                "CHEST & TRICEPS": [
                    "Press banca - 4x8-10",
                    "Press inclinado - 4x8-10",
                    "Aperturas con mancuernas - 3x10-12",
                    "Fondos en paralelas - 3x10-12",
                    "Press frances - 3x10-12",
                    "Extensiones de tríceps - 3x12-15"
                ],
                "BACK & BICEPS": [
                    "Dominadas - 4x8-12",
                    "Remo con barra - 4x8-10",
                    "Remo en polea baja - 3x10-12",
                    "Pullover - 3x10-12",
                    "Curl con barra - 4x10-12",
                    "Curl concentrado - 3x12-15"
                ],
                "HIIT EXTREME": [
                    "Sprint en cinta - 20s ON/10s OFF x12 rondas",
                    "Burpees - 45s ON/15s OFF x8 rondas",
                    "Battle ropes - 30s ON/30s OFF x10 rondas",
                    "Box jumps - 40s ON/20s OFF x8 rondas",
                    "Mountain climbers - 30s ON/10s OFF x10 rondas"
                ],
                "HIIT TABATA": [
                    "Tabata Burpees - 20s ON/10s OFF x8",
                    "Tabata Sentadillas - 20s ON/10s OFF x8",
                    "Tabata Mountain climbers - 20s ON/10s OFF x8",
                    "Tabata High knees - 20s ON/10s OFF x8"
                ],
                "ENDURANCE INTERVALS": [
                    "Carrera intervalos - 5 min fácil/3 min fuerte x5",
                    "Remo en máquina - 2000m tiempo",
                    "Bicicleta spinning - 45 min con intervalos",
                    "Escaladora - 20 min ritmo constante"
                ],
                "LONG CARDIO": [
                    "Carrera continua - 45-60 min ritmo conversacional",
                    "Bicicleta estática - 60 min intensidad media",
                    "Elíptica - 40 min",
                    "Natación - 30 min (si disponible)"
                ],
                "TONE UPPER": [
                    "Press con mancuernas - 3x12-15",
                    "Elevaciones laterales - 3x15",
                    "Remo con mancuernas - 3x12-15",
                    "Curl de bíceps - 3x15",
                    "Extensiones de tríceps - 3x15",
                    "Plancha - 3x45s"
                ],
                "TONE LOWER": [
                    "Sentadillas con mancuernas - 3x15-20",
                    "Zancadas - 3x12 c/pierna",
                    "Hip thrust - 3x15",
                    "Elevación de pantorrillas - 3x20",
                    "Puente de glúteo - 3x15",
                    "Wall sit - 3x45s"
                ],
                "POWER TRAINING": [
                    "Power clean - 5x3",
                    "Snatch - 5x2",
                    "Box jumps explosivos - 5x5",
                    "Medicine ball slams - 5x8",
                    "Sprint 40m - 6 repeticiones",
                    "Pliométricos específicos - 3 series"
                ]
            }

        return ejercicios_por_tipo.get(tipo_sesion, [
            "Entrenamiento personalizado - No se encontraron ejercicios para: " + tipo_sesion])

    def generar_notificaciones_personalizadas(self):
        """Genera notificaciones personalizadas según el usuario."""
        notificaciones = []

        if self.usuario.objetivo == "Adelgazar":
            notificaciones.append("RECORDATORIO: ¡Profes!¡Recordar ponernos buena nota! ;)")
        elif self.usuario.objetivo == "Ganar masa muscular":
            notificaciones.append("TIP: Consume suficiente proteína hoy")
        else:
            notificaciones.append("MOTIVACIÓN: ¡Sigue así, lo estás haciendo genial!")

        if hasattr(self.usuario, 'categoria_imc'):
            if self.usuario.categoria_imc == "Sobrepeso":
                notificaciones.append("SALUD: Considera aumentar tu actividad cardiovascular")
            elif self.usuario.categoria_imc == "Bajo peso":
                notificaciones.append("NUTRICIÓN: Asegúrate de comer suficientes calorías")

        notificaciones.append("HIDRATACIÓN: Recuerda beber agua regularmente")

        return notificaciones[:3]

    @pyqtSlot()
    def abrir_datos_perfil(self):
        """Abre la ventana de edición de perfil del usuario."""
        self.editar_perfil_window = EditarPerfilScreen(self.usuario, self)
        self.editar_perfil_window.show()

class EditarPerfilScreen(QMainWindow):
    def __init__(self, usuario, main_screen=None):
        super(EditarPerfilScreen, self).__init__()

        self.usuario = usuario
        self.main_screen = main_screen
        uic.loadUi("editar_perfil_screen.ui", self)

        self.db_service = BaseDatosGymSync()

        self.cargar_opciones_objetivo()
        self.cargar_disponibilidad_horaria()
        self.cargar_estilos_vida()
        self.cargar_lugar_entrenamiento()
        self.cargar_genero()

        self.cargar_datos_actuales()

        self.setupConnections()

    def setupConnections(self):
        """Configura las conexiones entre los widgets y los métodos."""
        self.btn_guardar_cambios.clicked.connect(self.guardar_cambios)
        self.btn_cancelar.clicked.connect(self.cancelar_edicion)
        self.btn_salir.clicked.connect(self.cancelar_edicion)

    def cargar_opciones_objetivo(self):
        """Carga las opciones del desplegable de objetivos."""
        objetivos = [
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
        disponibilidad = [
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
        lugar_entrenamiento = [
            "Casa sin equipamiento",
            "Casa con equipamiento",
            "Gimnasio"
        ]
        self.cmb_lugar_entrenamiento.clear()
        self.cmb_lugar_entrenamiento.addItems(lugar_entrenamiento)

    def cargar_genero(self):
        """Gestiona los géneros."""
        genero = [
            "Masculino",
            "Femenino",
            "Otro"
        ]
        self.cmb_genero.clear()
        self.cmb_genero.addItems(genero)

    def cargar_datos_actuales(self):
        """Carga los datos actuales del usuario en los campos del formulario."""
        self.txt_nombre.setText(self.usuario.nombre)
        self.txt_correo.setText(self.usuario.correo)
        self.txt_telefono.setText(self.usuario.telefono)
        self.txt_edad.setText(str(self.usuario.edad))
        self.txt_peso.setText(str(self.usuario.peso))
        self.txt_altura.setText(str(self.usuario.altura))

        self.establecer_seleccion_combobox(self.cmb_genero, self.usuario.genero)
        self.establecer_seleccion_combobox(self.cmb_objetivo, self.usuario.objetivo)
        self.establecer_seleccion_combobox(self.cmb_disponibilidad, self.usuario.disponibilidad)
        self.establecer_seleccion_combobox(self.cmb_estilo_vida, self.usuario.estilo_vida)
        self.establecer_seleccion_combobox(self.cmb_lugar_entrenamiento, self.usuario.lugar_entrenamiento)

        self.txt_correo.setEnabled(False)
        self.txt_correo.setStyleSheet("background-color: #f0f0f0; color: #666666;")

    def establecer_seleccion_combobox(self, combobox, valor_actual):
        """Establece la selección actual en un combobox basado en el valor."""
        for i in range(combobox.count()):
            if combobox.itemText(i) == valor_actual:
                combobox.setCurrentIndex(i)
                break

    @pyqtSlot()
    def guardar_cambios(self):
        """Guarda los cambios realizados en el perfil del usuario."""
        if not self.validar_campos_obligatorios():
            return

        nueva_contraseña = None
        if hasattr(self, 'txt_nueva_contraseña') and self.txt_nueva_contraseña.text():
            if hasattr(self, 'txt_confirmar_nueva_contraseña'):
                if self.txt_nueva_contraseña.text() != self.txt_confirmar_nueva_contraseña.text():
                    self.mostrar_error_validacion(
                        "Error de contraseña",
                        "Las contraseñas nuevas no coinciden."
                    )
                    return
                nueva_contraseña = self.txt_nueva_contraseña.text()

        try:
            usuario_actualizado = self.crear_objeto_usuario_actualizado(nueva_contraseña)

            if self.db_service.actualizar_usuario(usuario_actualizado):
                self.actualizar_usuario_en_memoria(usuario_actualizado)

                QMessageBox.information(
                    self,
                    "Cambios guardados",
                    "Los cambios en tu perfil se han guardado correctamente."
                )

                if self.main_screen:
                    self.main_screen.usuario = usuario_actualizado
                    self.main_screen.configurar_pantalla_usuario()

                self.close()

            else:
                self.mostrar_error_validacion(
                    "Error al guardar",
                    "No se pudieron guardar los cambios. Inténtalo de nuevo."
                )

        except Exception as e:
            self.mostrar_error_validacion(
                "Error inesperado",
                f"Ha ocurrido un error al guardar los cambios: {str(e)}"
            )

    def validar_campos_obligatorios(self):
        """Verifica que todos los campos requeridos estén completados."""
        campos_texto = {
            "Nombre y apellidos": self.txt_nombre.text(),
            "Número de teléfono": self.txt_telefono.text(),
            "Edad": self.txt_edad.text(),
            "Peso": self.txt_peso.text(),
            "Altura": self.txt_altura.text()
        }

        for campo, valor in campos_texto.items():
            if not valor:
                self.mostrar_error_validacion(
                    "Campos incompletos",
                    f"El campo '{campo}' es obligatorio. Por favor, complétalo."
                )
                return False

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

    def crear_objeto_usuario_actualizado(self, nueva_contraseña=None):
        """Crea un objeto Usuario con los datos actualizados del formulario."""
        return Usuario(
            correo=self.usuario.correo,  # El correo no cambia
            contraseña=nueva_contraseña if nueva_contraseña else self.usuario.contraseña,
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

    def actualizar_usuario_en_memoria(self, usuario_actualizado):
        """Actualiza los datos del usuario en memoria."""
        self.usuario.nombre = usuario_actualizado.nombre
        self.usuario.telefono = usuario_actualizado.telefono
        self.usuario.edad = usuario_actualizado.edad
        self.usuario.genero = usuario_actualizado.genero
        self.usuario.peso = usuario_actualizado.peso
        self.usuario.altura = usuario_actualizado.altura
        self.usuario.objetivo = usuario_actualizado.objetivo
        self.usuario.disponibilidad = usuario_actualizado.disponibilidad
        self.usuario.estilo_vida = usuario_actualizado.estilo_vida
        self.usuario.lugar_entrenamiento = usuario_actualizado.lugar_entrenamiento

        if usuario_actualizado.contraseña != self.usuario.contraseña:
            self.usuario.contraseña = usuario_actualizado.contraseña

    def mostrar_error_validacion(self, tipo_error, mensaje):
        """Muestra errores específicos cuando la validación falla."""
        QMessageBox.warning(self, tipo_error, mensaje)

    @pyqtSlot()
    def cancelar_edicion(self):
        """Cancela la edición y vuelve a la pantalla principal."""
        respuesta = QMessageBox.question(
            self,
            "Cancelar edición",
            "¿Estás seguro de que quieres cancelar? Los cambios no guardados se perderán.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            self.close()

class GymSyncApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.mostrar_login()

    def mostrar_login(self):
        self.login_screen = LoginScreen()
        self.login_screen.show()

    def ejecutar(self):
        return self.app.exec_()

def main():
    app = GymSyncApp()
    sys.exit(app.ejecutar())


if __name__ == '__main__':
    main()
