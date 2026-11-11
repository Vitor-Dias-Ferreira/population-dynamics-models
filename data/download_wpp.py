"""Downloads the UN World Population Prospects 2024 files and keeps only Brazil's rows.

Run from the repository root: python data/download_wpp.py
The four raw files add up to about 270 MB; the filtered CSVs are under 1 MB.
"""
import tempfile
import urllib.request
from pathlib import Path

import pandas as pd

BASE = 'https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/'
BRAZIL = 76  # UN location code
OUT = Path(__file__).parent


def brazil_rows(name, folder):
    path = folder / f'{name}.csv.gz'
    urllib.request.urlretrieve(BASE + path.name, path)
    chunks = pd.read_csv(path, chunksize=500_000, low_memory=False)
    return pd.concat(chunk[chunk['LocID'] == BRAZIL] for chunk in chunks)


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    total = brazil_rows('WPP2024_TotalPopulationBySex', tmp)
    total = total[total['Variant'].isin(['Medium', 'Low', 'High', 'Lower 95 PI', 'Upper 95 PI'])]
    total[['Variant', 'Time', 'PopMale', 'PopFemale', 'PopTotal']].to_csv(OUT / 'brazil_total_population.csv', index=False)

    by_age = brazil_rows('WPP2024_PopulationByAge5GroupSex_Medium', tmp)
    by_age[['Time', 'AgeGrp', 'AgeGrpStart', 'PopMale', 'PopFemale', 'PopTotal']].to_csv(
        OUT / 'brazil_population_by_age.csv', index=False)

    fertility = brazil_rows('WPP2024_Fertility_by_Age5', tmp)
    fertility = fertility[fertility['Variant'] == 'Medium']
    fertility[['Time', 'AgeGrp', 'AgeGrpStart', 'ASFR', 'Births']].to_csv(OUT / 'brazil_fertility_by_age.csv', index=False)

    life = brazil_rows('WPP2024_Life_Table_Abridged_Medium_1950-2023', tmp)
    life = life[life['Sex'] == 'Female']
    life[['Time', 'AgeGrp', 'AgeGrpStart', 'AgeGrpSpan', 'mx', 'qx', 'lx', 'Lx', 'Sx', 'Tx', 'ex']].to_csv(
        OUT / 'brazil_life_table_female.csv', index=False)
print('Saved the Brazil files in', OUT)
