import os
import ast
import json
from typing import List, Dict

import openai

class DocumentationAgent:
    """
    AI agent to automatically generate and maintain documentation
    for Python and JavaScript code files within a project.
    """

    def __init__(self, openai_api_key: str, project_root: str = '.'):
        openai.api_key = openai_api_key
        self.project_root = project_root

    def scan_code_files(self, extensions: List[str] = ['.py', '.js']) -> List[str]:
        """
        Recursively scan the project directory for code files with given extensions.
        """
        code_files = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    code_files.append(os.path.join(root, file))
        return code_files

    def read_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, file_path: str, content: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def extract_code_structure_python(self, code: str) -> Dict:
        """
        Extract basic structure from Python code using ast (functions, classes, docstrings).
        """
        tree = ast.parse(code)
        structure = {'functions': [], 'classes': []}

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                structure['functions'].append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node) or ''
                })
            elif isinstance(node, ast.ClassDef):
                structure['classes'].append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node) or '',
                    'methods': []
                })
                for class_node in node.body:
                    if isinstance(class_node, ast.FunctionDef):
                        structure['classes'][-1]['methods'].append({
                            'name': class_node.name,
                            'docstring': ast.get_docstring(class_node) or ''
                        })
        return structure

    def extract_code_structure_javascript(self, code: str) -> Dict:
        """
        Basic heuristic extraction of functions and classes from JavaScript code.
        Note: Without a JS parser, this is simplistic and regex-based.
        """
        import re
        structure = {'functions': [], 'classes': []}

        # Find function declarations
        func_pattern = re.compile(r'function\s+(\w+)\s*\(')
        for match in func_pattern.finditer(code):
            structure['functions'].append({
                'name': match.group(1),
                'docstring': ''  # Could be improved by extracting comments above
            })

        # Find class declarations
        class_pattern = re.compile(r'class\s+(\w+)')
        for match in class_pattern.finditer(code):
            structure['classes'].append({
                'name': match.group(1),
                'docstring': '',
                'methods': []  # Could be improved by parsing class body
            })

        return structure

    def generate_doc_for_code(self, filename: str, code: str, structure: Dict) -> str:
        """
        Use OpenAI API to generate or update documentation given code and extracted structure.
        """
        prompt = f"""
You are an AI assistant that generates clear, concise documentation for code files.

File name: {filename}

Code:
""" + code + """

Structure:
""" + json.dumps(structure, indent=2) + """

Generate a markdown documentation for this file including descriptions for the file, its classes, methods, and functions.
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You generate markdown documentation for code files."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content'].strip()

    def save_documentation(self, code_file_path: str, documentation: str):
        """
        Save the generated documentation alongside the code file as a markdown file.
        e.g. example.py => example.md
        """
        base, _ = os.path.splitext(code_file_path)
        doc_path = base + '.md'
        self.write_file(doc_path, documentation)

    def run(self):
        code_files = self.scan_code_files()

        for file_path in code_files:
            code = self.read_file(file_path)
            ext = os.path.splitext(file_path)[1]

            if ext == '.py':
                structure = self.extract_code_structure_python(code)
            elif ext == '.js':
                structure = self.extract_code_structure_javascript(code)
            else:
                continue  # Unsupported file type

            documentation = self.generate_doc_for_code(file_path, code, structure)
            self.save_documentation(file_path, documentation)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run Documentation Agent')
    parser.add_argument('--api_key', type=str, required=True, help='OpenAI API key')
    parser.add_argument('--project_root', type=str, default='.', help='Root directory of the project')

    args = parser.parse_args()

    agent = DocumentationAgent(openai_api_key=args.api_key, project_root=args.project_root)
    agent.run()
