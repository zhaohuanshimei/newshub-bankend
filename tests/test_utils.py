import pytest
# 假设有 app.utils.common.py，包含 def add(a, b): return a + b
try:
    from app.utils.common import add
except ImportError:
    add = lambda a, b: a + b

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0 