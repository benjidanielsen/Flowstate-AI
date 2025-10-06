from typing import Any, Dict

class FrontendAgent:
    """
    Specialized AI agent for frontend development with React and TypeScript expertise.
    Provides code generation, component scaffolding, and best practice suggestions.
    """

    def __init__(self):
        self.framework = "React"
        self.language = "TypeScript"
        self.expertise = ["React", "TypeScript", "Hooks", "Context API", "Redux", "Styled-components", "Testing with Jest & React Testing Library"]

    def generate_component(self, name: str, props: Dict[str, str], state: Dict[str, Any] = None, hooks: bool = True) -> str:
        """
        Generate a functional React component in TypeScript.

        Args:
            name: Component name
            props: Dictionary of prop names and their TypeScript types
            state: Optional dictionary of state variable names and initial values
            hooks: Whether to include React hooks for state management

        Returns:
            TypeScript React functional component as a string
        """
        props_interface = f"interface {name}Props {{\n"
        for prop_name, prop_type in props.items():
            props_interface += f"  {prop_name}: {prop_type};\n"
        props_interface += "}\n\n"

        state_code = ""
        if hooks and state:
            for state_var, init_value in state.items():
                init_val_str = repr(init_value) if not isinstance(init_value, str) else f'"{init_value}"'
                state_code += f"  const [{state_var}, set{state_var.capitalize()}] = React.useState<{type(init_value).__name__}>({init_val_str});\n"

        component_code = (
            f"import React from 'react';\n\n"
            f"{props_interface}"
            f"const {name}: React.FC<{name}Props> = ({{ {', '.join(props.keys())} }}) => {{\n"
            f"{state_code}"
            f"\n  return (\n    <div>\n      {/* TODO: Implement {name} component UI */}\n    </div>\n  );\n}};\n\nexport default {name};
"
        )

        return component_code

    def suggest_best_practices(self) -> str:
        """
        Return a string with best practices for React/TypeScript frontend development.
        """
        return (
            "- Use functional components and React hooks for state and lifecycle management.\n"
            "- Strictly type props and state using TypeScript interfaces and types.\n"
            "- Prefer composition over inheritance for component design.\n"
            "- Use Context API or state management libraries like Redux for global state.\n"
            "- Apply CSS-in-JS solutions like styled-components or emotion for styling.\n"
            "- Write unit and integration tests using Jest and React Testing Library.\n"
            "- Optimize performance with React.memo, useCallback, and useMemo where applicable.\n"
            "- Follow accessibility standards (a11y) and semantic HTML."
        )

# Example usage (would be removed or moved to tests in production):
# agent = FrontendAgent()
# print(agent.generate_component('MyButton', {'label': 'string', 'onClick': '() => void'}, {'count': 0}))
