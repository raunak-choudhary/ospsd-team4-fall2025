Contributing Guide
==================

This document provides a comprehensive technical guide for contributors to the base **mail client repository**. It outlines the architectural principles, repository structure, development practices, testing strategies, and continuous integration policies that govern this project.

The intent of this guide is to ensure consistency, maintainability, and adherence to software engineering best practices for all future contributions.

1\. Architecture Overview
-------------------------

### 1.1 Architectural Design

The repository follows a **component-based architecture** organized into a uv workspace. It demonstrates **separation of concerns**, **dependency injection**, and **interface-driven development**, which allows independent development and testing of components.

At a high level, the system is composed of the following layers:

*   **Interface Layer (email\_api)**: Defines abstract contracts for mail operations.
    
*   **Implementation Layer (gmail\_impl)**: Provides Gmail-specific implementations.
    
*   **Application Layer (main.py)**: Demonstrates integration through dependency injection.
    
*   **Testing Layer (tests/)**: Includes unit, integration, and end-to-end tests.
    

The architectural goal is to ensure that the interface layer remains stable and implementation-independent, enabling alternative mail clients (e.g., Outlook or IMAP) to be introduced with minimal modification.

### 1.2 Components Overview

#### (a) email\_api

This component defines the **interface abstraction** for the mail client. It provides the following core elements:

*   **Client**: An abstract base class representing a mail client with defined methods such as get\_messages, get\_message, delete\_message, and mark\_as\_read.
    
*   **Email and EmailAddress**: Data abstractions representing email metadata, sender, and recipient fields.
    
*   **Factory Functions**: Functions such as get\_client() are declared but unimplemented, to be overridden by concrete implementations through dependency injection.
    

#### (b) gmail\_impl

This component implements the abstractions defined in email\_api. It includes:

*   **GmailClient**: A concrete implementation that interacts with the Gmail API.
    
*   **Dependency Injection Setup**: The \_\_init\_\_.py file registers the implementation by assigning the concrete factory (get\_client\_impl) to the abstract factory in email\_api.
    
*   **Authentication Management**: Implements OAuth2-based authentication and token refresh logic.
    

#### (c) tests/

This component verifies that individual modules and interactions perform as expected. It includes:

*   **Integration Tests** (tests/integration): Validate component interoperability.
    
*   **End-to-End Tests** (tests/e2e): Validate the complete workflow.
    

### 1.3 Interface Design Principles

The system is designed using **deep interfaces**, following John Ousterhout’s “A Philosophy of Software Design.” Each interface hides substantial complexity while providing a minimal, stable surface to clients.

Key principles:

*   **Explicit Contracts**: Interfaces explicitly define required behaviors via abstract methods.
    
*   **Encapsulation**: The implementation details of message parsing and API interaction are fully hidden behind the Client abstraction.
    
*   **Minimal Dependencies**: Interfaces depend only on Python’s standard library and typing modules.
    
*   **Extensibility**: New clients (e.g., IMAP) can be added by implementing the same contract and registering through dependency injection.
    

### 1.4 Implementation Details

The implementation uses Python’s abc module for defining abstract base classes (ABCs). Each abstract method is decorated with @abstractmethod to enforce implementation in subclasses.

**Key Python Features Used:**

*   abc.ABC and @abstractmethod to define mandatory interfaces.
    
*   @property decorators for interface fields like id, subject, and body.
    
*   Type hints and Iterator for static validation and code readability.
    
*   NotImplementedError placeholders in unimplemented factories to ensure explicit overrides.
    

**Factory and Dependency Injection Flow:**

1.  email\_api.get\_client() raises NotImplementedError initially.
    
2.  gmail\_impl.get\_client\_impl() defines the actual instantiation.
    
3.  On import, gmail\_impl.\_\_init\_\_.py executes email\_api.get\_client = get\_client\_impl.
    
4.  Application code calls email\_api.get\_client() without depending on implementation details.
    

## 1.5 Extra Credit: ABC vs. Protocol

| **Aspect** | **Abstract Base Class (ABC)** | **Protocol (typing module)** |
|---|---|---|
| **Definition** | Requires explicit inheritance | Uses structural subtyping |
| **Validation** | Enforced at runtime | Enforced at type-checking time |
| **Use Case** | Enforces explicit contract fulfillment | Enables flexible duck typing |
| **Example** | `class GmailClient(Client)` | `class GmailClient: def get_messages(self)` |
| **Benefit** | Clear contract and runtime safety | Flexibility and compatibility with existing classes |

### Project Choice
This project adopts **ABCs** due to their explicitness, runtime validation, and suitability for educational clarity.  
ABCs ensure incomplete implementations fail immediately, improving maintainability and traceability.


### 1.6 Dependency Injection

Dependency injection (DI) decouples interface and implementation. In this repository, DI is achieved through runtime replacement of factory functions.


### Injection Point Example

```python
# gmail_impl/__init__.py
import email_api
from gmail_impl.gmail_client import get_client_impl

def register() -> None:
    email_api.get_client = get_client_impl  # Injection point
```
**Benefits of This Pattern:**

*   Enables **runtime substitution** of implementations.
    
*   Facilitates **mocking** during testing.
    
*   Promotes **loose coupling** and **extensibility**.
    
*   Ensures **single responsibility** by isolating creation logic.
    

2\. Repository Structure
------------------------

