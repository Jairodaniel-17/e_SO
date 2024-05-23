import pandas as pd
from pydantic import BaseModel


class Process(BaseModel):
    pid: str
    t_ll: int  # Tiempo de llegada
    raf: int  # Ráfaga


def fifo(processes):
    tiempo_actual = 0
    tiempo_espera = [0] * len(processes)
    tiempo_respuesta = [0] * len(processes)
    tiempo_inicio = [0] * len(processes)

    for i, proc in enumerate(processes):
        if tiempo_actual < proc.t_ll:
            tiempo_actual = proc.t_ll
        tiempo_inicio[i] = tiempo_actual
        tiempo_espera[i] = tiempo_actual - proc.t_ll
        tiempo_actual += proc.raf
        tiempo_respuesta[i] = tiempo_actual - proc.t_ll

    return tiempo_espera, tiempo_respuesta, tiempo_inicio


def main_fifo(excelfile: str):
    # Leer datos desde el archivo Excel
    df = pd.read_excel(excelfile, sheet_name="base")

    # Crear instancias de Process a partir de los datos del DataFrame
    processes = [
        Process(pid=row["pid"], t_ll=row["t_ll"], raf=row["raf"])
        for index, row in df.iterrows()
    ]

    # Ejecutar FIFO
    tiempo_espera, tiempo_respuesta, tiempo_inicio = fifo(processes)

    # Añadir los resultados al DataFrame
    df["Tiempo de Inicio"] = tiempo_inicio
    df["Tiempo de Espera"] = tiempo_espera
    df["Tiempo de Respuesta"] = tiempo_respuesta

    # Guardar los resultados en una nueva hoja en el mismo archivo
    with pd.ExcelWriter(
        excelfile, mode="a", engine="openpyxl", if_sheet_exists="new"
    ) as writer:
        df.to_excel(writer, sheet_name="FIFO", index=False)
