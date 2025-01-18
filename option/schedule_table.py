import tkinter as tk  
from tkinter import messagebox, ttk
from datetime import datetime


class ScheduleTable:
    def __init__(self, root, parent_frame):
        self.root = root
        self.scheduled_alarms = []  # Lista de alarmes agendados

        # Configuração da tabela
        self.tree = ttk.Treeview(parent_frame, columns=("time", "description"), show="headings")
        self.tree.heading("time", text="Horário")
        self.tree.heading("description", text="Descrição")
        self.tree.column("time", width=150, anchor="center")
        self.tree.column("description", width=400, anchor="w")
        self.tree.pack(fill="x", pady=10)

        # Botões de Ação
        self.action_frame = ttk.Frame(parent_frame)
        self.action_frame.pack(fill="x", pady=10)

        # self.edit_button = ttk.Button(self.action_frame, text="Editar", command=self.edit_selected)
        # self.edit_button.grid(row=0, column=0, padx=10)

        # self.delete_button = ttk.Button(self.action_frame, text="Excluir", command=self.delete_selected)
        # self.delete_button.grid(row=0, column=1, padx=10)

    def add_alarm(self, schedule_time, description):
        """Adiciona um alarme à tabela e organiza os itens por horário."""
        now = datetime.now().strftime("%H:%M")
        if schedule_time <= now:
            messagebox.showerror("Erro", "Não é possível agendar horários no passado.")
            return

        # Adicionar alarme à lista
        self.scheduled_alarms.append((schedule_time, description))
        self.sort_alarms()  # Ordenar os alarmes
        self.refresh_table()  # Atualizar a tabela

    def delete_selected(self):
        """Remove o alarme selecionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Nenhum item selecionado para exclusão.")
            return

        confirm = messagebox.askyesno("Confirmar Exclusão", "Deseja excluir o alarme selecionado?")
        if confirm:
            for item in selected_item:
                item_values = self.tree.item(item)["values"]
                self.tree.delete(item)
                self.scheduled_alarms.remove(tuple(item_values))

    def edit_selected(self):
        """Edita o alarme selecionado."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Nenhum item selecionado para edição.")
            return

        item_values = self.tree.item(selected_item)["values"]
        schedule_time, description = item_values[:2]

        # Janela de edição
        edit_window = EditAlarmWindow(self.root, schedule_time, description, self.update_alarm, selected_item)
        edit_window.show()

    def update_alarm(self, selected_item, new_time, new_description):
        """Atualiza o alarme na tabela e na lista."""
        item_values = self.tree.item(selected_item)["values"]
        self.scheduled_alarms.remove(tuple(item_values))
        self.tree.item(selected_item, values=(new_time, new_description))
        self.scheduled_alarms.append((new_time, new_description))
        self.sort_alarms()  # Ordenar os alarmes após a atualização
        self.refresh_table()

    def sort_alarms(self):
        """Ordena os alarmes por horário em ordem crescente."""
        self.scheduled_alarms.sort(key=lambda alarm: datetime.strptime(alarm[0], "%H:%M"))

    def refresh_table(self):
        """Atualiza a tabela com os alarmes ordenados."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for schedule_time, description in self.scheduled_alarms:
            self.tree.insert("", "end", values=(schedule_time, description))


class EditAlarmWindow:
    def __init__(self, root, schedule_time, description, on_update_callback, selected_item):
        self.root = root
        self.schedule_time = schedule_time
        self.description = description
        self.on_update_callback = on_update_callback
        self.selected_item = selected_item

        self.edit_window = None

    def show(self):
        """Exibe a janela de edição."""
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Editar Alarme")
        self.edit_window.geometry("400x200")

        # Entrada de horário
        tk.Label(self.edit_window, text="Horário (HH:MM):", font=("Arial", 12)).pack(pady=10)
        self.time_entry = tk.Entry(self.edit_window, font=("Arial", 14))
        self.time_entry.insert(0, self.schedule_time)
        self.time_entry.pack(pady=5)

        # Entrada de descrição
        tk.Label(self.edit_window, text="Descrição:", font=("Arial", 12)).pack(pady=10)
        self.description_entry = tk.Entry(self.edit_window, font=("Arial", 14))
        self.description_entry.insert(0, self.description)
        self.description_entry.pack(pady=5)

        # Botões
        save_button = tk.Button(self.edit_window, text="Salvar", font=("Arial", 12), command=self.save_changes)
        save_button.pack(pady=10)

    def save_changes(self):
        """Salva as alterações feitas no alarme."""
        new_time = self.time_entry.get()
        new_description = self.description_entry.get()

        # Validação do horário
        now = datetime.now().strftime("%H:%M")
        if new_time <= now:
            messagebox.showerror("Erro", "Não é possível agendar horários no passado.")
            return

        self.on_update_callback(self.selected_item, new_time, new_description)
        self.edit_window.destroy()
