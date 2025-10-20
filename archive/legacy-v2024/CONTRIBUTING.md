# Contributing to Flowstate-AI

We welcome contributions to the Flowstate-AI project! To ensure a smooth and collaborative development process, please follow these guidelines.

## Getting Started

1.  **Fork the Repository**: Start by forking the `benjidanielsen/Flowstate-AI` repository to your GitHub account.
2.  **Clone Your Fork**: Clone your forked repository to your local machine:
    ```bash
    git clone https://github.com/YOUR_USERNAME/Flowstate-AI.git
    cd Flowstate-AI
    ```
3.  **Set Upstream**: Add the original repository as an upstream remote:
    ```bash
    git remote add upstream https://github.com/benjidanielsen/Flowstate-AI.git
    ```
4.  **Create a Feature Branch**: Always work on a new branch for your features or bug fixes:
    ```bash
    git checkout -b feature/your-feature-name
    # or
    git checkout -b bugfix/issue-description
    ```

## Development Workflow

1.  **Make Your Changes**: Implement your feature or fix the bug. Ensure your code adheres to the [Coding Standards](#coding-standards).
2.  **Test Your Changes**: Run the relevant tests to ensure your changes work as expected and do not introduce regressions.
    ```bash
    # Run all tests
    npm test
    # Individual service tests
    npm run test:frontend
    npm run test:backend
    cd python-worker && python -m pytest
    # cd godmode-dashboard && python -m pytest # (if tests are implemented)
    ```
3.  **Lint Your Code**: Ensure your code follows the project's linting rules. Auto-fix issues where possible.
    ```bash
    npm run lint
    npm run lint:fix
    ```
4.  **Commit Your Changes**: Write clear and concise commit messages. Follow the Conventional Commits specification (e.g., `feat: add new pipeline stage`, `fix: correct API endpoint bug`).
    ```bash
    git commit -m "feat: Add new pipeline stage"
    ```
5.  **Push to Your Fork**: Push your branch to your forked repository:
    ```bash
    git push origin feature/your-feature-name
    ```
6.  **Create a Pull Request (PR)**: Open a pull request from your feature branch to the `main` branch of the `benjidanielsen/Flowstate-AI` repository. Provide a detailed description of your changes.

## Coding Standards

Refer to the `docs/CODING_STANDARDS.md` file for detailed coding standards for each language and framework used in Flowstate-AI.

## Documentation Guidelines

*   All new features or significant changes must be accompanied by updated documentation.
*   API endpoints should be documented using OpenAPI/Swagger specifications.
*   User-facing features should have corresponding updates in user guides.
*   Technical architecture changes should be reflected in `SYSTEM_ARCHITECTURE.md`.

## Code of Conduct

We expect all contributors to adhere to our Code of Conduct. Please be respectful and constructive in all interactions.

Thank you for contributing to Flowstate-AI!
