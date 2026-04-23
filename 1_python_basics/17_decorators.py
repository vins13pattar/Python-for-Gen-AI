# ============================================================================
# DECORATORS IN PYTHON
# ============================================================================

"""
Decorators are a powerful feature in Python that allow you to modify or extend
the behavior of functions without permanently modifying them.
A decorator is a function that wraps another function to add extra behavior
before or after it runs.

Think of it like: "Before calling this function, do something extra."
"""

# ============================================================================
# 1. WHAT IS A DECORATOR (IN SIMPLE WORDS)?
# ============================================================================

"""
A decorator is a function that wraps another function to add extra behavior
before or after it runs.

Think of it like:
"Before calling this function, do something extra."
"""

# ============================================================================
# 2. FUNCTIONS ARE FIRST-CLASS CITIZENS
# ============================================================================

"""
In Python, functions are first-class citizens, meaning:
- Functions can be passed as arguments
- Functions can be returned from other functions
- Functions can be assigned to variables

This is the foundation of decorators.
"""

# Example: Functions can be assigned to variables
def greet():
    return "Hello"

say_hello = greet
print(f"say_hello(): {say_hello()}")  # Output: Hello

# Example: Functions can be passed as arguments
def call_function(func):
    return func()

print(f"call_function(greet): {call_function(greet)}")  # Output: Hello

# Example: Functions can be returned from other functions
def get_greeting(greet):
    # extra logic before or after the function call
    print("Before function execution")
    result = greet
    print("After function execution")
    return result

greeting_func = get_greeting(greet)
print(f"greeting_func(): {greeting_func()}")  # Output: Hello

# ============================================================================
# 3. BASIC DECORATOR (WITHOUT @ SYNTAX)
# ============================================================================

"""
Step 1: Create a decorator function
A decorator takes a function as input and returns a new function.
"""

# Step 1: Function inside a function
def my_decorator(func):
    def wrapper(name):
        print("Before function execution")
        func(name)
        print("After function execution")
    return wrapper

# Step 2: Apply the decorator manually
def say_hi(name):
    print(f"Hi {name}!")

decorated_func = my_decorator(say_hi)
print("\n--- Manual decorator application ---")
decorated_func('Vinod')
# Output:
# Before function execution
# Hi!
# After function execution

# ============================================================================
# 4. USING @decorator SYNTAX (PYTHONIC WAY)
# ============================================================================

"""
The @decorator syntax is the Pythonic way to apply decorators.
It's cleaner and more readable than manual application.
"""

def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

print("\n--- Using @decorator syntax ---")
say_hello()
# Output:
# Before function
# Hello!
# After function

# Note: This is exactly the same as:
# say_hello = my_decorator(say_hello)

# ============================================================================
# 5. DECORATOR WITH ARGUMENTS (MOST COMMON CASE)
# ============================================================================

"""
Most real functions take parameters, so decorators must handle them.
Use *args and **kwargs to accept any number of arguments.
"""

