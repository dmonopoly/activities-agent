# Python Import Structure: Best Practices

## Problem: sys.path Manipulation

The original code used `sys.path` manipulation to make imports work:

```python
# ❌ Bad practice
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.tools.scraper import scrape_activities
```

### Why This Is Bad

1. **Fragile**: Only works when run from specific directories
2. **Hidden dependencies**: Not obvious that imports depend on path manipulation
3. **Not standard**: Most Python projects don't do this
4. **Hard to debug**: Import errors are confusing when paths are modified
5. **Testing issues**: Tests need the same path manipulation

## Solution: Install Package in Development Mode

The proper Python way is to install the package in development mode using `setup.py`:

```python
# ✅ Good practice
# After running: pip install -e .
from agents.tools.scraper import scrape_activities
```

### How It Works

1. **setup.py** defines the package structure
2. **pip install -e .** installs the package in "editable" mode
3. Python can now find `agents` as a proper package
4. No path manipulation needed

### Benefits

- ✅ **Standard practice**: This is how Python packages work
- ✅ **Works from anywhere**: Imports work regardless of working directory
- ✅ **Clear dependencies**: setup.py explicitly defines the package
- ✅ **IDE support**: IDEs understand the package structure
- ✅ **Testing**: Tests work without path hacks
- ✅ **Deployment**: Same structure works in production

## Setup Instructions

After creating the virtual environment and installing requirements:

```bash
cd backend
pip install -e .
```

This installs the package in "editable" mode, meaning:
- Changes to source code are immediately available
- No need to reinstall after code changes
- Package is properly registered with Python

## What Changed

### Before
- `sys.path` manipulation in multiple files
- Fallback import logic with `importlib.util`
- Fragile imports that break when run from different directories

### After
- Clean imports: `from agents.tools.scraper import ...`
- Single `setup.py` file defines package structure
- Works consistently from any directory
- Standard Python package structure

## Alternative Approaches (Not Used Here)

### 1. Relative Imports
```python
# Only works within a package
from .tools.scraper import scrape_activities
```
**Why not**: Can't use from top-level scripts like `main.py`

### 2. PYTHONPATH Environment Variable
```bash
export PYTHONPATH=/path/to/backend:$PYTHONPATH
```
**Why not**: Requires manual setup, not portable

### 3. Running from Specific Directory
```bash
# Only works if you always run from backend/
python main.py
```
**Why not**: Fragile, breaks in different contexts

## Conclusion

Using `pip install -e .` is the **standard, recommended approach** for Python projects. It makes the codebase more maintainable, easier to understand, and follows Python best practices.

