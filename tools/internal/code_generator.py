import os
from typing import Dict, Optional

class CodeGenerator:
    """
    AI-powered code generation with templates.

    This class allows generating code snippets or files based on provided templates and input parameters.
    """

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the CodeGenerator.

        Args:
            templates_dir (Optional[str]): Path to the directory containing code templates.
                If None, defaults to './tools/internal/templates'.
        """
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.templates_dir = templates_dir

    def list_templates(self) -> Dict[str, str]:
        """
        List all available templates with their content.

        Returns:
            Dict[str, str]: Mapping from template name to template content.
        """
        templates = {}
        if not os.path.isdir(self.templates_dir):
            return templates

        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.tpl'):
                path = os.path.join(self.templates_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    templates[filename] = f.read()
        return templates

    def generate_code(self, template_name: str, context: Dict[str, str]) -> str:
        """
        Generate code from a template with the provided context.

        Args:
            template_name (str): The filename of the template (e.g. 'python_class.tpl').
            context (Dict[str, str]): Dictionary of variables to replace in the template.

        Returns:
            str: Generated code with placeholders replaced by context values.

        Raises:
            FileNotFoundError: If the template does not exist.
            KeyError: If template placeholders are missing in context.
        """
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.isfile(template_path):
            raise FileNotFoundError(f"Template '{template_name}' not found in {self.templates_dir}")

        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        try:
            code = template.format(**context)
        except KeyError as e:
            missing_key = e.args[0]
            raise KeyError(f"Missing placeholder in context for key: {missing_key}") from e

        return code

    def save_generated_code(self, code: str, output_path: str) -> None:
        """
        Save the generated code to a file.

        Args:
            code (str): The generated code string.
            output_path (str): The path to save the generated code file.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)


# Example usage (to be removed or placed in tests):
# if __name__ == '__main__':
#     cg = CodeGenerator()
#     context = {"ClassName": "MyClass", "method_name": "do_something"}
#     code = cg.generate_code('python_class.tpl', context)
#     print(code)