```bash
ospd-ta-task/
│
├── src/                            # Interface component
│   │
│   ├── email_api/                  # Interface component
│   │   ├── src/email_api/          
│   │   │   ├── __init__.py         # Package initialization
│   │   │   ├── client.py           # Client, Email, EmailAddress
│   │   ├── tests/                  # Unit tests for API
│   │   └── pyproject.toml
│   │
│   └── gmail_impl/                 # Gmail implementation
│       ├── src/gmail_impl/
│       │   ├── __init__.py         # Registers dependency injection
│       │   ├── gmail_client.py     # GmailClient implementation
│       ├── tests/                  # Unit tests for implementation
│       └── pyproject.toml
│
├── tests/                          # Integration and E2E
│   ├── integration/                # Real Gmail API interaction tests
│   └── e2e/                        # End-to-end execution tests
│
├── main.py                         # Demonstration application
└── pyproject.toml                  # Root workspace configuration
```


*   src/: Source code of all components.
    
*   tests/: Centralized integration and e2e test suite.
    
*   pyproject.toml: Defines workspace and dependency configuration.
    

Each component functions as a self-contained package, promoting modularity and reusability.

### 2.1 Configuration Files

**Root pyproject.toml**

*   Defines workspace members (email\_api, gmail\_impl).
    
*   Configures shared tools such as Ruff, MyPy, and pytest.
    
*   Contains global dependency and test coverage settings.
    

**Component-Level pyproject.toml**

*   Defines component metadata and dependencies.
    
*   Specifies the internal dependency source via \[tool.uv.sources\].
    
*   May override root-level tool settings for specialized behavior.
    

### 2.2 Package and Import Guidelines

*   **Absolute imports** are mandatory (from email\_api import Client).
    
*   **Relative imports** (from . import X) are disallowed to maintain clarity.
    
*   Each module must contain explicit \_\_all\_\_ exports for controlled exposure.
    
*   \_\_init\_\_.py files should remain slim — containing imports and DI logic only.
    
*   Test directories include empty \_\_init\_\_.py files for pytest discovery only.
    

3\. Testing Strategy
--------------------

### 3.1 Testing Philosophy

All contributors must uphold the principle of _building quality in_. Testing is part of the development process, not an afterthought.

The repository adheres to the **Test Pyramid** pattern:

*   **Unit Tests** – Verify isolated functionality.
    
*   **Integration Tests** – Validate component interaction.
    
*   **End-to-End Tests** – Confirm system-level workflows.
    

The **FIRST** principles are followed:Fast • Isolated • Repeatable • Self-verifying • Timely.


### 3.2 Test Organization

| **Level**     | **Directory**         | **Purpose**                              |
|----------------|-----------------------|-------------------------------------------|
| Unit           | `src/*/tests`         | Component-level behavior                  |
| Integration    | `tests/integration`   | Verify component interoperability         |
| E2E            | `tests/e2e`           | Validate complete system functionality    |


All tests follow the **Arrange-Act-Assert (AAA)** pattern and must avoid shared state.

### 3.3 Code Coverage

*   **Tool:** pytest-cov
    
*   **Threshold:** 85% minimum (configured in pyproject.toml)
    
*   uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=85
    
*   **Reports:**
    
    *   term-missing for CLI summary
        
    *   htmlcov/ for detailed coverage visualization
        
    *   coverage.xml for CI integration
        

Lines intentionally untestable (e.g., raise NotImplementedError) are excluded with # pragma: no cover.

4\. Development Tools
---------------------

### 4.1 Workspace Management

This project uses **uv**, a fast Python package manager supporting multi-component workspaces.

**Essential Commands:**

*   Setup environment: uv sync --all-packages --extra dev
    
*   Run tests: uv run pytest
    
*   Lint: uv run ruff check .
    
*   Type check: uv run mypy src tests
    

Root pyproject.toml governs workspace-wide dependencies, while each component defines local metadata and runtime packages.

### 4.2 Static Analysis and Code Formatting

**Ruff**

*   Linting and auto-formatting combined.
    
*   Run lint: uv run ruff check .
    
*   Auto-fix issues: uv run ruff check . --fix
    

**MyPy**

*   Performs strict type checking.
    
*   Command: uv run mypy src tests
    

Configuration resides in the root pyproject.toml for uniform enforcement.

### 4.3 Documentation Generation

**MkDocs with Material Theme** is used for static site generation.

*   Serve locally: uv run mkdocs serve
    
*   Build: uv run mkdocs build
    

Documentation includes API references auto-generated via mkdocstrings.

5\. Continuous Integration (CI)
-------------------------------

The repository uses **CircleCI** for automated testing, linting, and coverage validation.

**Pipeline Overview:**

1.  **Build:** Install dependencies and cache environment.
    
2.  **Lint:** Validate code style and static analysis.
    
3.  **Unit Tests:** Run fast, isolated tests.
    
4.  **Integration Tests:** Execute controlled Gmail API tests.
    
5.  **Coverage:** Generate coverage reports.
    
6.  **Summary:** Aggregate and publish results.
    

**Triggers:**

*   Every commit and pull request.
    
*   Full integration tests run only on protected branches (main, develop).
    

Environment variables (e.g., GMAIL\_CLIENT\_ID, GMAIL\_CLIENT\_SECRET) are securely stored within CircleCI contexts.

6\. Contributor Workflow
------------------------

**1\. Clone and Setup:**

```bash
git clone <repo-url>
cd ospd-ta-task
uv sync --all-packages --extra dev
```

**2\. Run Tests and Linting:**

```bash
uv run ruff check .
uv run mypy src tests
uv run pytest
```

**3\. Add or Modify Code: Follow interface and DI patterns; update relevant documentation.**

**4\. Commit and Push: Commit changes with descriptive messages and open a Pull Request.**

**5\. CI Validation: Ensure CI passes before requesting review.**

7\. Summary
-----------

This guide defines the architectural, procedural, and technical standards for contributions.By adhering to these guidelines, contributors ensure consistency, maintain quality, and uphold the principles of software engineering excellence established in the base repository.


