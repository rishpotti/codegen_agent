import pytest
from your_module import add, subtract, multiply, divide # Assuming the functions are in 'your_module.py'

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(-1, -1) == -2
    assert add(0, 0) == 0
    assert add(2.5, 3.5) == 6.0
    assert add(100, 0) == 100

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2
    assert subtract(-1, 1) == -2
    assert subtract(-1, -1) == 0
    assert subtract(0, 0) == 0
    assert subtract(5.5, 2.5) == 3.0
    assert subtract(100, 0) == 100
    assert subtract(0, 100) == -100

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-1, 5) == -5
    assert multiply(-1, -5) == 5
    assert multiply(0, 5) == 0
    assert multiply(5, 0) == 0
    assert multiply(2.5, 2) == 5.0
    assert multiply(10, 0.5) == 5.0

def test_divide():
    assert divide(6, 3) == 2.0
    assert divide(5, 2) == 2.5
    assert divide(-10, 2) == -5.0
    assert divide(-10, -2) == 5.0
    assert divide(0, 5) == 0.0
    assert divide(5, 0) == "Error! Division by zero."
    assert divide(7.5, 2.5) == 3.0
