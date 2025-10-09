# Flowstate-AI Coding Standards

This document outlines the coding standards for the Flowstate-AI project. Adhering to these standards ensures code consistency, readability, and maintainability across the entire codebase.

## General Principles

*   **Readability**: Code should be easy to read and understand by other developers.
*   **Consistency**: Follow existing patterns and styles within the codebase.
*   **Maintainability**: Write code that is easy to modify and extend.
*   **Performance**: Optimize for performance where critical, but prioritize readability and maintainability first.
*   **Security**: Write secure code and follow best practices to prevent vulnerabilities.

## Python (Backend AI Worker, Godmode Dashboard, Evolution Framework)

*   **Formatting**: Adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code layout. Use a linter like `flake8` or `pylint` and a formatter like `Black`.
*   **Naming Conventions**: 
    *   `snake_case` for variables, functions, and module names.
    *   `CamelCase` for class names.
    *   `UPPER_SNAKE_CASE` for constants.
*   **Docstrings**: All modules, classes, and functions should have comprehensive docstrings following the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#pyguide-python-language-rules).
*   **Type Hinting**: Use [type hints](https://docs.python.org/3/library/typing.html) for all function arguments and return values.
*   **Imports**: Organize imports into three groups:
    1.  Standard library imports
    2.  Third-party imports
    3.  Local application/library imports
    Each group should be sorted alphabetically and separated by a blank line.
*   **Error Handling**: Use `try-except` blocks for handling expected errors. Avoid bare `except` clauses.

## JavaScript/TypeScript (Frontend, Backend API Service)

*   **Formatting**: Adhere to a consistent style guide, preferably enforced by `ESLint` and formatted by `Prettier`. The project uses `Airbnb JavaScript Style Guide` as a base.
*   **Naming Conventions**: 
    *   `camelCase` for variables, functions, and methods.
    *   `PascalCase` for class names, React components, and TypeScript interfaces/types.
    *   `UPPER_SNAKE_CASE` for constants.
*   **Comments**: Use JSDoc-style comments for functions, classes, and complex logic.
*   **TypeScript**: Utilize TypeScript for type safety in both frontend and backend. Define clear interfaces and types.
*   **Asynchronous Code**: Use `async/await` for handling asynchronous operations. Avoid callback hell.
*   **Error Handling**: Implement robust error handling using `try-catch` blocks for asynchronous operations and proper error propagation.

## HTML/CSS (Frontend, Godmode Dashboard Templates)

*   **HTML Structure**: Use semantic HTML5 elements. Ensure proper indentation and closing tags.
*   **CSS Styling**: 
    *   Use `Tailwind CSS` for utility-first styling in the frontend.
    *   For custom CSS, use `BEM (Block Element Modifier)` methodology or a similar approach for class naming.
    *   Organize CSS properties consistently (e.g., layout, box model, typography, color).
*   **Responsiveness**: Design with a mobile-first approach and ensure responsiveness across various screen sizes.

## Database (SQL - SQLite, PostgreSQL)

*   **Naming Conventions**: 
    *   `snake_case` for table and column names.
    *   Plural table names (e.g., `customers`, `interactions`).
*   **Schema Design**: Normalize tables to reduce redundancy. Use appropriate data types for columns.
*   **Migrations**: All schema changes must be managed through database migration scripts. Ensure migrations are reversible where possible.
*   **Indexing**: Create indexes on frequently queried columns to improve performance.

## Git Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Examples:**
*   `feat: add new pipeline stage`
*   `fix(api): correct customer update endpoint bug`
*   `docs: update contributing guidelines`
*   `refactor(frontend): improve pipeline visualization component`

## Code Review

All code contributions must undergo a code review process. Reviewers will check for:

*   Adherence to coding standards.
*   Correctness and functionality.
*   Readability and maintainability.
*   Test coverage.
*   Security implications.

By following these guidelines, we can maintain a high-quality codebase and foster a productive development environment for Flowstate-AI.
