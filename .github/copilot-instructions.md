# TensorTrade AI Coding Agent Guide

## Architecture Overview

TensorTrade is a composable RL trading framework built on a **component-based dependency injection pattern** using `TradingContext`:

- **Component Registry Pattern**: All major components inherit from `Component` base class and use `registered_name` class attribute to register in the global registry (see [tensortrade/core/component.py](tensortrade/core/component.py), [tensortrade/core/registry.py](tensortrade/core/registry.py))
- **Context Injection**: Components are initialized within a `TradingContext` (Python context manager) that provides configuration via metaclass `InitContextMeta`
- **Major Component Types**: `actions`, `rewards`, `observer`, `informer`, `stopper`, `renderer` (defined in `MAJOR_COMPONENTS`)

### Core Modules

- **`tensortrade/core/`**: Base abstractions (`Component`, `TradingContext`, `Clock`, `Identifiable`, `TimeIndexed`)
- **`tensortrade/oms/`**: Order Management System - exchanges, wallets, orders, instruments, slippage models
- **`tensortrade/feed/`**: Streaming data pipeline using composable `Stream` objects with lazy evaluation and topological sorting
- **`tensortrade/env/`**: Gymnasium-compatible trading environments (`env/generic/` for base, `env/default/` for concrete implementations)
- **`tensortrade/agents/`**: RL agents (A2C, DQN) with parallel training support

## Component Registration Pattern

**Critical**: When creating new components, always set `registered_name`:

```python
from tensortrade.core import Component

class MyActionScheme(ActionScheme):  # ActionScheme inherits Component
    registered_name = "actions"  # Must match MAJOR_COMPONENTS for injection
    
    def __init__(self, some_param: str):
        super().__init__()
        # Access injected config via self.context
        custom_value = self.context.get('custom_key', default_value)
```

Components are instantiated inside a `TradingContext`:

```python
from tensortrade.core import TradingContext

config = {
    "actions": {"some_param": "value"},  # Matches registered_name
    "shared": {"global_key": "global_value"}  # Available to all components
}

with TradingContext(config):
    action_scheme = MyActionScheme("value")  # Config auto-injected via metaclass
```

See [tests/tensortrade/unit/base/test_component.py](tests/tensortrade/unit/base/test_component.py) for usage patterns.

## Data Feed System

Streams use **declarative lazy evaluation** with automatic topological sorting:

- Create streams using operators: `+`, `-`, `*`, `/`, comparison operators
- Streams auto-wire dependencies and execute in correct order when `DataFeed.run()` is called
- Example: `price_stream = Stream.source([100, 101, 102]).rename("price")`

See [tensortrade/feed/core/](tensortrade/feed/core/) and [tensortrade/feed/api/](tensortrade/feed/api/) for stream operations.

## Development Workflows

### Running Tests

```bash
make test                 # Run full test suite
make test-parallel        # Parallel test execution
pytest tests/             # Direct pytest
pytest --doctest-modules tensortrade/  # Run doctests
```

### Docker Workflows

```bash
make run-notebook         # Launch Jupyter on port 8888
make run-docs            # Build and serve docs on port 8000
make run-tests           # Run tests in Docker
make build-cpu           # Build CPU Docker image
```

### Documentation

- Built with Sphinx: `make docs-build` in `docs/` directory
- Docstrings must use **Markdown format** with sections: `Parameters`, `Returns`, `Raises`
- See existing docstrings in codebase for examples

## Code Conventions

### Style Requirements

- **PEP8 compliant** (not strict on line length, but keep reasonable)
- Use `autopep8` for automatic fixes: `autopep8 -i --select <errors> <file>`
- Abstract methods must be decorated with `@abstractmethod` from `abc`
- Type hints required for public APIs

### Testing Requirements

- Full unit test coverage required for new code
- Test file structure mirrors source: `tests/tensortrade/<module>/test_<file>.py`
- Use `pytest` with fixtures for component initialization
- Mock external dependencies (exchanges, RL frameworks)

### OMS (Order Management System) Integration

Action schemes that use the built-in OMS should inherit from `TensorTradeActionScheme`:

```python
from tensortrade.env.default.actions import TensorTradeActionScheme

class BSH(TensorTradeActionScheme):  # Buy-Sell-Hold example
    registered_name = "bsh"
    
    def get_orders(self, action: int, portfolio: 'Portfolio') -> List[Order]:
        # Return list of Order objects for broker execution
        pass
```

The parent class handles `portfolio`, `broker`, and `clock` synchronization automatically.

## Key Files Reference

- [tensortrade/core/component.py](tensortrade/core/component.py) - Component base class and metaclass injection
- [tensortrade/core/context.py](tensortrade/core/context.py) - TradingContext implementation
- [tensortrade/env/generic/components/](tensortrade/env/generic/components/) - Base component interfaces
- [tensortrade/env/default/](tensortrade/env/default/) - Default implementations (actions, rewards, observers)
- [examples/](examples/) - Jupyter notebooks with complete examples
- [setup.py](setup.py) - Dependencies and version requirements

## Dependencies

- **Python >= 3.11.9** (strict requirement)
- **Core**: `numpy`, `pandas`, `gymnasium` (replaces deprecated `gym`)
- **ML**: `tensorflow >= 2.7.0`
- **Visualization**: `matplotlib`, `plotly`, `ipywidgets`
- **Data**: `stochastic` for synthetic data generation

## Common Pitfalls

- **Never instantiate Components outside TradingContext** - config injection will fail
- **Clock synchronization**: Components that are `TimeIndexed` must share the same `Clock` instance
- **Stream reset**: Always call `feed.reset()` before starting new episode
- **Broker state**: The `Broker` maintains state - reset between episodes via `broker.reset()`
