import clang.cindex
import os
from rich.tree import Tree
from rich.console import Console

console = Console()


def get_ast_context(file_path, line_number):

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    if not isinstance(line_number, int) or line_number < 1:
        return {"error": f"Invalid line number: {line_number}"}

    index = clang.cindex.Index.create()
    tu = index.parse(file_path, args=['-std=c++17', '-fsyntax-only'])

    if not tu or not tu.cursor:
        return {"error": "Failed to parse AST"}

    context = {
        "function": "Global Scope",
        "variables": [],
        "snippet": "",
    }

    def walk_tree(node):

        if node.extent.start.line == 0 and node.extent.end.line == 0:
            return

        if node.extent.start.line <= line_number <= node.extent.end.line:

            if node.kind in [clang.cindex.CursorKind.FUNCTION_DECL,
                             clang.cindex.CursorKind.CXX_METHOD]:
                context["function"] = node.spelling

            if node.kind == clang.cindex.CursorKind.VAR_DECL:
                if node.location.line <= line_number:
                    var_name = node.spelling
                    if var_name and var_name not in context["variables"]:
                        context["variables"].append(var_name)

            for child in node.get_children():
                walk_tree(child)

    walk_tree(tu.cursor)

    with open(file_path, 'r') as f:
        lines = f.readlines()
        idx = line_number - 1 
        start = max(0, idx - 1)
        end = min(len(lines), idx + 2)
        context["snippet"] = "".join(lines[start:end])

    return context


def visualize_ast(node, tree=None, max_depth=3, source_file=None):

    if tree is None:
        label = node.spelling or 'TranslationUnit'
        tree = Tree(
            f":evergreen_tree: [bold blue]AST Root[/bold blue]: {label}"
        )

    if max_depth <= 0:
        return tree

    for child in node.get_children():

        child_file = child.location.file
        if child_file is None:
            continue

        if source_file and os.path.normpath(child_file.name) != os.path.normpath(source_file):
            continue

        branch_label = (
            f"[green]{child.kind.name}[/green]: "
            f"[yellow]{child.spelling or 'unnamed'}[/yellow] "
            f"[dim](line {child.location.line})[/dim]" 
        )
        branch = tree.add(branch_label)
        visualize_ast(child, branch, max_depth - 1, source_file)

    return tree


def run_ast_visualization(file_path, line_number, max_depth=3):

    if not os.path.exists(file_path):
        console.print(f"[red]File not found:[/red] {file_path}")
        return

    index = clang.cindex.Index.create()
    tu = index.parse(file_path, args=['-std=c++17', '-fsyntax-only'])

    if not tu or not tu.cursor:
        console.print("[red]Failed to parse AST[/red]")
        return

    ctx = get_ast_context(file_path, line_number)
    if 'error' in ctx:
        console.print(f"[red]Error:[/red] {ctx['error']}")
        return

    console.print(f"\n[bold]Scope:[/bold] {ctx['function']}")
    vars_str = ', '.join(ctx['variables']) if ctx['variables'] else 'None'
    console.print(f"[bold]Variables:[/bold] {vars_str}")
    console.print(f"[bold]Snippet:[/bold]\n{ctx['snippet']}")

    tree = visualize_ast(tu.cursor, max_depth=max_depth, source_file=file_path)
    console.print(tree)