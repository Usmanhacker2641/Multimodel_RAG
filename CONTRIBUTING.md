# Contributing to Multimodel RAG

Thank you for your interest in contributing to Multimodel RAG! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Multimodel_RAG.git
   cd Multimodel_RAG
   ```
3. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment:
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

3. Run tests:
   ```bash
   python -m unittest discover tests/
   ```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Add integration tests for complex features

## Submitting Changes

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request on GitHub

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Update documentation if needed

## Areas for Contribution

- Add support for more LLM providers (Anthropic, Cohere, etc.)
- Implement additional aggregation strategies
- Add support for more document formats
- Improve error handling and logging
- Add more comprehensive tests
- Improve documentation and examples

## Questions?

Feel free to open an issue for any questions or concerns.

Thank you for contributing!
