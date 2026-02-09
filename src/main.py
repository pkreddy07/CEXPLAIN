from core.runner import run_compiler
from core.parser import parse_diagnostics
import sys

def main() :
    if (len(sys.argv) < 2) :
        print("Usage: python src/main.py <file.cpp>")
        return
    
    target_file = sys.argv[1]
    print(f"--- Analyzing {target_file} ---")

    raw_output = run_compiler(target_file)

    found_errors = parse_diagnostics(raw_output)

    if not found_errors :
        print("No errors found! Code looks clean")
    else :
        for err in found_errors :
            print(f"[{err['severity'].upper()}] Line {err['line']}: {err['message']}")
    
if __name__ == "__main__" :
    main()