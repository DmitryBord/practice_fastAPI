from pathlib import Path

path = Path(__file__).resolve().parent

print(path/"tmp/file.txt")