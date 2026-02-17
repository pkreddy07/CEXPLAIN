import os
import sys
import clang.cindex
from rich.console import Console

# Initialize console here to avoid NameError
console = Console()

# --- DYNAMIC PATH SETUP ---
# This ensures it finds your venv no matter where the folder is moved
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_site_packages = os.path.join(base_dir, 'venv', 'Lib', 'site-packages')
if venv_site_packages not in sys.path:
    sys.path.append(venv_site_packages)

try:
    from libclang import libclang
    # Automatically locate the DLL inside the site-packages
    dll_path = os.path.join(os.path.dirname(libclang.__file__), 'native')
    if os.path.exists(dll_path):
        clang.cindex.Config.set_library_path(dll_path)
except Exception:
    # If this fails, we don't crash yet; the AST engine might find it via System PATH
    pass

# Now import project modules
try:
    from analysis.ast_engine import run_ast_visualization
    from core.runner import run_compiler
    from core.parser import parse_diagnostics
except ImportError as e:
    console.print(f"[bold red]Import Error:[/bold red] {e}")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/bold red] python src/main.py <file.cpp>")
        return
    
    target_file = sys.argv[1]
    if not os.path.exists(target_file):
        console.print(f"[bold red]Error:[/bold red] File '{target_file}' not found.")
        return

    console.print(f"\n[bold blue] CEXPLAIN: Analyzing {os.path.basename(target_file)}...[/bold blue]")
    console.print("[dim]──────────────────────────────────────────────────[/dim]")

    # 1. Capture Raw Compiler Output
    raw_output = run_compiler(target_file)

    # 2. Parse into Structured Errors
    found_errors = parse_diagnostics(raw_output)

    if not found_errors:
        console.print("[bold green]✔ No syntax errors found![/bold green]")
    else:
        for err in found_errors:
            # Color code based on severity
            sev = err['severity'].lower()
            color = "red" if "error" in sev else "yellow"
            
            console.print(f"\n[bold {color}][{sev.upper()}][/bold {color}] "
                          f"Line {err['line']}: [white]{err['message']}[/white]")
            
            # 3. Trigger AST Visualization
            try:
                run_ast_visualization(err['file'], err['line'], max_depth=3)
            except Exception as e:
                console.print(f"[dim red]AST Visualization skipped: {e}[/dim red]")
            
            console.print("[dim]──────────────────────────────────────────────────[/dim]")

if __name__ == "__main__":
    main()