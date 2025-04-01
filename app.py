import os
import time
import logging
import shutil
import tkinter as tk
from tkinter import messagebox, scrolledtext
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import threading
from datetime import datetime, timedelta

# Función para solicitar autorización
def solicitar_autorizacion():
    response = messagebox.askyesno("Autorizacion", "¿Deseas ejecutar el programa?")
    if not response:
        print("Accion cancelada por el usuario.")
        exit()  # Cerrar el programa si el usuario no da permiso

# Configuración de logging para almacenar los eventos
def configurar_logging():
    log_file = "auditoria_logs.txt"
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

# Función para revisar los logs en busca de registros críticos
def revisar_logs():
    log_file = "auditoria_logs.txt"
    critical_log_file = "logs_criticos.txt"

    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = f.readlines()

        # Revisar si algún evento crítico ha sido registrado
        for log in logs:
            # Ignorar logs generados por el propio programa (palabra "Auditoria" como ejemplo)
            if "Auditoria" in log:
                continue

            if "CRITICAL" in log:  # Buscar registros con nivel CRITICAL
                # Extraer la hora del log (suponiendo que el formato de la fecha es el mismo que en el log)
                timestamp_str = log.split(" - ")[0]  # Obtener la parte antes de " - "
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")

                # Comparar si el log es más antiguo que 2 minutos
                if datetime.now() - timestamp <= timedelta(minutes=2):
                    guardar_log_critico(log, critical_log_file)
                    alertar_critico(log)  # Generar la alerta para logs recientes
                else:
                    # Si el log es viejo (más de 2 minutos), solo agregarlo al box sin alerta
                    log_box.insert(tk.END, f"Log antiguo (sin alerta): {log}\n")
                    log_box.yview(tk.END)
            else:
                # Si no es un log crítico, solo mostrarlo en el box
                log_box.insert(tk.END, f"Log normal: {log}\n")
                log_box.yview(tk.END)
    else:
        print("No se ha encontrado el archivo de logs.")

# Función para guardar los logs críticos en un archivo
def guardar_log_critico(log, critical_log_file):
    # Verifica si el log crítico ya existe, si no, lo agrega
    with open(critical_log_file, "a") as f:
        f.write(log)

    # Crear copias de seguridad si los registros críticos son eliminados
    backup_log_file = "backup_logs_criticos.txt"
    if os.path.exists(critical_log_file):
        shutil.copy(critical_log_file, backup_log_file)

# Función para generar una alerta
def alertar_critico(log):
    messagebox.showwarning("Alerta Critica", f"Se ha detectado un registro critico: {log}")

# Función para ejecutar la auditoría con tiempos variables
def ejecutar_auditoria(log_box, intervalo):
    configurar_logging()  # Configurar logging
    print("Comenzando auditoria...")

    while auditoria_activa.is_set():
        # Simulamos que el programa está funcionando y registrando eventos
        logging.info("Evento normal ocurrido.")
        time.sleep(2)
        logging.warning("Advertencia: Algo no parece estar bien.")
        time.sleep(2)
        logging.critical("¡Error critico! Intento de acceso no autorizado.")
        
        revisar_logs()  # Revisión de logs

        # Actualizar los logs en tiempo real en la GUI
        log_box.insert(tk.END, "Evento normal ocurrido.\n")
        log_box.insert(tk.END, "Advertencia: Algo no parece estar bien.\n")
        log_box.insert(tk.END, "¡Error critico! Intento de acceso no autorizado.\n")
        log_box.yview(tk.END)  # Desplazar la vista hacia abajo

        # Esperar el intervalo configurado antes de revisar nuevamente
        time.sleep(intervalo)

# Función para detener la auditoría
def detener_auditoria():
    auditoria_activa.clear()

# Crear un icono para la bandeja del sistema
def crear_icono_bandeja():
    # Crear una imagen simple para el icono
    icon_image = Image.new('RGB', (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle((0, 0, 64, 64), fill="blue")

    # Función para cerrar el programa
    def cerrar_programa(icon, item):
        icon.stop()
        os._exit(0)  # Salir del programa

    # Crear el menú de la bandeja con opciones
    menu = Menu(MenuItem('Cerrar Auditoria', cerrar_programa))

    # Crear el icono en la bandeja del sistema
    icon = Icon("Auditoria", icon_image, menu=menu)
    icon.run()

# Función para confirmar si el usuario desea cerrar o minimizar el programa
def on_closing():
    respuesta = messagebox.askyesno("Confirmacion", "¿Quieres minimizar la ventana en lugar de cerrarla?")
    if respuesta:
        hide_window()
    else:
        root.quit()

# Función para ocultar la ventana
def hide_window():
    root.withdraw()  # Oculta la ventana de la interfaz
    # Inicia el icono de la bandeja
    threading.Thread(target=crear_icono_bandeja).start()

# Función para abrir los logs en un archivo
def abrir_logs():
    os.system("notepad.exe auditoria_logs.txt")  # Abrir archivo de logs con el Bloc de notas

# Crear la ventana principal de la interfaz
root = tk.Tk()
root.title("Auditoria de Seguridad")
root.geometry("500x350")

# Crear un cuadro de texto más pequeño para mostrar los logs
log_box = scrolledtext.ScrolledText(root, width=60, height=7)
log_box.pack(pady=10)

# Organizar los botones en dos columnas
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

# Botones para cambiar el intervalo de la auditoría
def cambiar_intervalo(intervalo):
    # Inicia la auditoría con el intervalo seleccionado
    auditoria_activa.set()
    threading.Thread(target=ejecutar_auditoria, args=(log_box, intervalo), daemon=True).start()

# Intervalos de auditoría (en segundos)
btn_5min = tk.Button(btn_frame, text="Cada 5 Minutos", command=lambda: cambiar_intervalo(5 * 60))
btn_5min.grid(row=0, column=0, padx=5, pady=5)

btn_10min = tk.Button(btn_frame, text="Cada 10 Minutos", command=lambda: cambiar_intervalo(10 * 60))
btn_10min.grid(row=0, column=1, padx=5, pady=5)

btn_30min = tk.Button(btn_frame, text="Cada 30 Minutos", command=lambda: cambiar_intervalo(30 * 60))
btn_30min.grid(row=1, column=0, padx=5, pady=5)

btn_1h = tk.Button(btn_frame, text="Cada 1 Hora", command=lambda: cambiar_intervalo(60 * 60))
btn_1h.grid(row=1, column=1, padx=5, pady=5)

btn_1d = tk.Button(btn_frame, text="Cada 1 Dia", command=lambda: cambiar_intervalo(24 * 60 * 60))
btn_1d.grid(row=2, column=0, padx=5, pady=5)

# Botón para detener la auditoría
btn_detener = tk.Button(btn_frame, text="Detener Auditoria", command=detener_auditoria)
btn_detener.grid(row=2, column=1, padx=5, pady=5)

# Botón para abrir los logs
btn_ver_logs = tk.Button(root, text="Ver Logs", command=abrir_logs)
btn_ver_logs.pack(pady=5)

# Botón para cerrar la auditoría
btn_cerrar = tk.Button(root, text="Cerrar Auditoria", command=root.quit)
btn_cerrar.pack(pady=5)

# Iniciar el hilo que maneja la auditoría
auditoria_activa = threading.Event()

# Manejo de cierre de ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

# Ejecutar la interfaz
root.mainloop()
