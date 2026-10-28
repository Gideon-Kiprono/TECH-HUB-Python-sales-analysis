import csv
from pathlib import Path

DATA_PATH = Path("data") / "electronics_sales.csv"

with open(DATA_PATH, "r") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)