#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Run Python static analysis and linting
echo "Running Python static analysis and linting..."
# Check code style with flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Run mypy for static type checking
mypy .

# Run isort to check import sorting
isort --check-only --diff .

# Run black for code formatting check
black --check .

# Run JavaScript/TypeScript linting
echo "Running JavaScript/TypeScript linting..."
# Use ESLint to lint all JS/TS files
# Assuming eslint is configured in the project
eslint "**/*.{js,jsx,ts,tsx}"

# Run Prettier check for code formatting
prettier --check "**/*.{js,jsx,ts,tsx,json,css,md}"

# Run TypeScript type checks if applicable
if [ -f tsconfig.json ]; then
  echo "Running TypeScript type checks..."
  tsc --noEmit
fi

echo "Code quality checks completed successfully."