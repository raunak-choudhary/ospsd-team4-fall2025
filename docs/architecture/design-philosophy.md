# Design Philosophy

## Core Principles

This project follows strict design principles not because they apply to every situation, but to teach recognition of what works well and how to identify "red flags" in software design.

## Deep Classes

This project embraces John Ousterhout's concept of **Deep Classes** from [A Philosophy of Software Design](https://web.stanford.edu/~ouster/cgi-bin/book.php):

```
┌─────────────────────────┐
│  Small, Simple Interface│  ← Low Cost (easy to understand)
├─────────────────────────┤
│                         │
│   Substantial           │  ← High Benefit (lots of functionality)
│   Functionality         │
│                         │
└─────────────────────────┘
```

**Key Idea**: The smaller the interface surface area, the better. A good interface gives you a simple way to think about something that might be really complicated underneath.

### What Makes a Good Abstraction?

- **Smallest cost**: Minimal complexity in the interface
- **Greatest benefit**: Maximum functionality provided
- **Clear contract**: Interface is a promise of behavior

This applies to:
- Classes and methods
- Modules and packages
- Components and subsystems
- All interfaces in your system

## Interface vs Implementation: The Contract Model

Think of your interface like a **contract between two parties**:

> "If you call this method with these parameters, I promise to return this type of data and perform this behavior."

The implementation is how you actually fulfill that promise.

### Why Separation Matters

```python
# Interface (Contract)
class Client(ABC):
    @abstractmethod
    def get_messages(self, limit: int | None = None) -> Iterator[Email]:
        """Return an iterator of messages from inbox."""
        
# Implementation (Promise Fulfillment)
class GmailClient(Client):
    def get_messages(self, limit: int | None = None) -> Iterator[Email]:
        # Gmail-specific implementation details
```

**Benefits**:
1. **Abstraction**: Users only need to understand the interface, not Gmail API details
2. **Flexibility**: Switch implementations (Gmail → Outlook) without breaking code
3. **Testability**: Mock interfaces easily in tests
4. **Parallelization**: Different team members work on interfaces and implementations simultaneously

## How Components Connect

Components interact through **Interfaces**. An interface is everything someone needs to have in their head to use your component:

- Method signatures
- Expected behavior
- Side effects
- Dependencies

**The cost goes up** with complexity. The more complex your interface, the more effort required to use your component.


## Strict Standards

This project enforces:
- All ruff checks enabled
- Mypy strict mode
- 80%+ test coverage
- Dependency injection
- Component-based architecture

