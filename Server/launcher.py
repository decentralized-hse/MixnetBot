import os
from multiprocessing import Pool
import time

PORTS = [8001, 8002]
# PORTS = list(range(8001, 8020))


def run_process(process):
    p = process.split("*")

    # time.sleep(int(p[0]) * 5)
    os.system(p[1])
    # time.sleep(5)


if __name__ == '__main__':
    processes = [f'{-1 + p % 8000}*python server.py --xport={p}' for p in PORTS]

    pool = Pool(processes=len(PORTS)+2)
    pool.map(run_process, processes)
