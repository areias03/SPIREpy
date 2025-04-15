from os import environ

import pandas as pd


def get_ncpus():
    for ev in ["OMP_NUM_THREADS", "NCPUS", "Q_CORES", "Q_CORE"]:
        if ev in environ:
            return int(environ[ev].strip())
    for ev in ["LSB_MCPU_HOSTS"]:
        if ev in environ:
            break
    else:
        return 1
    tokens = environ[ev].strip().split()
    if len(tokens) > 2:
        raise SystemError(
            "Cannot handle this type of environment ({}='{}')".format(ev, environ[ev])
        )
    return int(tokens[1])


def clean_emapper_data(file: str) -> pd.DataFrame:
    data = pd.read_csv(file, skipfooter=3, skiprows=4, sep="\t")
    data.columns = data.columns.str.replace("#", "")
    return data
