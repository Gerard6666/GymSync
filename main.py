import sys
import os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QLabel, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt


class GymSyncApp:
    def __init__(self):
        # Initialize the application
        self.app = QtWidgets.QApplication(sys.argv)

        # Load the UI file
        self.window = uic.loadUi("GymSync.ui")

        # Set default page
        self.window.stackedWidget.setCurrentWidget(self.window.login_page)

        # Replace image references with text labels since images don't exist
        self.setup_placeholder_images()

        # Connect buttons
        self.connect_buttons()

        # Sample data
        self.user_credentials = {"user@gmail.com": "1234"}
        self.current_user = ""

        # Initialize workout data
        self.workout_data = {
            "Monday": {"name": "ARM DAY",
                       "exercises": ["EJERCICIO 1", "EJERCICIO 2", "EJERCICIO 3", "EJERCICIO 4", "EJERCICIO 5"]},
            "Tuesday": {"name": "PUSH DAY",
                        "exercises": ["Bench Press", "Shoulder Press", "Tricep Extensions", "Chest Fly", "Push-ups"]},
            "Wednesday": {"name": "LEGS DAY",
                          "exercises": ["Squats", "Leg Press", "Lunges", "Leg Extensions", "Calf Raises"]}
        }

        # Initialize progress data
        self.progress_data = {
            "weekly": [60, 75, 50, 80, 65, 90, 70],
            "monthly": [65, 70, 75, 80],
            "chart_data": {
                "bench": [50, 55, 60, 65, 70],
                "squat": [80, 85, 90, 95, 100],
                "deadlift": [100, 105, 110, 115, 120]
            },
            "attendance": [
                [1, 1, 1, 0, 1, 1, 1],
                [1, 1, 0, 1, 1, 1, 0],
                [1, 0, 1, 1, 1, 0, 1],
                [0, 1, 1, 1, 0, 1, 1]
            ]
        }

        # Setup the attendance table
        self.setup_attendance_table()

    def setup_placeholder_images(self):
        # Replace image references with text since we don't have the actual images
        self.window.logo_label.setText("GYM SYNC")
        self.window.logo_label.setStyleSheet("font-size: 24pt; font-weight: bold;")

        self.window.email_icon.setText("@")
        self.window.email_icon.setStyleSheet("font-size: 16pt;")

        self.window.password_icon.setText("🔒")
        self.window.password_icon.setStyleSheet("font-size: 16pt;")

    def connect_buttons(self):
        # Login page
        self.window.login_button.clicked.connect(self.login)
        self.window.register_button.clicked.connect(self.go_to_register)

        # Main page
        self.window.profile_button.clicked.connect(
            lambda: self.window.stackedWidget.setCurrentWidget(self.window.profile_page))
        self.window.progress_button.clicked.connect(
            lambda: self.window.stackedWidget.setCurrentWidget(self.window.progress_page))

        # Profile page
        self.window.save_profile_button.clicked.connect(self.save_profile)
        self.window.cancel_profile_button.clicked.connect(
            lambda: self.window.stackedWidget.setCurrentWidget(self.window.main_page))

        # Register page
        self.window.save_register_button.clicked.connect(self.register_user)

        # Progress page
        self.window.back_to_main_button.clicked.connect(
            lambda: self.window.stackedWidget.setCurrentWidget(self.window.main_page))

    def login(self):
        email = self.window.email_input.text()
        password = self.window.password_input.text()

        if len(email) == 0 or len(password) == 0:
            self.window.login_error.setText("Por favor complete los campos.")
            return

        if email in self.user_credentials and self.user_credentials[email] == password:
            self.current_user = email
            self.window.user_email_label.setText(email)
            self.setup_main_page()
            self.window.stackedWidget.setCurrentWidget(self.window.main_page)
            self.window.email_input.clear()
            self.window.password_input.clear()
            self.window.login_error.clear()
        else:
            self.window.login_error.setText("Usuario o contraseña incorrectos.")
            self.window.email_input.clear()
            self.window.password_input.clear()

    def go_to_register(self):
        self.window.stackedWidget.setCurrentWidget(self.window.register_page)

    def register_user(self):
        # Get registration data
        email = self.window.reg_email_input.text()
        password = self.window.reg_password_input.text()
        confirm_password = self.window.reg_confirm_password_input.text()

        if not email or not password or not confirm_password:
            QMessageBox.warning(self.window, "Error", "Por favor complete todos los campos obligatorios.")
            return

        if password != confirm_password:
            QMessageBox.warning(self.window, "Error", "Las contraseñas no coinciden.")
            return

        if email in self.user_credentials:
            QMessageBox.warning(self.window, "Error", "Este correo ya está registrado.")
            return

        # Register the user
        self.user_credentials[email] = password
        QMessageBox.information(self.window, "Éxito", "Usuario registrado correctamente.")
        self.window.stackedWidget.setCurrentWidget(self.window.login_page)

    def setup_main_page(self):
        # Set up workout schedule
        for day, workout in self.workout_data.items():
            if hasattr(self.window, f"{day.lower()}_label"):
                day_label = getattr(self.window, f"{day.lower()}_label")
                day_label.setText(f"{day}\n{workout['name']}")

        # Set up exercise list for Monday (default)
        self.update_exercise_list("Monday")

    def update_exercise_list(self, day):
        if day in self.workout_data:
            exercises = self.workout_data[day]["exercises"]
            exercise_layout = QtWidgets.QVBoxLayout()

            # Clear previous layout
            if self.window.exercise_container.layout():
                QtWidgets.QWidget().setLayout(self.window.exercise_container.layout())

            # Add new exercise labels
            for exercise in exercises:
                exercise_item = QtWidgets.QLabel(exercise)
                exercise_layout.addWidget(exercise_item)

            self.window.exercise_container.setLayout(exercise_layout)

    def setup_attendance_table(self):
        # Setup attendance table with red/green cells
        table = self.window.attendance_table

        # Fill table with attendance data
        for row in range(4):
            for col in range(7):
                item = QTableWidgetItem()
                if self.progress_data["attendance"][row][col] == 1:
                    item.setBackground(QColor(0, 255, 0))  # Green for attended
                else:
                    item.setBackground(QColor(255, 0, 0))  # Red for missed
                table.setItem(row, col, item)

    def save_profile(self):
        # Here you would save the profile data
        QMessageBox.information(self.window, "Éxito", "Perfil actualizado correctamente.")
        self.window.stackedWidget.setCurrentWidget(self.window.main_page)

    def run(self):
        self.window.show()
        return self.app.exec_()


if __name__ == "__main__":
    app = GymSyncApp()
    sys.exit(app.run())