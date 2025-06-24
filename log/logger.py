from datetime import datetime

def info(mensaje):
    """Registra un mensaje en el archivo de log."""
    archivo_log = open("log/log.txt", "a", encoding="utf-8")
    archivo_log.write(f"INFO--{datetime.now()}: {mensaje}\n")
    archivo_log.close()


def error(mensaje):
    """Registra un mensaje de error en el archivo de log."""
    archivo_log = open("log/log.txt", "a", encoding="utf-8")
    archivo_log.write(f"ERROR--{datetime.now()}: ERROR: {mensaje}\n")
    archivo_log.close()

def debug(mensaje):
    """Registra un mensaje de depuración en el archivo de log."""
    with open("log/log.txt", "a", encoding="utf-8") as archivo_log:
        archivo_log.write(f"DEBUG--{datetime.now()}: {mensaje}\n")