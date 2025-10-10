# Mail Client as a Service (Team 4) — Extended Academic & Technical Report

---

## Abstract

This comprehensive report documents the full **design, development, and evaluation** of the **Mail Client as a Service** project undertaken by **Team 4** as part of the *Open Source Software Product Development (OSPSD) course, Fall 2025, NYU Tandon School of Engineering*.  
The primary aim was to transform a **library-based Gmail client** into a **service-oriented architecture (SOA)** using **FastAPI**, thereby enabling language-independent and network-based access to email functionality.

The project applies key software design principles such as **Abstraction**, **Dependency Inversion**, **Interface Segregation**, **Adapter Pattern**, and **Open/Closed Principle**. These theoretical principles were grounded through practical implementation and iterative testing across multiple environments.  

The new architecture maintains **interface compliance** with the base system while introducing distributed accessibility and containerized deployment capabilities.  
Through this transformation, the team demonstrates how foundational design patterns can guide the modernization of legacy components into modular, testable, and scalable services.

---

## 1. Introduction and Motivation

### 1.1 Background

Modern software systems increasingly rely on modular and distributed design to support scalability, integration, and maintainability. Monolithic systems, once prevalent, now limit flexibility and adaptability.  
In this context, transitioning from a **local Gmail client library** to a **microservice-based system** represents an educational and architectural milestone.  

The **Mail Client as a Service** project embodies this shift — evolving from a **local Python-bound library** to a **platform-agnostic service**.  

Key motivations included:

- 🌐 **Cross-language Interoperability:** Support applications beyond Python through HTTP.  
- 🔄 **Code Reusability:** Enable existing codebases to use the same interface without modification.  
- ⚙️ **Centralized Credential Management:** Simplify Gmail OAuth management.  
- 🧪 **Improved Testing Workflow:** Allow isolated and mock-based testing.  
- ☁️ **Deployment Readiness:** Facilitate containerization and scalable deployment.

### 1.2 Significance of Study

This work is pedagogically significant because it connects **theoretical principles** with **practical implementation**.  
It demonstrates that concepts such as **Dependency Inversion** and **Adapter Design Pattern** are not abstract ideas but living frameworks that guide software transformation.

By implementing the Gmail client as a **service**, the team successfully demonstrates:

- How *abstraction* fosters long-term maintainability.  
- How *adapter layers* ensure backward compatibility.  
- How *dependency injection* decouples infrastructure from logic.  

The project also emphasizes collaboration, CI/CD discipline, and open-source contribution ethics — key elements of professional engineering practice.

---

## 2. Problem Statement

### 2.1 Base Repository Limitations

The base repository provided a **library-only Gmail client** that directly accessed Google’s API. While functional, it exhibited multiple shortcomings:

| Category | Limitation | Consequence |
|-----------|-------------|-------------|
| **Architecture** | Tight coupling between logic and Gmail API | Poor maintainability |
| **Language Support** | Python-only | Excludes non-Python ecosystems |
| **Deployment** | Requires Gmail credentials locally | Security and scaling issues |
| **Testing** | Dependent on live Gmail accounts | Fragile, non-deterministic tests |
| **Integration** | Library must be installed everywhere | Repeated environment setup |

### 2.2 Need for Refactoring

To overcome these constraints, the system needed:

- ✅ Decoupling of client logic from Gmail-specific code.  
- ✅ Standardized interface (HTTP) for cross-environment integration.  
- ✅ Configurable dependency injection to support testability.  
- ✅ A REST-compliant API specification to ensure interoperability.  

Thus, this refactor was not merely a technical exercise but a **strategic redesign** guided by solid architectural reasoning.

---

## 3. Objectives

The specific goals of this project were as follows:

1. **Expose core Gmail operations** via RESTful APIs built using **FastAPI**.  
2. **Implement an Adapter Layer** that mirrors the `email_api.Client` interface.  
3. **Generate OpenAPI Clients** automatically for type safety and multi-language compatibility.  
4. **Preserve backward compatibility** — user code remains identical.  
5. **Enable robust testing**, including unit, integration, and end-to-end levels.  
6. **Introduce Dockerized Deployment** for consistent environments.  
7. **Ensure CI/CD Quality Gates** — enforced via `mypy`, `ruff`, and `pytest --cov`.  
8. **Document the design and results** comprehensively for educational replication.

---

## 4. Theoretical Framework

### 4.1 Core Software Principles Applied

