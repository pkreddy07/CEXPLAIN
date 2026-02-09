import subprocess

def run_compiler(path):
    cmd = ["g++", "-fsyntax-only", "-fdiagnostics-color=never", path]

    try:
        result = subprocess.run(cmd, capture_output = True, text = True)
        return result.stderr
    except FileNotFoundError:
        return "Error: g++ not found. Please install a C++ compiler"