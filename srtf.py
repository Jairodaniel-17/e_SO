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


def srtf(processes: List[Process]):
    tiempo_actual = 0
    completados = 0
    n = len(processes)
    tiempo_espera = [0] * n
    tiempo_respuesta = [0] * n

    while completados < n:
        candidatos = [
            proc
            for proc in processes
            if proc.t_ll <= tiempo_actual and proc.tiempo_restante > 0
        ]
        if not candidatos:
            tiempo_actual += 1
            continue

        proceso_actual = min(candidatos, key=lambda x: x.tiempo_restante)
        proceso_actual.tiempo_restante -= 1
        tiempo_actual += 1

        if proceso_actual.tiempo_restante == 0:
            completados += 1
            tiempo_espera[processes.index(proceso_actual)] = (
                tiempo_actual - proceso_actual.t_ll - proceso_actual.raf
            )
            tiempo_respuesta[processes.index(proceso_actual)] = (
                tiempo_actual - proceso_actual.t_ll
            )

    tep = sum(tiempo_espera) / n
    tpr = sum(tiempo_respuesta) / n
    return tiempo_espera, tiempo_respuesta, tep, tpr


def main_srtf(excelfile):
    # Leer datos desde el archivo Excel
    df = pd.read_excel(excelfile, sheet_name="base")

    # Crear instancias de Process a partir de los datos del DataFrame
    processes = [
        Process(pid=row["pid"], t_ll=row["t_ll"], raf=row["raf"])
        for index, row in df.iterrows()
    ]

    tiempo_espera, tiempo_respuesta, tep, tpr = srtf(processes)

    # Añadir los resultados al DataFrame
    df["Tiempo de Espera"] = tiempo_espera
    df["Tiempo de Respuesta"] = tiempo_respuesta
    df["Tiempo Espera Promedio"] = [tep] * len(df)
    df["Tiempo Respuesta Promedio"] = [tpr] * len(df)

    # Guardar los resultados en una nueva hoja en el mismo archivo
    with pd.ExcelWriter(
        excelfile, mode="a", engine="openpyxl", if_sheet_exists="new"
    ) as writer:
        df.to_excel(writer, sheet_name="srtf", index=False)