| Principle | Description | Application in Project |
|------------|-------------|------------------------|
| **Abstraction** | Isolate Gmail logic behind a generic interface | `email_api.Client` defines contracts |
| **Dependency Inversion** | Depend on abstractions, not implementations | FastAPI injects concrete clients dynamically |
| **Adapter Pattern** | Bridge between legacy interface and service-based model | `ServiceEmailClient` wraps HTTP client |
| **Interface Segregation** | Provide fine-grained, cohesive contracts | Separate `Client` and `Message` ABCs |
| **Open/Closed Principle** | Extend functionality without altering base | Added services while keeping base repo intact |

### 4.2 Theoretical Importance

Each design principle bridges a known problem in software engineering:

- The **Adapter Pattern** ensures compatibility between old and new modules.  
- **Dependency Injection** transforms hard-coded dependencies into flexible interfaces.  
- **Abstraction and Encapsulation** reduce cognitive load and code fragility.  
- The **SOA paradigm** introduces scalability and modularity into legacy software.

This theoretical backbone aligns with engineering frameworks such as **SOLID**, **Clean Architecture**, and **Domain-Driven Design**.

---

## 5. System Architecture

### 5.1 Overview

The architecture is divided into **four major layers**, each with clearly defined responsibilities:

```
┌────────────────────────────────────────────────────────────┐
│                   Client Applications                       │
└─────────────┬───────────────────────────┬──────────────────┘
              │                           │
              │ (Direct Import)           │ (HTTP Access)
              │                           │
┌─────────────▼───────────────┐   ┌────────▼──────────────────┐
│   gmail_impl (Base)         │   │ mail_client_service       │
│   - GmailClient             │   │ - FastAPI REST API        │
│   - OAuth 2.0               │   │ - Adapter via HTTP        │
└────────────┬───────────────┘   └──────────┬────────────────┘
             │                              │
             ▼                              ▼
    ┌────────────────────────────────────────────────┐
    │               email_api (Interface)             │
    │        - Client ABC  |  - Message ABC           │
    └────────────────────────────────────────────────┘
```

### 5.2 Architectural Layers

1. **Interface Layer (email_api):**
   - Defines abstract classes (`Client`, `Message`).
   - Serves as the foundation of all implementations.
2. **Implementation Layer (gmail_impl):**
   - Provides direct Gmail integration.
   - Manages OAuth authentication and message operations.
3. **Service Layer (mail_client_service):**
   - Converts local methods into HTTP routes using FastAPI.
   - Returns standardized JSON responses.
4. **Adapter Layer (mail_client_adapter):**
   - Translates service calls to interface-compliant methods.
   - Ensures client code remains unmodified.

### 5.3 Architectural Benefits

- **Extensibility:** New mail providers can be integrated easily.  
- **Scalability:** FastAPI allows concurrent requests and container orchestration.  
- **Maintainability:** Separation of concerns reduces regression risk.  
- **Testing Flexibility:** Mock injection supports isolated verification.  

---

## 6. Component-Level Design

### 6.1 FastAPI Service

The **FastAPI Service** serves as the public-facing API layer.  
It transforms function calls into networked endpoints while enforcing validation through Pydantic models.

**Endpoints Summary:**

| Method | Path | Operation | HTTP Status | Description |
|--------|------|------------|--------------|--------------|
| `GET` | `/messages` | List all messages | 200 | Retrieves message summaries |
| `GET` | `/messages/{id}` | Fetch message by ID | 200 | Retrieves message content |
| `POST` | `/messages/{id}/mark-as-read` | Mark message as read | 200 | Updates read status |
| `DELETE` | `/messages/{id}` | Delete message | 200 | Removes message permanently |

**Key Features:**

- Stateless, REST-compliant endpoints.  
- Dependency injection via `Depends(get_email_client)`.  
- Automatic OpenAPI documentation at `/docs`.  
- Input validation handled by FastAPI’s request models.

### 6.2 Adapter: ServiceEmailClient

The adapter layer provides backward compatibility with the `email_api.Client` interface.

**Adapter Responsibilities:**

- Translate interface method calls into HTTP requests.  
- Handle responses, exceptions, and error translation.  
- Maintain consistent function signatures.

**Sample Code:**
```python
def list_messages(self, limit: int = 10):
    resp = list_messages_messages_get.sync(client=self._gen, limit=limit)
    return [self._map_summary(x) for x in resp]
```

The adapter thereby hides all network logic from the end-user, making the distributed nature of the system transparent.

### 6.3 OpenAPI Client

The **auto-generated OpenAPI client** bridges the service and adapter layers.  

