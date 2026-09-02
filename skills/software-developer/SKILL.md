# Software Developer Skill

## Overview

This skill provides expert guidance on code development, maintainability, readability, and best practices. It focuses on clean, testable code that follows SOLID principles and industry standards.

---

## Core Principles

### 1. Intention-Revealing Names 🏷️

Variables, functions, and classes should tell you why they exist, what they do, and how they are used.

**Good:**
```python
# ✅ Clear intent
result = calculate_total(items)
user_config = load_user_preferences(config_path)

# ❌ Vague
x = do_something(data)
t = get_stuff(path)
```

### 2. Functions Should Do One Thing 🎯

Functions should be small, focused, and represent a single level of abstraction.

**Bad:**
```python
def process_order(order):
    # Does too much!
    validate_order(order)
    calculate_tax(order)
    apply_discount(order)
    create_invoice(order)
    send_email(order)
    log_result(order)
    return order
```

**Good:**
```python
# ✅ Each function has a single responsibility
def validate_order(order: Order) -> bool: ...
def calculate_tax(order: Order) -> float: ...
def apply_discount(order: Order) -> Order: ...
def create_invoice(order: Order) -> Invoice: ...
```

### 3. Avoid Side Effects 🚫

Functions should either do something OR answer something, but not both (Command-Query Separation).

**Mixed responsibility:**
```python
# ❌ Both reads AND writes in one function
def get_or_create_user(name: str) -> User:
    user = find_user_by_name(name)  # Read
    if not user:
        user = create_user(name)     # Write
    return user
```

**Separated:**
```python
# ✅ Clear intent with separate functions
def find_user_by_name(name: str) -> Optional[User]: ...
def create_user(name: str) -> User: ...
```

### 4. Boy Scout Rule 🧑‍🎓

"Leave the campground cleaner than you found it." - Always improve code, even in small ways.

**Example:**
```python
# Found this method
def save(user):
    user.name = user.name.strip()  # Already exists
    user.email = user.email.lower() # Already exists
    user.save()                     # Core functionality
    print(f"Saved {user}")          # Dead code, unused
    
# Leave it cleaner than you found it
def save(user):
    user.save()
```

### 5. DRY Principle (Don't Repeat Yourself) 📝

Avoid duplication; consolidate logic to prevent maintenance issues.

**Bad:**
```python
def validate_email(email: str) -> bool:
    return email and "@" in email and "." in email

def validate_phone(phone: str) -> bool:
    return phone and len(phone) > 10

# Duplicated pattern...
```

**Good:**
```python
class Validator:
    @staticmethod
    def validate(email: str) -> bool: ...
    @staticmethod  
    def validate_phone(phone: str) -> bool: ...
```

### 6. Keep it Simple (KISS) 🎈

Reduce complexity as much as possible.

**Bad:**
```python
def is_valid_order(order):
    if order.items is None or len(order.items) == 0:
        return False
    
    tax_rate = order.tax_rate if order.tax_rate else 0.0
    discount_amount = 0.0
    
    for item in order.items:
        if not item.quantity or item.quantity < 0:
            return False
        if not item.price or item.price <= 0:
            return False
            
    subtotal = sum(item.quantity * item.price for item in order.items)
    total = subtotal + (subtotal * tax_rate) - discount_amount
    
    if total <= 0:
        return False
        
    if len(order.shipping_address.street) < 5:
        return False
        
    # More checks...
    
    return True
```

**Good:**
```python
class OrderValidator:
    @staticmethod
    def validate_order(order: Order) -> ValidationError | None:
        if not order.items or not order.items[0]:
            return ValidationError("Order must have items")
        
        tax_rate = order.tax_rate or 0.0
        
        for item in order.items:
            if item.quantity <= 0:
                return ValidationError(f"Item {item.name} has invalid quantity")
            
        subtotal = sum(item.quantity * item.price for item in order.items)
        total = subtotal * (1 + tax_rate)
        
        if total <= 0:
            return ValidationError("Invalid order total")
        
        return None
```

### 7. Comments are Failures 💭

Code should be self-explanatory. Instead of writing comments, refactor the code to make it readable.

**Bad:**
```python
# Increment index by 1 to move to next element
index = index + 1
```

