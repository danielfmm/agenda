import datetime
import json

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput


def date_now():
    return str(datetime.datetime.now().strftime("%d/%m/%Y"))


class Appointment:
    def __init__(self, client, scheduled_time):
        self.client = client
        self.scheduled_time = scheduled_time

    def __str__(self):
        return f"{self.client}: {self.scheduled_time.strftime('%d/%m/%Y %H:%M')}"

    def to_dict(self):
        return {
            "client": self.client,
            "scheduled_time": self.scheduled_time.strftime('%d/%m/%Y %H:%M')
        }

    @classmethod
    def from_dict(cls, appointment_dict):
        scheduled_time = datetime.datetime.strptime(
            appointment_dict['scheduled_time'], '%d/%m/%Y %H:%M')
        return cls(appointment_dict['client'], scheduled_time)


class Schedule:
    def __init__(self, file_path="data.json"):
        self.file_path = file_path

    def _load_data(self):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        return data

    def _save_data(self, data):
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    def schedule_appointment(self, client, scheduled_time):
        appointment = Appointment(client, scheduled_time)
        data = self._load_data()
        data.append(appointment.to_dict())
        self._save_data(data)

    def check_availability(self, scheduled_time):
        data = self._load_data()
        appointments = [Appointment.from_dict(a) for a in data]
        for appointment in appointments:
            if appointment.scheduled_time.date() == scheduled_time.date() and abs((appointment.scheduled_time - scheduled_time).total_seconds()) < 40 * 60:
                return False
        return True

    def list_appointments(self, date):
        data = self._load_data()
        appointments = [Appointment.from_dict(a) for a in data]
        appointments_on_date = [
            a for a in appointments if a.scheduled_time.date() == date.date()]
        return appointments_on_date


class ScheduleApp(App):
    def build(self):
        self.schedule = Schedule()

        main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.result_label = Label(text="Selecione uma opção abaixo:")
        main_layout.add_widget(self.result_label)

        button_layout = BoxLayout(orientation="horizontal", spacing=10)
        schedule_button = Button(text="Marcar consulta")
        schedule_button.bind(on_press=self.show_schedule_popup)
        button_layout.add_widget(schedule_button)

        list_button = Button(text="Listar consultas por data")
        list_button.bind(on_press=self.show_list_popup)
        button_layout.add_widget(list_button)

        main_layout.add_widget(button_layout)

        return main_layout

    def show_schedule_popup(self, _):
        popup_layout = BoxLayout(
            orientation="vertical", padding=10, spacing=10)

        client_input = TextInput(hint_text="Nome do cliente")
        popup_layout.add_widget(client_input)

        date_input = TextInput(
            text=date_now(), hint_text="Data da consulta (dd/mm/aaaa)")
        popup_layout.add_widget(date_input)

        hour_input = TextInput(hint_text="Hora da consulta (9 a 16)")
        popup_layout.add_widget(hour_input)

        minute_input = TextInput(hint_text="Minuto da consulta (0 a 59)")
        popup_layout.add_widget(minute_input)

        submit_button = Button(text="Marcar consulta")
        submit_button.bind(on_press=lambda x: self.schedule_appointment(
            client_input, date_input, hour_input, minute_input))
        popup_layout.add_widget(submit_button)

        cancel_button = Button(text="Cancelar")
        cancel_button.bind(on_press=lambda x: self.dismiss_popup())
        popup_layout.add_widget(cancel_button)

        self.popup = Popup(title="Marcar consulta", content=popup_layout, size_hint=(
            None, None), size=(400, 400))
        self.popup.open()

    def show_list_popup(self, _):
        popup_layout = BoxLayout(
            orientation="vertical", padding=10, spacing=10)

        date_input = TextInput(
            text=date_now(), hint_text="Data das consultas (dd/mm/aaaa)")
        popup_layout.add_widget(date_input)

        submit_button = Button(text="Listar consultas")
        submit_button.bind(
            on_press=lambda x: self.list_appointments(date_input))
        popup_layout.add_widget(submit_button)

        cancel_button = Button(text="Cancelar")
        cancel_button.bind(on_press=lambda x: self.dismiss_popup())
        popup_layout.add_widget(cancel_button)

        self.popup = Popup(title="Listar consultas por data",
                           content=popup_layout, size_hint=(None, None), size=(400, 250))
        self.popup.open()

    def schedule_appointment(self, client_input, date_input, hour_input, minute_input):
        client = client_input.text
        date = date_input.text
        hour = int(hour_input.text)
        minute = int(minute_input.text)

        if 9 <= hour <= 16 and 0 <= minute <= 59:
            if date:
                schedule_time = datetime.datetime.strptime(
                    date + f" {hour}:{minute}", "%d/%m/%Y %H:%M")
            else:
                schedule_time = datetime.datetime.now().replace(
                    hour=hour, minute=minute, second=0, microsecond=0)

            if self.schedule.check_availability(schedule_time):
                self.schedule.schedule_appointment(client, schedule_time)
                self.result_label.text = "Consulta marcada com sucesso!"
            else:
                self.result_label.text = "Desculpe, este horário já está reservado."
        else:
            self.result_label.text = "Horário inválido. Tente novamente."

        self.dismiss_popup()

    def list_appointments(self, date_input):
        date = date_input.text
        date_obj = datetime.datetime.strptime(date, "%d/%m/%Y")
        appointments = self.schedule.list_appointments(date_obj)
        if appointments:
            self.result_label.text = f"Consultas marcadas em {date_obj.strftime('%d/%m/%Y')}:\n" + "\n".join(
                str(appointment) for appointment in appointments)
        else:
            self.result_label.text = "Nenhuma consulta marcada nesta data."

        self.dismiss_popup()

    def dismiss_popup(self):
        self.popup.dismiss()


if __name__ == "__main__":
    ScheduleApp().run()
