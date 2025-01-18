from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
app.secret_key = "secret-key"

# Lista de alarmes
alarms = []

# Estados dos inputs
input_states = {
    "seconds": "enabled",
    "date": "enabled"
}

# Threads ativas para timers
active_timers = []


def validate_alarm(time, description):
    """Valida os dados do alarme."""
    if not time:
        return False, "Preencha o horário!"
    try:
        datetime.strptime(time, "%H:%M")
    except ValueError:
        return False, "Formato inválido para o horário (HH:MM)."
    return True, ""


def validate_timer_seconds(seconds):
    """Valida o timer em segundos."""
    try:
        seconds = int(seconds)
        if seconds <= 0:
            return False, "O número de segundos deve ser maior que zero."
        return True, ""
    except ValueError:
        return False, "Por favor, insira um número válido de segundos."


def run_timer_seconds(seconds, description):
    """Executa o timer em segundos."""
    global input_states
    time.sleep(seconds)
    print(f"⏰ Timer de {seconds} segundos finalizado! Descrição: {description}")
    input_states["seconds"] = "enabled"  # Habilitar o input novamente


def run_timer_date(target_time, description):
    """Executa o timer com base em uma data específica."""
    global input_states
    now = datetime.now()
    while now < target_time:
        time.sleep(1)
        now = datetime.now()
    print(f"⏰ Alarme ativado para {target_time.strftime('%Y-%m-%d %H:%M')} - Descrição: {description}")
    input_states["date"] = "enabled"  # Habilitar o input novamente


@app.route("/", methods=["GET", "POST"])
def index():
    global alarms, input_states
    if request.method == "POST":
        if "add_alarm" in request.form:
            # Adicionar agendamento por horário (HH:MM)
            time_input = request.form.get("time")
            description = request.form.get("description") or "Sem descrição"

            # Validar dados do alarme
            is_valid, error_message = validate_alarm(time_input, description)
            if not is_valid:
                flash(error_message, "error")
            else:
                alarms.append({"time": time_input, "description": description})
                flash("Alarme agendado com sucesso!", "success")

        elif "start_timer_seconds" in request.form:
            # Iniciar timer em segundos
            seconds = request.form.get("seconds")
            description = request.form.get("description_seconds") or "Sem descrição"

            is_valid, error_message = validate_timer_seconds(seconds)
            if not is_valid:
                flash(error_message, "error")
            else:
                seconds = int(seconds)
                flash(f"Timer de {seconds} segundos iniciado!", "success")
                input_states["seconds"] = "disabled"  # Desabilitar o input
                thread = threading.Thread(target=run_timer_seconds, args=(seconds, description), daemon=True)
                thread.start()
                active_timers.append(thread)

        elif "start_timer_date" in request.form:
            # Iniciar timer por data
            date_input = request.form.get("date")
            description = request.form.get("description_date") or "Sem descrição"

            try:
                target_time = datetime.strptime(date_input, "%Y-%m-%d %H:%M")
                if target_time <= datetime.now():
                    flash("A data/hora deve ser no futuro!", "error")
                else:
                    flash(f"Timer para {target_time.strftime('%Y-%m-%d %H:%M')} iniciado!", "success")
                    input_states["date"] = "disabled"  # Desabilitar o input
                    thread = threading.Thread(target=run_timer_date, args=(target_time, description), daemon=True)
                    thread.start()
                    active_timers.append(thread)
            except ValueError:
                flash("Formato inválido para a data (YYYY-MM-DD HH:MM).", "error")

    return render_template("index.html", alarms=alarms, input_states=input_states)


@app.route("/delete/<int:alarm_id>")
def delete(alarm_id):
    """Exclui o alarme com base no ID fornecido."""
    global alarms
    if 0 <= alarm_id < len(alarms):
        alarms.pop(alarm_id)
        flash("Alarme excluído com sucesso!", "success")
    else:
        flash("Alarme inválido!", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)