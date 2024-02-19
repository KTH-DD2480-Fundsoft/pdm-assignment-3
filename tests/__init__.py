from pathlib import Path
from atexit import register 

FIXTURES = Path(__file__).parent / "fixtures"

# Here you add your function, initializing all the branches to False
covering = {}
# example: The function 'export' has 24 branches 
covering["export"] = [False for _ in range(24)]
covering["synchronize"] = [False for _ in range(20)]

# This is called at the end, and pretty-prints the branch coverage 
def count_covering():
    for func in covering:
        print(func + ":", end='\n\t')
        s = 0
        for i, e in enumerate(covering[func]):
            print(f"{i}: {e}", end="\n\t")
            s += (1 if e else 0)
        print(f"total coverage: {s / len(covering[func])}")

register(count_covering)
