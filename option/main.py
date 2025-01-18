import tkinter as tk
from tkinter import ttk, messagebox
from pygame import mixer
import threading
from datetime import datetime
from option.timer_module import TimerApp
from option.schedule_table import ScheduleTable
import time  # Import necessário para time.sleep


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer e Agendamento")
        self.root.geometry("800x1000")
        self.root.resizable(False, False)
        mixer.init()

        # Configurar estilos
        self.style = ttk.Style()
        self.configure_styles()

        # Layout principal
        self.create_widgets()

    def configure_styles(self):
        """Configura o estilo geral da aplicação."""
        dark_bg = "#1e1e1e"  # Fundo escuro
        light_text = "#f5f5f5"  # Texto claro
        accent_color = "#ff4500"  # Destaque (laranja)
        input_bg = "#2e2e2e"  # Fundo dos inputs
        input_fg = "#ffffff"  # Texto nos inputs
        table_bg = "#3e3e3e"  # Fundo da tabela
        table_fg = "#f5f5f5"  # Texto da tabela

        # Fundo e texto geral
        self.style.configure("TFrame", background=dark_bg)
        self.style.configure("TLabel", font=("Helvetica", 12), background=dark_bg, foreground=light_text)
        self.style.configure("TButton", font=("Helvetica", 12, "bold"), background=accent_color, foreground="white")
        self.style.map(
            "TButton",
            background=[("active", "#e63e00")],
            foreground=[("active", "white")],
        )

        # Configurações de inputs
        self.style.configure("TEntry", fieldbackground=input_bg, foreground=input_fg, padding=5)
        self.style.configure("Treeview", background=table_bg, foreground=table_fg, rowheight=25)
        self.style.configure("Treeview.Heading", background=accent_color, foreground="white", font=("Helvetica", 12, "bold"))

        # Configurar o fundo principal
        self.root.configure(bg=dark_bg)

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

         # Timer App
        timer_frame = ttk.LabelFrame(main_frame, text="Timer", padding=15, style="TFrame")
        timer_frame.pack(fill="x", pady=20)

        self.timer_app = TimerApp(timer_frame)

        # Agendamento de Alarmes
        schedule_frame = ttk.LabelFrame(main_frame, text="Agendamento de Alarmes", padding=15, style="TFrame")
        schedule_frame.pack(fill="x", pady=20)

        # Entrada para agendamento
        input_frame = ttk.Frame(schedule_frame)
        input_frame.pack(pady=10)

        self.schedule_time_entry = ttk.Entry(input_frame, font=("Helvetica", 14), width=10)
        self.schedule_time_entry.grid(row=0, column=0, padx=10)
        self.add_placeholder(self.schedule_time_entry, "HH:MM")

        self.description_entry = ttk.Entry(input_frame, font=("Helvetica", 14), width=30)
        self.description_entry.grid(row=0, column=1, padx=10)
        self.add_placeholder(self.description_entry, "Descrição do Alarme")

        self.add_schedule_button = ttk.Button(input_frame, text="Adicionar Alarme", command=self.add_alarm)
        self.add_schedule_button.grid(row=0, column=2, padx=10)

        # Tabela de Agendamento
        self.table = ttk.Treeview(schedule_frame, columns=("time", "description"), show="headings")
        self.table.heading("time", text="Horário")
        self.table.heading("description", text="Descrição")
        self.table.column("time", width=100, anchor="center")
        self.table.column("description", width=300, anchor="center")
        self.table.pack(fill="both", pady=10)

        # Botões de Ação
        action_frame = ttk.Frame(schedule_frame)
        action_frame.pack(pady=10)

        self.edit_button = ttk.Button(action_frame, text="Editar Alarme", command=self.edit_alarm)
        self.edit_button.grid(row=0, column=0, padx=10)

        self.delete_button = ttk.Button(action_frame, text="Excluir Alarme", command=self.delete_alarm)
        self.delete_button.grid(row=0, column=1, padx=10)

    def add_placeholder(self, entry, placeholder):
        """Adiciona placeholder a um campo de entrada."""
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground="white")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground="grey")

        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def add_alarm(self):
        """Adiciona um alarme à tabela."""
        try:
            schedule_time = self.schedule_time_entry.get()
            if schedule_time == "HH:MM" or ":" not in schedule_time:
                raise ValueError("Formato inválido para o horário (HH:MM).")
            description = self.description_entry.get()
            if description == "Descrição do Alarme" or not description.strip():
                raise ValueError("Descrição inválida.")
            self.table.insert("", "end", values=(schedule_time.strip(), description.strip()))

            # Resetar inputs após adicionar o alarme
            self.schedule_time_entry.delete(0, tk.END)
            self.schedule_time_entry.insert(0, "HH:MM")
            self.schedule_time_entry.config(foreground="grey")
            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, "Descrição do Alarme")
            self.description_entry.config(foreground="grey")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def edit_alarm(self):
        """Abre a janela de edição para o alarme selecionado."""
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Nenhum alarme selecionado.")
            return
        item = self.table.item(selected_item)
        schedule_time, description = item["values"]
        self.schedule_time_entry.delete(0, tk.END)
        self.schedule_time_entry.insert(0, schedule_time)
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, description)
        self.table.delete(selected_item)

    def delete_alarm(self):
        """Exclui o alarme selecionado."""
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Nenhum alarme selecionado.")
            return
        self.table.delete(selected_item)

    def monitor_alarms(self):
        """Monitora os alarmes e aciona-os no horário definido."""
        while True:
            now = datetime.now().strftime("%H:%M")
            for item in self.table.get_children():
                schedule_time, description = self.table.item(item, "values")
                if now == schedule_time:
                    self.alert_user(description)
                    self.table.delete(item)
            time.sleep(10)

    def alert_user(self, description):
        """Aciona o alerta sonoro."""
        mixer.music.load("alarme.mp3")
        mixer.music.play(-1)
        messagebox.showinfo("Alarme Ativado", f"Descrição: {description}")
        mixer.music.stop()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
