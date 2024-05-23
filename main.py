from fifo import main_fifo
from round_robin import main_round_robin
from sjf import main_sjf
from srtf import main_srtf


def main(excelfile: str):
    main_srtf(excelfile)
    main_sjf(excelfile)
    main_round_robin(excelfile)
    main_fifo(excelfile)


if __name__ == "__main__":
    main("examen.xlsx")
