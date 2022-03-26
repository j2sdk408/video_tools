#!/usr/bin/env python3
import sys

file_name = sys.argv[1]

with open(file_name, "r") as f:
    content = f.read().splitlines()


content = [x.strip() for x in content if x.strip()]
content = [x for x in content if not x.startswith("#")]

print("#!/usr/bin/env bash")

for idx, line in enumerate(content):
    print(
        f"wget {line} -O {idx:05d}.ts"
    )