def log_function(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result
    return wrapper

@log_function
def add(a, b):
    return a + b

@log_function
def greet_person(name, age=None):
    if age:
        return f"Hello {name}, you are {age} years old"
    return f"Hello {name}"

print("\n--- Decorator with arguments ---")
result = add(3, 5)
print(f"Result: {result}")
# Output:
# Calling add with args=(3, 5), kwargs={}
# add returned: 8
# Result: 8

result = greet_person("Alice", age=25)
print(f"Result: {result}")
# Output:
# Calling greet_person with args=('Alice',), kwargs={'age': 25}
# greet_person returned: Hello Alice, you are 25 years old
# Result: Hello Alice, you are 25 years old

# ============================================================================
# 6. PRACTICAL REAL-WORLD DECORATOR EXAMPLES
# ============================================================================

# ----------------------------------------------------------------------------
# Example 1: Logging (Production / Backend)
# ----------------------------------------------------------------------------

"""
Used in:
- Backend APIs
- ETL jobs
- AI pipelines
"""

def logger(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Function {func.__name__} started")
        print(f"[LOG] Arguments: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] Function {func.__name__} ended with result: {result}")
        return result
    return wrapper

@logger
def process_order(order_id):
    print(f"Processing order {order_id}")
    return f"Order {order_id} processed successfully"

print("\n--- Example 1: Logging Decorator ---")
process_order("ORD-12345")

# ----------------------------------------------------------------------------
# Example 2: Execution Time Measurement (AI / ML / ETL)
# ----------------------------------------------------------------------------

"""
Used in:
- Model training
- Data processing
- Performance tuning
"""

import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timer
def train_model():
    print("Training model...")
    time.sleep(0.5)  # Simulate work
    return "Model trained"

@timer
def process_data(data_size):
    print(f"Processing {data_size} records...")
    time.sleep(0.3)  # Simulate work
    return f"Processed {data_size} records"

print("\n--- Example 2: Timer Decorator ---")
train_model()
process_data(1000)

# ----------------------------------------------------------------------------
# Example 3: Authorization Check (Web Apps)
# ----------------------------------------------------------------------------

"""
Used in:
- Django / Flask
- API security
- Role-based access
"""

def require_login(func):
    def wrapper(user, *args, **kwargs):
        if not user.get("is_logged_in"):
            print("Access denied! Please log in.")
            return None
        print(f"Access granted for user: {user.get('name', 'Unknown')}")
        return func(user, *args, **kwargs)
    return wrapper

@require_login
def view_dashboard(user):
    print("Welcome to dashboard")
    return "Dashboard content"

@require_login
def view_profile(user):
    print(f"Viewing profile for {user.get('name')}")
    return f"Profile of {user.get('name')}"

print("\n--- Example 3: Authorization Decorator ---")
user_logged_in = {"name": "Vinod", "is_logged_in": True}
user_not_logged_in = {"name": "Guest", "is_logged_in": False}

view_dashboard(user_logged_in)
view_dashboard(user_not_logged_in)

# ----------------------------------------------------------------------------
# Example 4: Caching (Very Important for AI & APIs)
# ----------------------------------------------------------------------------

"""
Used in:
- LLM calls
- API responses
- Expensive DB queries
"""

def simple_cache(func):
    cache = {}
    
    def wrapper(*args, **kwargs):
        # Create a key from arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in cache:
            print(f"[CACHE HIT] Returning cached result for {func.__name__}{args}")
            return cache[key]
        
        print(f"[CACHE MISS] Computing {func.__name__}{args}")
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    return wrapper

@simple_cache
def expensive_calc(n):
    print(f"Computing {n} * {n}...")
    return n * n

@simple_cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("\n--- Example 4: Caching Decorator ---")
print(f"expensive_calc(4): {expensive_calc(4)}")
print(f"expensive_calc(4): {expensive_calc(4)}")  # Should use cache
print(f"expensive_calc(5): {expensive_calc(5)}")
print(f"expensive_calc(5): {expensive_calc(5)}")  # Should use cache

# ----------------------------------------------------------------------------
# Example 5: Retry Logic (AI APIs / Network Calls)
# ----------------------------------------------------------------------------

"""
Used in:
- OpenAI / LLM calls
- Network requests
- External integrations
"""

def retry(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(times):
                try:
                    print(f"[RETRY] Attempt {i+1}/{times} for {func.__name__}")
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"[RETRY] Attempt {i+1} failed: {e}")
                    if i < times - 1:
                        time.sleep(0.1)  # Brief delay before retry
            
            raise Exception(f"All {times} retries failed. Last error: {last_exception}")
        return wrapper
    return decorator

@retry(3)
def unstable_api_call():
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise ValueError("API error: Service unavailable")
    return "API call successful"

print("\n--- Example 5: Retry Decorator ---")
try:
    result = unstable_api_call()
    print(f"Result: {result}")
except Exception as e:
    print(f"Final error: {e}")

# ============================================================================
# 7. DECORATORS WITH functools.wraps (IMPORTANT)
# ============================================================================

"""
Without functools.wraps, function metadata is lost.
This is important for:
- Keeping function name
- Keeping docstring
- Required for frameworks (FastAPI, Flask)
"""

from functools import wraps

# Without @wraps - metadata is lost
def decorator_without_wraps(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# With @wraps - metadata is preserved
def decorator_with_wraps(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator_without_wraps
def example_function():
    """This is a docstring for example_function."""
    return "Hello"

@decorator_with_wraps
def example_function_wrapped():
    """This is a docstring for example_function_wrapped."""
    return "Hello"

print("\n--- Example: functools.wraps ---")
print(f"Without wraps - name: {example_function.__name__}")  # Output: wrapper
print(f"Without wraps - doc: {example_function.__doc__}")  # Output: None

print(f"With wraps - name: {example_function_wrapped.__name__}")  # Output: example_function_wrapped
print(f"With wraps - doc: {example_function_wrapped.__doc__}")  # Output: This is a docstring...

# ============================================================================
# 8. BUILT-IN PYTHON DECORATORS YOU ALREADY USE
# ============================================================================

"""
Python provides several built-in decorators:
- @staticmethod
- @classmethod
- @property
"""

class User:
    def __init__(self, name, is_admin=False):
        self.name = name
        self._is_admin = is_admin
    
    @property
    def is_admin(self):
        """Property decorator - makes method accessible like an attribute"""
        return self._is_admin
    
    @is_admin.setter
    def is_admin(self, value):
        """Setter for property"""
        self._is_admin = value
    
    @staticmethod
    def validate_email(email):
        """Static method - doesn't need instance or class"""
        return "@" in email
    
    @classmethod
    def create_admin(cls, name):
        """Class method - receives class as first argument"""
        return cls(name, is_admin=True)

print("\n--- Example: Built-in Decorators ---")
user = User("Alice")
print(f"user.is_admin: {user.is_admin}")  # Using @property

user.is_admin = True  # Using setter
print(f"user.is_admin after setter: {user.is_admin}")

print(f"User.validate_email('test@example.com'): {User.validate_email('test@example.com')}")  # @staticmethod

admin = User.create_admin("Bob")  # @classmethod
print(f"admin.name: {admin.name}, admin.is_admin: {admin.is_admin}")

# ============================================================================
# 9. WHERE YOU'LL SEE DECORATORS IN REAL PROJECTS
# ============================================================================

"""
Decorators are used extensively in real-world projects:

Django / Flask routes:
   @app.route('/api/users')
   def get_users():
       ...

FastAPI dependencies:
   @app.get('/items')
   async def read_items():
       ...

AI pipelines (logging, timing, retry):
   @timer
   @logger
   def train_model():
       ...

Test frameworks (@pytest.mark):
   @pytest.mark.parametrize('input,expected', [(1, 2), (2, 4)])
   def test_double(input, expected):
       ...

Caching (@lru_cache):
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_embedding(text):
       ...

Access control:
   @require_auth
   @require_role('admin')
   def delete_user():
       ...
"""

# Example: Using functools.lru_cache (built-in caching decorator)
from functools import lru_cache

@lru_cache(maxsize=100)
def get_embedding(text):
    """Simulate expensive embedding computation"""
    print(f"Computing embedding for: {text}")
    return hash(text)  # Simulate embedding

print("\n--- Example: lru_cache Decorator ---")
print(f"get_embedding('hello'): {get_embedding('hello')}")
print(f"get_embedding('hello'): {get_embedding('hello')}")  # Should use cache
print(f"get_embedding('world'): {get_embedding('world')}")

# ============================================================================
# 10. DECORATORS WITH PARAMETERS
# ============================================================================

"""
Sometimes you need decorators that accept parameters.
This requires an extra level of nesting.
"""

def repeat(times):
    """Decorator factory - returns a decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for i in range(times):
                print(f"Call {i+1}/{times}")
                result = func(*args, **kwargs)
                results.append(result)
            return results
        return wrapper
    return decorator

@repeat(3)
def say_hi():
    return "Hi!"

print("\n--- Example: Decorator with Parameters ---")
results = say_hi()
print(f"Results: {results}")

# Another example: Rate limiting decorator
def rate_limit(max_calls, period):
    """Rate limiting decorator"""
    def decorator(func):
        calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove calls older than period
            calls[:] = [call_time for call_time in calls if now - call_time < period]
            
            if len(calls) >= max_calls:
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {period}s")
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

@rate_limit(max_calls=3, period=1)
def api_call():
    return "API response"

print("\n--- Example: Rate Limiting Decorator ---")
for i in range(3):
    print(f"Call {i+1}: {api_call()}")

try:
    api_call()  # Should fail - rate limit exceeded
except Exception as e:
    print(f"Error: {e}")

# ============================================================================
# 11. CHAINING MULTIPLE DECORATORS
# ============================================================================

"""
You can apply multiple decorators to a single function.
They are applied from bottom to top (closest to function first).
"""

def bold(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold
@italic
def get_text():
    return "Hello World"

print("\n--- Example: Chaining Decorators ---")
print(f"get_text(): {get_text()}")
# Output: <b><i>Hello World</i></b>
# Note: @bold is applied first, then @italic
# So: italic(bold(get_text))()

# ============================================================================
# 12. CLASS-BASED DECORATORS
# ============================================================================

"""
Decorators can also be implemented as classes.
This is useful when you need to maintain state.
"""

class CountCalls:
    """Decorator class that counts function calls"""
    def __init__(self, func):
        self.func = func
        self.count = 0
        wraps(func)(self)  # Preserve metadata
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} has been called {self.count} times")
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    return f"Hello, {name}!"

print("\n--- Example: Class-based Decorator ---")
print(greet("Alice"))
print(greet("Bob"))
print(greet("Charlie"))

# ============================================================================
# 13. MENTAL MODEL TO REMEMBER
# ============================================================================

"""
Decorator = function that takes a function and returns a new function
with added behavior

Original Function
       ↓
Decorator
       ↓
Enhanced Function

Key Points:
1. Decorators are functions that take functions as input
2. They return new functions with added behavior
3. Use @syntax for cleaner code
4. Always use functools.wraps to preserve metadata
5. Use *args and **kwargs to handle any function signature
6. Decorators are powerful for cross-cutting concerns:
   - Logging
   - Timing
   - Caching
   - Authentication
   - Retry logic
   - Rate limiting
"""

# ============================================================================
# 14. PRACTICAL EXERCISE: COMBINING DECORATORS
# ============================================================================

"""
Let's create a function with multiple decorators for a real-world scenario:
An API endpoint that needs logging, timing, caching, and retry logic.
"""

def api_endpoint(func):
    """Combines multiple concerns for an API endpoint"""
    
    # Apply logging
    @logger
    def logged_func(*args, **kwargs):
        return func(*args, **kwargs)
    
    # Apply timing
    @timer
    def timed_func(*args, **kwargs):
        return logged_func(*args, **kwargs)
    
    # Apply caching
    @simple_cache
    def cached_func(*args, **kwargs):
        return timed_func(*args, **kwargs)
    
    # Apply retry
    @retry(2)
    def retried_func(*args, **kwargs):
        return cached_func(*args, **kwargs)
    
    return retried_func

@api_endpoint
def get_user_data(user_id):
    """Simulate fetching user data"""
    print(f"Fetching data for user {user_id}")
    return f"Data for user {user_id}"

print("\n--- Example: Combined Decorators ---")
result = get_user_data(123)
print(f"Result: {result}")

print("\n" + "="*70)
print("DECORATORS SUMMARY")
print("="*70)
print("""
- Decorators wrap functions to add behavior
- Use @syntax for clean code
- Always use functools.wraps
- Handle arguments with *args and **kwargs
- Common uses: logging, timing, caching, auth, retry
- Can be chained and parameterized
- Essential for production Python code
""")
