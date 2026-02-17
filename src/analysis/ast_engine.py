import os
import clang.cindex
from rich.tree import Tree
from rich.console import Console

console = Console()

def get_ast_context(file_path, line_number):
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    index = clang.cindex.Index.create()
    tu = index.parse(file_path, args=['-std=c++17'])

    context = {"function": "Global Scope", "variables": [], "snippet": "", "root_node": tu.cursor}

    def walk_tree(node):
        if not node.extent.start.file or node.extent.start.file.name != file_path:
            return
        if node.extent.start.line <= line_number <= node.extent.end.line:
            if node.kind in [clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.CXX_METHOD]:
                context["function"] = node.spelling
            if node.kind == clang.cindex.CursorKind.VAR_DECL and node.location.line <= line_number:
                if node.spelling not in context["variables"]:
                    context["variables"].append(node.spelling)
        for child in node.get_children():
            walk_tree(child)

    walk_tree(tu.cursor)
    with open(file_path, 'r') as f:
        lines = f.readlines()
        idx = line_number - 1
        context["snippet"] = "".join(lines[max(0, idx-1):min(len(lines), idx+2)])
    return context

def visualize_ast(node, tree=None, max_depth=3, source_file=None):
    if tree is None:
        label = node.spelling or 'TranslationUnit'
        tree = Tree(f":evergreen_tree: [bold blue]AST Root[/bold blue]: {label}")
    if max_depth <= 0: return tree
    for child in node.get_children():
        if child.location.file and os.path.normpath(child.location.file.name) == os.path.normpath(source_file):
            branch = tree.add(f"[green]{child.kind.name}[/green]: [yellow]{child.spelling or 'unnamed'}[/yellow]")
            visualize_ast(child, branch, max_depth - 1, source_file)
    return tree

def run_ast_visualization(file_path, line_number, max_depth=3):
    ctx = get_ast_context(file_path, line_number)
    if 'error' in ctx: return
    console.print(f"\n[bold]Scope:[/bold] {ctx['function']} | [bold]Variables:[/bold] {', '.join(ctx['variables']) or 'None'}")
    console.print(f"[bold]Snippet:[/bold]\n[dim]{ctx['snippet']}[/dim]")
    tree = visualize_ast(ctx["root_node"], max_depth=max_depth, source_file=file_path)
    console.print(tree)
    return ctx["root_node"] # Return this for the security scanner