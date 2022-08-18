import os
from multiprocessing import Pool
import time

PORTS = [8001, 8002]
# ports = list(range(8001, 8008))


def run_process(process):
    p = process.split("*")

    time.sleep(int(p[0]) * 5)
    os.system(p[1])
    # time.sleep(5)


if __name__ == '__main__':
    processes = [f'{-1 + p % 8000}*python server.py --xport={p}' for p in PORTS]

    pool = Pool(processes=8)
    pool.map(run_process, processes)
