# Python Import Best Practices

## Problem: Redundant sys.path Manipulation

The original code used `sys.path` manipulation, but it was **redundant**:

```python
# ❌ Redundant - Python already adds current directory to sys.path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
from agents.orchestrator import AgentOrchestrator
```

## Why This Was Redundant

When you run `python main.py` from the `backend/` directory:
1. Python automatically adds the current directory (`backend/`) to `sys.path`
2. This makes `agents`, `api`, etc. importable as top-level packages
3. The `sys.path.insert()` was doing the same thing Python already does

## Why sys.path Manipulation Is Generally Not Good Practice

1. **Redundant**: Python already handles this when running from the package directory
2. **Uncommon in Python repos**: Most projects rely on Python's automatic behavior
3. **Fragile**: If run from a different directory, it might not work as expected
4. **Hard to debug**: Makes import errors confusing
5. **Not standard**: Python has better ways to handle this

## Solutions

### ✅ Solution 1: Relative Imports (What We Use)

Use relative imports within the package:

```python
# In api/routes.py
from ..agents.orchestrator import AgentOrchestrator
from ..agents.tools.preferences import get_user_preferences

# In agents/orchestrator.py
from .tools.scraper import scrape_activities
from .tools.sheets import save_to_sheets
```

**Pros:**
- Standard Python practice
- Works regardless of working directory
- Clear package structure
- No path manipulation needed

**Cons:**
- Must run as a module (e.g., `python -m backend.main`)
- Or ensure backend directory is in PYTHONPATH

### ✅ Solution 2: Install Package in Editable Mode

Create `setup.py` or `pyproject.toml` and install:

```bash
pip install -e .
```

Then use absolute imports:
```python
from agents.orchestrator import AgentOrchestrator
```

**Pros:**
- Clean absolute imports
- Works from any directory
- Standard for Python packages

**Cons:**
- Requires setup file
- Extra installation step

### ✅ Solution 3: Set PYTHONPATH

```bash
export PYTHONPATH=/path/to/backend:$PYTHONPATH
python main.py
```

**Pros:**
- Simple
- No code changes needed

**Cons:**
- Environment-specific
- Easy to forget

## Why Our Code Works Now

1. **main.py runs from backend directory**: When you run `python main.py` from `backend/`, Python adds the current directory to `sys.path`
2. **Relative imports work**: Since `main.py` imports `api.routes`, and `routes.py` uses relative imports `from ..agents`, Python resolves them correctly
3. **Package structure**: All `__init__.py` files make directories proper packages

## When sys.path Manipulation Is Acceptable

1. **Test files**: Tests are often run from different directories, so path manipulation is more acceptable
2. **Scripts**: Standalone scripts that need to import from parent directories
3. **Legacy code**: When refactoring isn't feasible

## Current Implementation

- ✅ **api/routes.py**: Uses absolute imports (works because `backend/` is in `sys.path` when running `main.py`)
- ✅ **agents/orchestrator.py**: Uses absolute imports (same reason)
- ✅ **agents/tools/*.py**: No imports from backend package (only external libs)
- ⚠️ **tests/test_orchestrator.py**: Uses `sys.path` (acceptable for tests run from different directories)

## Running the Application

The application works because:

1. **main.py is in backend/**: When you run `python main.py`, Python's current directory is `backend/`
2. **Python adds current dir to sys.path**: This makes `api` and `agents` importable
3. **Relative imports resolve correctly**: `from ..agents` works because we're in a package

If you need to run from a different directory:

```bash
# Option 1: Set PYTHONPATH
PYTHONPATH=/path/to/backend python backend/main.py

# Option 2: Run as module (from project root)
python -m backend.main

# Option 3: Install in editable mode
cd backend
pip install -e .
python main.py  # Works from anywhere
```

## Summary

- ✅ Removed **redundant** `sys.path` manipulation from production code
- ✅ Using absolute imports (work because Python adds `backend/` to `sys.path` when running `main.py`)
- ✅ Code is cleaner - no unnecessary path manipulation
- ⚠️ Tests still use `sys.path` (acceptable for test files that may run from different directories)

## Key Insight

The `sys.path` manipulation was **redundant** because:
- When you run `python main.py` from `backend/`, Python automatically adds `backend/` to `sys.path`
- This makes `agents`, `api`, etc. importable as top-level packages
- The explicit `sys.path.insert()` was doing what Python already does automatically

**Best practice**: Trust Python's automatic behavior and only add `sys.path` manipulation when absolutely necessary (like in test files that run from different directories).

