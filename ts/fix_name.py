import os

file_list = [
    x for x in os.listdir(".") if x.endswith(".ts")
]

for old_file_name in file_list:
    if len(old_file_name) == len("0000.ts"):
        continue

    file_id = int(old_file_name[:-3])
    new_file_name = f"{file_id:04d}.ts"

    os.rename(old_file_name, new_file_name)