**Good:**
```python
index += 1  # Clear enough!
```

### 8. SOLID Principles 🔩

#### Single Responsibility Principle (SRP)
A class should have one reason to change.

```python
# ❌ Too many responsibilities
class User:
    def create(self, data): ...  # Business logic
    def validate_email(data): ...  # Validation
    def persist_to_db(): ...      # Persistence
    
# ✅ Split them
class User: ...                  # Domain model
class UserRepository: ...        # Persistence
class UserValidator: ...         # Validation
```

#### Open/Closed Principle
Open for extension, closed for modification.

```python
# ✅ Use composition over inheritance
class PaymentProcessor:
    def process(self, amount): ...  # Base interface
    
class StripeProcessor(PaymentProcessor):
    def process(self, amount): ...  # Extension through subclassing
    
def register_processor(processor: PaymentProcessor): ...  # Dependency injection
```

#### Liskov Substitution Principle
Subtypes should be substitutable for base types.

```python
# ❌ Duck typing violations
class Rectangle:
    def set_width(self, w): ...
    
class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w  # Violates LSP!
        
# ✅ Use composition or explicit contracts instead
```

#### Interface Segregation Principle
Many specific interfaces are better than one general-purpose interface.

```python
# ❌ Too broad
class Worker:
    def work(): ...
    def eat(): ...
    def sleep(): ...
    
# ✅ Specific roles
class DevWorker(Worker):
    def code(): ...
    
class HRWorker(Worker):
    def interview(): ...
```

#### Dependency Inversion Principle
Depend on abstractions, not concretions.

```python
# ❌ Direct dependency
def process_order(order: Order) -> Invoice:
    order = calculate_taxes(order)  # Concrete dependency
    invoice = create_invoice(order)
    
# ✅ Depend on abstraction
from abc import ABC, abstractmethod
class TaxCalculator(ABC):
    @abstractmethod
    def calculate(order: Order) -> float: ...

def process_order(order: Order, calculator: TaxCalculator) -> Invoice:
    order = calculator.calculate(order)  # Abstraction
```

---

## Usage Examples

### Quick Code Review

**Before:**
```python
def save_user(user):
    user.name = user.name.strip()
    user.email = user.email.lower()
    db.save(user)
    print(f"Saved {user}")
    return user.id
```

**After:**
```python
class UserRepository:
    @staticmethod
    def save(user: User) -> User | None:
        user.name = user.name.strip()
        user.email = user.email.lower()
        db.save(user)
        return user.id
```

### Unit Testing

```python
from unittest.mock import patch, MagicMock

def test_calculate_discount():
    with patch('src.module.apply_promo_code') as mock_apply:
        mock_apply.return_value = 0.8
        
        result = apply_discount(100)
        
        assert result == 80
        mock_apply.assert_called_once()
```

### Error Handling

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ValidationError:
    """Implements the error as an object, not exception."""
    field: str
    message: str
    
    def __str__(self):
        return f"{self.field}: {self.message}"

def validate_name(name: str) -> Optional[ValidationError]:
    if len(name) < 2:
        return ValidationError("name", "Must be at least 2 characters")
    if len(name) > 100:
        return ValidationError("name", "Must be at most 100 characters")
    return None
```

---

## Best Practices Summary ✅

1. **Names**: Intention-revealing, consistent style
2. **Size**: Functions < 20 lines, classes < 200 lines
3. **Dependencies**: Abstract interfaces, inject concrete implementations
4. **Testing**: Unit tests for core logic, integration tests for boundaries
5. **Documentation**: Docstrings for public APIs, READMEs for projects
6. **Refactoring**: Extract methods when function > 10 lines
7. **Comments**: Explain WHY, not WHAT (code should explain WHAT)

---

## Integration with Git Operations Skill

This skill complements `git-operations` by:
- ✅ Providing code review checklist items
- ✅ Architectural guidance for feature implementations
- ✅ Testing standards and conventions
- ✅ Refactoring suggestions during development

The `git-operations` skill handles:
- ✅ Commit message quality and consistency
- ✅ Branch strategy decisions (when to rebase vs merge)
- ✅ Repository organization and hygiene
- ✅ PR process optimization

Together, they provide complete development workflow coverage!