**Benefits:**
- Provides **type-safe HTTP operations**.  
- Reduces boilerplate.  
- Ensures schema consistency.  
- Facilitates integration with other languages (C#, JavaScript, etc.).

**Generation Command:**
```bash
openapi-python-client generate   --path clients/specs/openapi.json   --output-path clients/python/mail_client_service_client
```

### 6.4 Docker Integration

Docker enables consistent runtime environments for both developers and users.

**Docker Highlights:**
- Based on Python 3.11-slim.  
- Uses `uv` package manager for reproducible installs.  
- Exposes port `8000` for API access.  
- Supports local and production builds.  

**Build and Run:**
```bash
docker build -t mail-client-service .
docker run -p 8000:8000 mail-client-service
```

---

## 7. Integration with Base Repository

Integration achieved through **dependency injection (DI)**:

```python
def get_client_impl(base_url: str = "http://localhost:8000") -> Client:
    return ServiceEmailClient(base_url)
```

**Key Advantages:**

- Preserves the original Gmail interface.  
- Simplifies testing by swapping implementations dynamically.  
- Allows co-existence of local and remote clients.

---

## 8. Testing Methodology

### 8.1 Levels of Testing

| Type | Description | Framework | Notes |
|------|--------------|------------|-------|
| **Unit Tests** | Validate adapter logic, service responses | `pytest`, `mock` | Run fast and isolated |
| **Integration Tests** | Test communication between layers | `respx`, `httpx` | Uses in-memory FastAPI |
| **E2E Tests** | Test real Gmail API interactions | OAuth setup | Requires credentials |

### 8.2 CI/CD Pipeline

The **CircleCI pipeline** enforces:  

1. ✅ Linting (`ruff`).  
2. ✅ Type checking (`mypy`).  
3. ✅ Unit + Integration testing (`pytest --cov`).  
4. ✅ Documentation build validation (`mkdocs`).  

### 8.3 Mocking Strategy

- Mock Gmail API for isolated tests.  
- Use dependency injection to swap real vs mock clients.  
- Store sample JSON responses for deterministic results.

---

## 9. Results and Analysis

### 9.1 Key Metrics

| Metric | Target | Achieved |
|--------|---------|-----------|
| **Coverage** | ≥90% | 93.6% |
| **Lint Score** | 0 errors | 0 errors |
| **Type Consistency** | 100% compliant | ✅ Passed |
| **Interface Parity** | Full compliance | ✅ Achieved |

### 9.2 Observations

- Mock testing dramatically reduced CI runtime.  
- Docker environment ensured uniform builds.  
- Auto-generated clients minimized manual schema drift.  
- Service latency remained within acceptable limits (~50–100ms overhead).

### 9.3 Comparative Analysis

| Aspect | Base Library | Service Version |
|---------|--------------|-----------------|
| **Portability** | Python-only | Cross-language |
| **Deployment** | Local | Containerized |
| **Testing** | Requires Gmail | Mock-enabled |
| **Extensibility** | Limited | High |
| **Security** | Decentralized | Centralized credentials |

---

## 10. Design Decisions and Tradeoffs

| Decision | Rationale | Advantage | Limitation |
|-----------|------------|------------|-------------|
| **Sync API** | Align with Gmail SDK | Simple integration | Limited concurrency |
| **Mock Fallback** | Offline testing | Reliable CI runs | Needs upkeep |
| **Vendored OpenAPI Client** | Determinism | Stable builds | Larger repo |
| **Single-stage Docker** | Simplicity | Quick builds | Bigger image size |
| **No Authentication Layer** | Out of scope | Easier grading | Not production-ready |

---

## 11. Future Work

1. **Add Authentication:** Integrate JWT and OAuth2 for secure access.  
2. **Async Implementation:** Support concurrency via `async def`.  
3. **Caching Layer:** Employ Redis or Memcached.  
4. **Observability Tools:** Add metrics with Prometheus.  
5. **API Versioning:** Introduce `/v1`, `/v2` with deprecation warnings.  
6. **GraphQL Endpoint:** Explore flexible queries for client apps.  

---

## 12. Conclusion

This project successfully extends the local Gmail client architecture into a **distributed, service-oriented system** that is modular, testable, and future-ready.  

### 12.1 Achievements Recap

- ✅ Achieved **full functional parity** with base Gmail client.  
- ✅ Demonstrated **FastAPI-based SOA design**.  
- ✅ Validated **interface compliance** through static and runtime checks.  
- ✅ Implemented **mock-driven CI pipeline**.  
- ✅ Enabled **containerized deployment**.  

### 12.2 Educational Impact

- Reinforced understanding of SOLID principles.  
- Illustrated practical value of software design patterns.  
- Demonstrated real-world scalability of theoretical constructs.  

### 12.3 Broader Implications

This project serves as a reusable blueprint for similar **API modernization efforts**, illustrating how legacy codebases can be safely evolved into distributed, service-based architectures while retaining interface integrity.

---

**End of Report**  
*Team 4 – OSPSD Fall 2025, NYU Tandon School of Engineering*
