# miscutils

Utilities for working with python projects.

## Usage

### logging_config

Default configuration for structlog. 

Configure json logging at the INFO level:
```python
from miscutils.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.INFO, LogFormat.JSON)
```

Configure text logging at the DEBUG level:
```python
from miscutils.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.DEBUG, LogFormat.TEXT)
```

Configure text logging at the DEBUG level and filter out external loggers:
```python
from miscutils.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.DEBUG, LogFormat.TEXT, ["extern_logger_1"])
```

### Log timing information for a function

Decorator to add timing information to the logs:
```python
from miscutils.timer import timer

import structlog

@timer(structlog.get_logger(__name__))
def some_function():
    pass
```

### Create a namespace relative patch

Create namespace relative patches:
```python
import some_package.sub_package.another_package as under_test
from miscutils.testing import relative_patch_maker

patch = relative_patch_maker(under_test.__name__)

class TestStuff:
    #equivalent to @unittest.mock.patch("some_package.sub_package.another_package.something_to_patch")
    @patch("something_to_patch")
    def test_something(self, patched):
        under_test.something()
        patched.assert_called_once()

    #equivalent to @unittest.mock.patch("some_package.sub_package.another_package.something_else_to_patch")
    @patch("something_else_to_patch")
    def test_something(self, patched):
        under_test.something()
        patched.assert_called_once()
```

## Development Guide

This project uses [poetry](https://python-poetry.org/):

```
$ pip install poetry
$ cd to/project/root
$ poetry install
```

### Testing

Testing is done via pytest.

```
$ poetry run pytest
```