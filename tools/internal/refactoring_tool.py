import ast
import astor
import difflib
import subprocess
import tempfile
import os

class RefactoringTool:
    def __init__(self):
        pass

    def refactor_code(self, code: str) -> str:
        """
        Perform automated code refactoring and optimization on Python code.

        Args:
            code (str): The original Python source code.

        Returns:
            str: The refactored and optimized Python source code.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Input code is not valid Python: {e}")

        # Apply transformations
        tree = self._remove_unused_imports(tree)
        tree = self._optimize_imports(tree)
        tree = self._simplify_if_statements(tree)
        tree = self._format_code(tree)

        refactored_code = astor.to_source(tree)

        # Optionally run autopep8 for style consistency
        refactored_code = self._run_autopep8(refactored_code)

        return refactored_code

    def _remove_unused_imports(self, tree: ast.AST) -> ast.AST:
        """
        Remove imports that are not used anywhere in the code.
        """
        # Collect all imported names
        import_names = set()
        import_nodes = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
                for alias in node.names:
                    import_names.add(alias.asname or alias.name.split('.')[0])

        # Collect all used names
        class NameCollector(ast.NodeVisitor):
            def __init__(self):
                self.used_names = set()
            def visit_Name(self, node):
                self.used_names.add(node.id)

        collector = NameCollector()
        collector.visit(tree)

        # Filter out unused imports
        new_body = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Keep only those aliases that are used
                used_aliases = [alias for alias in node.names
                                if (alias.asname or alias.name.split('.')[0]) in collector.used_names]
                if used_aliases:
                    node.names = used_aliases
                    new_body.append(node)
                # else skip this import completely
            else:
                new_body.append(node)

        tree.body = new_body
        return tree

    def _optimize_imports(self, tree: ast.AST) -> ast.AST:
        """
        Sort imports alphabetically and group standard library, third party, local imports.
        Currently, just sorts import statements alphabetically.
        """
        import_nodes = []
        other_nodes = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
            else:
                other_nodes.append(node)

        def import_key(node):
            if isinstance(node, ast.Import):
                return node.names[0].name
            elif isinstance(node, ast.ImportFrom):
                return (node.module or '')
            return ''

        import_nodes.sort(key=import_key)
        tree.body = import_nodes + other_nodes
        return tree

    def _simplify_if_statements(self, tree: ast.AST) -> ast.AST:
        """
        Simplify if statements like:
        if cond:
            return True
        else:
            return False
        -> return cond

        Also handles negated returns.
        """
        class IfSimplifier(ast.NodeTransformer):
            def visit_If(self, node):
                self.generic_visit(node)

                # Check pattern if <cond>: return True else return False
                if (len(node.body) == 1 and isinstance(node.body[0], ast.Return) and
                    len(node.orelse) == 1 and isinstance(node.orelse[0], ast.Return)):
                    ret_body = node.body[0]
                    ret_else = node.orelse[0]
                    if (isinstance(ret_body.value, ast.Constant) and isinstance(ret_else.value, ast.Constant)):
                        if ret_body.value.value is True and ret_else.value.value is False:
                            return ast.Return(value=node.test)
                        elif ret_body.value.value is False and ret_else.value.value is True:
                            return ast.Return(value=ast.UnaryOp(op=ast.Not(), operand=node.test))
                return node

        simplifier = IfSimplifier()
        tree = simplifier.visit(tree)
        ast.fix_missing_locations(tree)
        return tree

    def _format_code(self, tree: ast.AST) -> ast.AST:
        """
        Placeholder for future AST-based formatting if needed.
        Currently does nothing.
        """
        return tree

    def _run_autopep8(self, code: str) -> str:
        """
        Run autopep8 on the code to enforce PEP8 style.
        Requires autopep8 to be installed.
        """
        try:
            import autopep8
            fixed_code = autopep8.fix_code(code, options={'aggressive': 1})
            return fixed_code
        except ImportError:
            # autopep8 not installed, return original code
            return code

    def diff(self, original_code: str, refactored_code: str) -> str:
        """
        Generate a unified diff between original and refactored code.
        """
        original_lines = original_code.splitlines(keepends=True)
        refactored_lines = refactored_code.splitlines(keepends=True)
        diff_lines = difflib.unified_diff(
            original_lines, refactored_lines,
            fromfile='original.py', tofile='refactored.py', lineterm=''
        )
        return ''.join(diff_lines)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python refactoring_tool.py <python_source_file>")
        sys.exit(1)

    source_path = sys.argv[1]
    with open(source_path, 'r', encoding='utf-8') as f:
        original_code = f.read()

    tool = RefactoringTool()
    refactored_code = tool.refactor_code(original_code)

    diff_text = tool.diff(original_code, refactored_code)
    if diff_text:
        print(diff_text)
    else:
        print("No changes made by refactoring tool.")
