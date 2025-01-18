import time
import tkinter as tk
from tkinter import ttk, messagebox
from pygame import mixer
import threading
from datetime import datetime


class TimerApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame

        # Variáveis de controle para os timers
        self.timer_seconds_running = False
        self.timer_hour_running = False

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Container do Timer
        timer_frame = ttk.Frame(self.parent_frame)
        timer_frame.pack(pady=20, fill="x")

        # Timer em Segundos
        self.second_label = ttk.Label(timer_frame, text="Timer em Segundos:", font=("Arial", 14))
        self.second_label.grid(row=0, column=0, padx=10, sticky="w")
        self.second_entry = ttk.Entry(timer_frame, font=("Arial", 14), width=10, foreground="grey")
        self.second_entry.grid(row=0, column=1, padx=10)
        self.add_placeholder(self.second_entry, "Insira segundos")

        self.second_start_button = ttk.Button(timer_frame, text="Iniciar", command=self.start_timer_seconds)
        self.second_start_button.grid(row=0, column=2, padx=5)
        self.second_cancel_button = ttk.Button(timer_frame, text="Cancelar", command=self.cancel_timer_seconds)
        self.second_cancel_button.grid(row=0, column=3, padx=5)

        # Timer em Hora
        self.hour_minute_label = ttk.Label(timer_frame, text="Timer em Hora (HH:MM):", font=("Arial", 14))
        self.hour_minute_label.grid(row=1, column=0, padx=10, sticky="w")
        self.hour_minute_entry = ttk.Entry(timer_frame, font=("Arial", 14), width=10, foreground="grey")
        self.hour_minute_entry.grid(row=1, column=1, padx=10)
        self.add_placeholder(self.hour_minute_entry, "HH:MM")

        self.hour_minute_start_button = ttk.Button(timer_frame, text="Iniciar", command=self.start_timer_hour)
        self.hour_minute_start_button.grid(row=1, column=2, padx=5)
        self.hour_minute_cancel_button = ttk.Button(timer_frame, text="Cancelar", command=self.cancel_timer_hour)
        self.hour_minute_cancel_button.grid(row=1, column=3, padx=5)

        # TextBox para exibir dados detalhados
        self.log_label = ttk.Label(self.parent_frame, text="Detalhes do Timer:", font=("Arial", 14))
        self.log_label.pack(pady=10)
        self.log_textbox = tk.Text(self.parent_frame, height=10, width=70, font=("Arial", 12), state="disabled")
        self.log_textbox.pack(pady=10)

    def add_placeholder(self, entry, placeholder):
        """Adiciona placeholder a um campo de entrada."""
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground="black")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground="grey")

        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def log_details(self, message):
        """Adiciona informações ao TextBox."""
        self.log_textbox.config(state="normal")
        self.log_textbox.insert(tk.END, f"{message}\n")
        self.log_textbox.see(tk.END)  # Rola até o final
        self.log_textbox.config(state="disabled")

    def start_timer_seconds(self):
        if self.timer_seconds_running:
            self.show_warning("Timer em segundos já está em execução.")
            return
        try:
            seconds = int(self.second_entry.get())
            if seconds <= 0:
                raise ValueError
            self.timer_seconds_running = True
            self.second_entry.config(state="disabled")
            self.log_details(f"Iniciando Timer em Segundos: {seconds} segundos.")
            threading.Thread(target=self.run_timer_seconds, args=(seconds,), daemon=True).start()
        except ValueError:
            self.show_error("Por favor, insira um número válido maior que zero.")

    def run_timer_seconds(self, seconds):
        for remaining in range(seconds, 0, -1):
            if not self.timer_seconds_running:
                return
            time.sleep(1)
        if self.timer_seconds_running:
            self.alert_user()
        self.reset_inputs()

    def cancel_timer_seconds(self):
        """Cancela o timer em segundos e reseta os inputs."""
        if self.timer_seconds_running:
            self.timer_seconds_running = False
            self.log_details("Timer em segundos cancelado.")
            self.reset_inputs()
            self.show_info("O timer em segundos foi cancelado.")

    def reset_inputs(self):
        """Reseta os campos de entrada e reativa os botões."""
        self.second_entry.config(state="normal")
        self.second_entry.delete(0, tk.END)
        self.second_entry.insert(0, "Insira segundos")
        self.second_entry.config(foreground="grey")

        self.hour_minute_entry.config(state="normal")
        self.hour_minute_entry.delete(0, tk.END)
        self.hour_minute_entry.insert(0, "HH:MM")
        self.hour_minute_entry.config(foreground="grey")

    def start_timer_hour(self):
        if self.timer_hour_running:
            self.show_warning("Timer em hora já está em execução.")
            return
        try:
            hour_minute = self.hour_minute_entry.get()
            if ":" not in hour_minute:
                raise ValueError
            target_hour, target_minute = map(int, hour_minute.split(":"))
            now = datetime.now()
            target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            if target_time <= now:
                self.show_error("A hora definida deve ser no futuro.")
                return
            self.timer_hour_running = True
            self.hour_minute_entry.config(state="disabled")
            self.log_details(f"Iniciando Timer em Hora: {hour_minute}.")
            threading.Thread(target=self.run_timer_hour, args=(target_time,), daemon=True).start()
        except ValueError:
            self.show_error("Por favor, insira a hora no formato HH:MM.")

    def run_timer_hour(self, target_time):
        while self.timer_hour_running:
            now = datetime.now()
            if now >= target_time:
                if self.timer_hour_running:
                    self.alert_user()
                self.reset_inputs()
                break
            time.sleep(1)

    def cancel_timer_hour(self):
        """Cancela o timer em hora e reseta os inputs."""
        if self.timer_hour_running:
            self.timer_hour_running = False
            self.log_details("Timer em hora cancelado.")
            self.reset_inputs()
            self.show_info("O timer em hora foi cancelado.")

    def alert_user(self):
        mixer.music.load("alarme.mp3")
        mixer.music.play(-1)
        self.log_details("⏰ Alarme disparado!")
        self.show_info("⏰ Tempo esgotado!")
        mixer.music.stop()

    def show_error(self, message):
        tk.messagebox.showerror("Erro", message)

    def show_info(self, message):
        tk.messagebox.showinfo("Informação", message)

    def show_warning(self, message):
        tk.messagebox.showwarning("Aviso", message)
