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
        self.tiempo_restante = self.raf


def round_robin(processes: List[Process], quantum: int):
    tiempo_actual = 0
    cola = []
    tiempo_espera = [0] * len(processes)
    tiempo_respuesta = [0] * len(processes)
    procesados = [False] * len(processes)  # Para marcar la primera respuesta

    while any(p.tiempo_restante > 0 for p in processes):
        # Añadir procesos que llegan al tiempo actual
        cola.extend([p for p in processes if p.t_ll == tiempo_actual and p not in cola])

        if cola:
            proc = cola.pop(0)
            tiempo_real = min(proc.tiempo_restante, quantum)
            tiempo_actual += tiempo_real
            proc.tiempo_restante -= tiempo_real

            # Actualizar tiempos de espera y respuesta
            if proc.tiempo_restante == 0:
                tiempo_espera[processes.index(proc)] = (
                    tiempo_actual - proc.raf - proc.t_ll
                )
                tiempo_respuesta[processes.index(proc)] = tiempo_actual - proc.t_ll
            cola.extend(
                [
                    p
                    for p in processes
                    if p.t_ll <= tiempo_actual
                    and p.tiempo_restante > 0
                    and p not in cola
                ]
            )
            for p in processes:
                if p != proc and p.tiempo_restante > 0 and p.t_ll < tiempo_actual:
                    tiempo_espera[processes.index(p)] += tiempo_real
        else:
            tiempo_actual += 1  # Avanzar tiempo si no hay procesos listos

    tep = sum(tiempo_espera) / len(processes)
    tpr = sum(tiempo_respuesta) / len(processes)
    return tiempo_espera, tiempo_respuesta, tep, tpr


def main_round_robin(excelfile):
    df = pd.read_excel(excelfile, sheet_name="base")
    processes = [
        Process(pid=row["pid"], t_ll=row["t_ll"], raf=row["raf"])
        for index, row in df.iterrows()
    ]
    quantum = 2
    tiempo_espera, tiempo_respuesta, tep, tpr = round_robin(processes, quantum)
    df["Tiempo de Espera"] = tiempo_espera
    df["Tiempo de Respuesta"] = tiempo_respuesta
    df["Tiempo Espera Promedio"] = [tep] * len(df)
    df["Tiempo Respuesta Promedio"] = [tpr] * len(df)

    with pd.ExcelWriter(
        excelfile, mode="a", engine="openpyxl", if_sheet_exists="replace"
    ) as writer:
        df.to_excel(writer, sheet_name="Round_Robin", index=False)
