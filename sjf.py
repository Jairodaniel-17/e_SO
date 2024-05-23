import pandas as pd
from typing import List
from pydantic import BaseModel


class Process(BaseModel):
    pid: str
    t_ll: int  # Tiempo de llegada
    raf: int  # Ráfaga
    tiempo_restante: int = None

    def __init__(self, **data):
        super().__init__(**data)
        self.tiempo_restante = self.raf  # Inicializa tiempo restante igual a la ráfaga


def sjf(processes: List[Process]):
    tiempo_actual = 0
    procesos_ordenados = sorted(processes, key=lambda x: (x.t_ll, x.raf))
    tiempo_espera = [0] * len(procesos_ordenados)
    tiempo_respuesta = [0] * len(procesos_ordenados)
    for i, proc in enumerate(procesos_ordenados):
        if tiempo_actual < proc.t_ll:
            tiempo_actual = proc.t_ll
        tiempo_espera[i] = tiempo_actual - proc.t_ll
        tiempo_respuesta[i] = tiempo_actual + proc.raf - proc.t_ll
        tiempo_actual += proc.raf

    tep = sum(tiempo_espera) / len(procesos_ordenados)
    tpr = sum(tiempo_respuesta) / len(procesos_ordenados)
    return tiempo_espera, tiempo_respuesta, tep, tpr


def main_sjf(excelfile):
    # Leer datos desde el archivo Excel
    df = pd.read_excel(excelfile, sheet_name="base")

    # Crear instancias de Process a partir de los datos del DataFrame
    processes = [
        Process(pid=row["pid"], t_ll=row["t_ll"], raf=row["raf"])
        for index, row in df.iterrows()
    ]

    tiempo_espera, tiempo_respuesta, tep, tpr = sjf(processes)

    # Añadir los resultados al DataFrame y guardarlos
    df["Tiempo de Espera"] = tiempo_espera
    df["Tiempo de Respuesta"] = tiempo_respuesta
    df["Tiempo Espera Promedio"] = [tep] * len(df)
    df["Tiempo Respuesta Promedio"] = [tpr] * len(df)

    # Guardar los resultados en una nueva hoja en el mismo archivo
    with pd.ExcelWriter(
        excelfile, mode="a", engine="openpyxl", if_sheet_exists="new"
    ) as writer:
        df.to_excel(writer, sheet_name="SJF", index=False)
