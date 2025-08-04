# Component Documentation

This document defines the structure, naming conventions, and guidelines for components in this repository. Components are self-contained modules that encapsulate specific functionality behind a clear, minimal interface. Following these guidelines ensures that our components are easy to understand, maintain, and test while hiding internal complexity behind "Deep Classes" as defined by John Ousterhout.

---

## 1. Component Structure

Each component should be organized within its own subdirectory under the `src` directory, following the modern Python "src layout" pattern.

- **Directory Structure:**
  The component should reside in a subdirectory whose name matches the component. For example, for a component named **email_api**, the structure should be:

```
src/
    └── email_api/
        ├── src/
        │   └── email_api/
        │       ├── __init__.py
        │       ├── interfaces.py      # Protocol definitions
        │       ├── models.py          # Data models
        │       └── exceptions.py      # Exception hierarchy
        ├── tests/
        │   ├── __init__.py
        │   ├── test_interfaces.py
        │   ├── test_models.py
        │   └── test_exceptions.py
        ├── pyproject.toml            # Component configuration
        └── README.md                 # Component documentation
```

- **Interface Files:**
Interface files should use `typing.Protocol` or `abc.ABC` for dependency injection patterns and be named clearly (e.g., `interfaces.py`).

- **Implementation Files:**
When implementations are created, they should be separate components that depend on the interface component.

---

## 2. Naming Conventions

- **Components:** Use lowercase letters with words separated by underscores.
*Example:* `email_api`, `gmail_impl`, `outlook_impl`

- **Python Modules:** Use lowercase letters with words separated by underscores.
*Example:* `interfaces.py`, `models.py`, `exceptions.py`

- **Classes:** Use PascalCase.
*Example:* `EmailClient`, `EmailAddress`, `EmailError`

- **Functions/Methods/Variables:** Use snake_case.
*Example:* `list_inbox_messages`, `get_email_content`, `has_content`

- **Constants:** Use UPPER_SNAKE_CASE.
*Example:* `DEFAULT_LIMIT`, `MAX_RETRIES`

---

## 3. Documentation Guidelines

- **Component-Level Documentation:**
Each component should have a comprehensive README.md file describing its purpose, usage, and examples.

- **Documentation Site:**
Use MkDocs for generating professional documentation sites from Markdown files. Configure `mkdocs.yml` for structured documentation with navigation, themes, and plugins.

- **Public Interface Documentation:**
All public protocols, classes, methods, and functions must be documented with docstrings. Documentation should include:
  - A brief description of what the method or class does
  - Descriptions of parameters with types
  - The return value with type
  - Any exceptions that may be raised
  - Usage examples where helpful

- **Design Intent:**
Document design decisions that hide internal complexity and promote modularity. This allows users of the component to interact with it through a simple, clear protocol without needing to know implementation details.

---

## 4. Protocol-Based Design

- **Protocols Over Inheritance:**
Use `typing.Protocol` or `abc.ABC` with abstract methods to define interfaces. Protocols enable structural typing and better dependency injection patterns, while ABCs provide explicit inheritance contracts.

- **Dependency Injection:**
Design components to accept dependencies through constructor injection or protocol parameters.

- **Async-First:**
Prefer async interfaces for I/O operations to support modern Python applications.

---

## 5. Quality Standards

- **Type Safety:**
All components must pass mypy strict mode checking with comprehensive type hints.

- **Code Quality:**
All components must pass ruff linting with maximum strictness (all rules enabled).

- **Testing:**
Components must achieve ≥85% test coverage with comprehensive unit tests.

- **Documentation:**
All public interfaces must be fully documented with examples. Use MkDocs for generating professional documentation sites.

---

## 6. Testing

- Each component must have corresponding unit tests
- Create a `tests` subdirectory within each component's directory (e.g., `src/email_api/tests/`)
- Test files should be named `test_<module>.py` and aim for comprehensive coverage
- Use pytest with async support (`pytest-asyncio`)
- Integration and End-to-End tests must be in the root test directory (`tests/`)
- Mock external dependencies using dependency injection patterns

---

## 7. Components in this Repository

### email_api

- **Purpose:** Defines protocol-based interfaces and data models for email client implementations
- **Interface:**
  - `EmailClient` protocol with async methods for email operations
  - `Email` and `EmailAddress` immutable data models
  - Comprehensive exception hierarchy
- **Design Principle:** "Deep Classes" - simple interface hiding complex email handling
- **Dependencies:** Zero external dependencies for maximum compatibility

---

## 8. Implementation Guidelines

### When Creating New Components:

1. **Start with the Interface:** Define the protocol first, focusing on the minimal API surface
2. **Hide Complexity:** Keep the public interface simple while handling complexity internally  
3. **Use Dependency Injection:** Accept dependencies through constructor parameters
4. **Follow Async Patterns:** Use async/await for I/O operations
5. **Ensure Type Safety:** Add comprehensive type hints and pass mypy strict mode
6. **Write Tests First:** Create comprehensive test coverage using mocks and dependency injection
7. **Document Thoroughly:** Provide clear documentation with usage examples

### Quality Checklist:

- [ ] Protocol-based interface design
- [ ] Comprehensive type hints (mypy strict mode)
- [ ] Full ruff compliance with all rules enabled  
- [ ] ≥85% test coverage
- [ ] Async context manager support where applicable
- [ ] Immutable data models using dataclasses
- [ ] Clear exception hierarchy
- [ ] Component-specific README with examples
- [ ] MkDocs configuration for documentation site generation
- [ ] Zero or minimal external dependencies

---

### Design Philosophy
- **"Deep Classes"**: Simple interfaces hiding substantial complexity
- **Protocol-Based**: Use `typing.Protocol` or `abc.ABC` for flexible contracts
- **Dependency Injection**: Enable testing and modularity through external dependency management
- **Async-First**: Modern Python patterns for I/O operations 