#!/usr/local/bin/python3
"""
Pickle Scanner - Detects malicious pickles through taint tracking

This scanner safely analyzes Python pickle files by subclassing Unpickler and:
1. Tracking which values are "static" (directly pushed) vs "dynamic" (computed)
2. Recording all find_class calls without importing modules
3. Rejecting pickles that use dynamically constructed class names (e.g., STACK_GLOBAL with tainted strings)

The key insight: legitimate pickles have statically determinable class names,
while malicious pickles often use REDUCE to build class names dynamically.
"""

import sys
from io import BytesIO
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import pickle


@dataclass
class ScanResult:
    """Result of scanning a pickle file"""
    is_safe: bool
    static_classes: List[Tuple[str, str]]  # [(module, name), ...]
    rejection_reason: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class PickleScannerError(Exception):
    """Raised when a pickle is determined to be unsafe"""
    pass


class DummyCallable:
    """
    A dummy callable that can be used as a placeholder for classes.

    This allows REDUCE and other opcodes to "call" the class without
    actually executing any code.
    """
    def __call__(self, *args, **kwargs):
        # Return a new dummy object that's also marked as tainted
        return object()

    def __new__(cls, *args, **kwargs):
        # Handle NEWOBJ and NEWOBJ_EX opcodes
        return object()


class SafeUnpickler(pickle._Unpickler):
    """
    Safe pickle unpickler that tracks taint and detects dynamic class construction.

    This subclass overrides dangerous methods to prevent code execution while
    tracking whether values are statically or dynamically constructed.

    Only allows a whitelist of safe, trivially harmless classes.
    """

    # Whitelist of allowed classes - only trivially safe types
    SAFE_CLASSES = {
        # Basic immutable types
        ('builtins', 'int'),
        ('builtins', 'float'),
        ('builtins', 'str'),
        ('builtins', 'bytes'),
        ('builtins', 'bool'),
        ('builtins', 'NoneType'),

        # Basic container types
        ('builtins', 'list'),
        ('builtins', 'tuple'),
        ('builtins', 'dict'),
        ('builtins', 'set'),
        ('builtins', 'frozenset'),

        # Common safe types
        ('datetime', 'datetime'),
        ('datetime', 'date'),
        ('datetime', 'time'),
        ('datetime', 'timedelta'),
        ('decimal', 'Decimal'),
    }

    def __init__(self, file, *, strict=True):
        super().__init__(file)
        self.strict = strict
        self.tainted = set()          # Set of id() for tainted objects
        self.static_classes = []      # List[(module, name)]
        self.warnings = []
        self.rejection_reason = None

        # Manually update dispatch table to use our overridden methods
        # The pure Python Unpickler doesn't automatically use subclass methods
        self.dispatch[pickle.REDUCE[0]] = SafeUnpickler.load_reduce
        self.dispatch[pickle.BUILD[0]] = SafeUnpickler.load_build
        self.dispatch[pickle.INST[0]] = SafeUnpickler.load_inst
        self.dispatch[pickle.OBJ[0]] = SafeUnpickler.load_obj
        self.dispatch[pickle.NEWOBJ[0]] = SafeUnpickler.load_newobj
        self.dispatch[pickle.NEWOBJ_EX[0]] = SafeUnpickler.load_newobj_ex
        self.dispatch[pickle.STACK_GLOBAL[0]] = SafeUnpickler.load_stack_global
        self.dispatch[pickle.TUPLE[0]] = SafeUnpickler.load_tuple
        self.dispatch[pickle.LIST[0]] = SafeUnpickler.load_list
        self.dispatch[pickle.DICT[0]] = SafeUnpickler.load_dict
        self.dispatch[pickle.APPEND[0]] = SafeUnpickler.load_append
        self.dispatch[pickle.APPENDS[0]] = SafeUnpickler.load_appends
        self.dispatch[pickle.SETITEM[0]] = SafeUnpickler.load_setitem
        self.dispatch[pickle.SETITEMS[0]] = SafeUnpickler.load_setitems
        self.dispatch[pickle.ADDITEMS[0]] = SafeUnpickler.load_additems
        self.dispatch[pickle.FROZENSET[0]] = SafeUnpickler.load_frozenset
        self.dispatch[pickle.PERSID[0]] = SafeUnpickler.load_persid
        self.dispatch[pickle.BINPERSID[0]] = SafeUnpickler.load_binpersid

    def _mark_tainted(self, obj):
        """Mark an object as tainted (dynamically constructed)"""
        self.tainted.add(id(obj))
        return obj

    def _is_tainted(self, obj):
        """Check if an object is tainted"""
        return id(obj) in self.tainted

    def _reject(self, reason):
        """Mark the pickle as rejected and raise an error"""
        self.rejection_reason = reason
        raise PickleScannerError(reason)

    # =========================================================================
    # CRITICAL SECURITY OVERRIDES
    # =========================================================================

    def find_class(self, module, name):
        """
        Override find_class to record class references without importing.

        This is called by GLOBAL, INST, and EXT* opcodes. We record the
        (module, name) pair and check against our whitelist of safe classes.

        Only trivially safe classes are allowed!
        """
        # Record class reference
        self.static_classes.append((module, name))

        # Check whitelist
        if (module, name) not in self.SAFE_CLASSES:
            self._reject(
                f"Class '{module}.{name}' is not in the safe class whitelist. "
                f"Only trivially safe types are allowed."
            )
        # Return a dummy callable marked as tainted
        dummy = DummyCallable()
        return self._mark_tainted(dummy)

    def load_stack_global(self):
        """
        Override STACK_GLOBAL opcode handler - CRITICAL SECURITY CHECK.

        STACK_GLOBAL pops module and name from the stack. If either is tainted
        (dynamically constructed), this indicates a malicious pickle trying to
        obfuscate which class is being loaded.
        """
        # Pop name and module from stack
        name = self.stack.pop()
        module = self.stack.pop()

        # SECURITY CHECK: Reject if either is tainted
        if self._is_tainted(name) or self._is_tainted(module):
            self._reject(
                f"STACK_GLOBAL with dynamically constructed class name: "
                f"module={'<tainted>' if self._is_tainted(module) else repr(module)}, "
                f"name={'<tainted>' if self._is_tainted(name) else repr(name)}"
            )

        # Verify they're strings
        if not isinstance(name, str) or not isinstance(module, str):
            self._reject(
                f"STACK_GLOBAL requires string arguments, got "
                f"module={type(module).__name__}, name={type(name).__name__}"
            )

        # Record and push dummy
        klass = self.find_class(module, name)
        self.append(klass)

    def load_reduce(self):
        """
        Override REDUCE opcode handler.

        REDUCE pops a callable and args tuple, then executes callable(*args).
        This is the primary code execution vector. We simulate it by pushing
        a tainted dummy object without executing anything.
        """
        args = self.stack.pop()
        func = self.stack.pop()

        # Don't execute! Just push a tainted dummy
        dummy = object()
        self._mark_tainted(dummy)
        self.append(dummy)

    def load_build(self):
        """
        Override BUILD opcode handler.

        BUILD pops state and instance, then calls instance.__setstate__(state)
        or updates instance.__dict__. We simulate this by marking the instance
        as tainted without modifying it.
        """
        state = self.stack.pop()
        inst = self.stack[-1]

        # Mark instance as tainted (it's been modified)
        self._mark_tainted(inst)
        # Note: instance is still on stack (BUILD doesn't pop it)

    # =========================================================================
    # INSTANCE CREATION OVERRIDES
    # =========================================================================

    def load_inst(self):
        """
        Override INST opcode handler (protocol 0).

        INST reads module/name from opcode stream (always static), pops args
        from mark, then instantiates the class. We record the class and push
        a tainted dummy instance.
        """
        # Read module and class name (from opcode stream - always static)
        module = self.readline()[:-1].decode("ascii")
        name = self.readline()[:-1].decode("ascii")

        # Record the class
        klass = self.find_class(module, name)

        # Pop arguments
        args = self.pop_mark()

        # Don't instantiate! Push tainted dummy
        dummy = object()
        self._mark_tainted(dummy)
        self.append(dummy)

    def load_obj(self):
        """
        Override OBJ opcode handler (protocol 1).

        OBJ pops [mark, cls, arg1, arg2, ...] from stack and instantiates.
        The class comes from the stack (not find_class).
        """
        args = self.pop_mark()
        cls = args.pop(0)  # First element is the class

        # Don't instantiate! Push tainted dummy
        dummy = object()
        self._mark_tainted(dummy)
        self.append(dummy)

    def load_newobj(self):
        """
        Override NEWOBJ opcode handler (protocol 2).

        NEWOBJ pops args tuple and class, then calls cls.__new__(cls, *args).
        """
        args = self.stack.pop()
        cls = self.stack.pop()

        # Don't execute __new__! Push tainted dummy
        dummy = object()
        self._mark_tainted(dummy)
        self.append(dummy)

    def load_newobj_ex(self):
        """
        Override NEWOBJ_EX opcode handler (protocol 4).

        NEWOBJ_EX pops kwargs dict, args tuple, and class, then calls
        cls.__new__(cls, *args, **kwargs).
        """
        kwargs = self.stack.pop()
        args = self.stack.pop()
        cls = self.stack.pop()

        # Don't execute __new__! Push tainted dummy
        dummy = object()
        self._mark_tainted(dummy)
        self.append(dummy)

    # =========================================================================
    # PERSISTENT ID HANDLING
    # =========================================================================

    def persistent_load(self, pid):
        """
        Override persistent_load to mark result as tainted.

        Persistent IDs are rarely used in legitimate pickles and could be
        used for obfuscation or attacks.
        """
        if self.strict:
            self.warnings.append(f"Persistent ID used: {pid!r}")

        # Return a tainted dummy object
        dummy = object()
        self._mark_tainted(dummy)
        return dummy

    def load_persid(self):
        """
        Override PERSID opcode handler (protocol 0).

        PERSID reads a persistent ID from the opcode stream and calls
        persistent_load(). We mark the result as tainted.
        """
        try:
            pid = self.readline()[:-1].decode("ascii")
        except UnicodeDecodeError:
            self._reject("PERSID with non-ASCII persistent ID")

        obj = self.persistent_load(pid)
        self.append(obj)

    def load_binpersid(self):
        """
        Override BINPERSID opcode handler (protocol 1+).

        BINPERSID pops a persistent ID from the stack and calls
        persistent_load(). We mark the result as tainted.
        """
        pid = self.stack.pop()
        obj = self.persistent_load(pid)
        self.append(obj)

    # =========================================================================
    # CONTAINER TAINT PROPAGATION
    # =========================================================================

    def load_tuple(self):
        """
        Override tuple construction to propagate taint.

        If any element in the tuple is tainted, the tuple itself is tainted.
        """
        items = self.pop_mark()
        t = tuple(items)

        # Propagate taint
        if any(self._is_tainted(item) for item in items):
            self._mark_tainted(t)

        self.append(t)

    def load_list(self):
        """
        Override list construction to propagate taint.

        If any element in the list is tainted, the list itself is tainted.
        """
        items = self.pop_mark()
        lst = list(items)

        # Propagate taint
        if any(self._is_tainted(item) for item in items):
            self._mark_tainted(lst)

        self.append(lst)

    def load_dict(self):
        """
        Override dict construction to propagate taint.

        If any key or value in the dict is tainted, the dict itself is tainted.
        """
        items = self.pop_mark()
        d = {}
        for i in range(0, len(items), 2):
            key = items[i]
            value = items[i + 1]
            d[key] = value

        # Propagate taint
        if any(self._is_tainted(item) for item in items):
            self._mark_tainted(d)

        self.append(d)

    def load_append(self):
        """
        Override APPEND opcode to propagate taint.

        If we're appending a tainted value to a list, the list becomes tainted.
        """
        value = self.stack.pop()
        lst = self.stack[-1]

        lst.append(value)

        # Propagate taint
        if self._is_tainted(value):
            self._mark_tainted(lst)

    def load_appends(self):
        """
        Override APPENDS opcode to propagate taint.

        If we're appending any tainted values to a list, the list becomes tainted.
        """
        items = self.pop_mark()
        lst = self.stack[-1]

        lst.extend(items)

        # Propagate taint
        if any(self._is_tainted(item) for item in items):
            self._mark_tainted(lst)

    def load_setitem(self):
        """
        Override SETITEM opcode to propagate taint.

        If we're setting a tainted key or value, the dict becomes tainted.
        """
        value = self.stack.pop()
        key = self.stack.pop()
        d = self.stack[-1]

        d[key] = value

        # Propagate taint
        if self._is_tainted(key) or self._is_tainted(value):
            self._mark_tainted(d)

    def load_setitems(self):
        """
        Override SETITEMS opcode to propagate taint.

        If we're setting any tainted keys or values, the dict becomes tainted.
        """
        items = self.pop_mark()
        d = self.stack[-1]

        for i in range(0, len(items), 2):
            key = items[i]
            value = items[i + 1]
            d[key] = value

        # Propagate taint
        if any(self._is_tainted(item) for item in items):
            self._mark_tainted(d)

    def load_additems(self):
        """
        Override ADDITEMS opcode (protocol 4) to propagate taint.

        If we're adding any tainted items to a set, the set becomes tainted.
        """
        items = self.pop_mark()
        s = self.stack[-1]

        s.update(items)

        # Propagate taint
        if any(self._is_tainted(item) for item in items):
            self._mark_tainted(s)

    def load_frozenset(self):
        """
        Override FROZENSET opcode (protocol 4) to propagate taint.

        If any element is tainted, the frozenset itself is tainted.
        """
        items = self.pop_mark()
        fs = frozenset(items)

        # Propagate taint
        if any(self._is_tainted(item) for item in items):
            self._mark_tainted(fs)

        self.append(fs)

    # =========================================================================
    # EXTENSION OPCODE HANDLING
    # =========================================================================

    def get_extension(self, code):
        """
        Override extension registry handling.

        EXT* opcodes are rare in legitimate pickles and could be used for
        obfuscation. In strict mode, we warn about them.
        """
        if self.strict:
            self.warnings.append(f"EXT opcode used (code={code}) - uncommon in legitimate pickles")

        # Call parent implementation but mark result as tainted
        try:
            super().get_extension(code)
            # Mark the top of stack as tainted
            if self.stack:
                self._mark_tainted(self.stack[-1])
        except Exception:
            # If extension code isn't registered, that's suspicious
            self.warnings.append(f"Unregistered extension code {code}")
            raise


# =============================================================================
# PUBLIC API
# =============================================================================

def scan_pickle(data: bytes, strict=True) -> ScanResult:
    """
    Scan a pickle and return a safety verdict.

    Args:
        data: Pickle bytes to scan
        strict: If True, warn about uncommon opcodes like EXT*

    Returns:
        ScanResult with safety verdict, list of static classes, and any warnings
    """
    unpickler = SafeUnpickler(BytesIO(data), strict=strict)
    try:
        unpickler.load()

        if unpickler.rejection_reason:
            return ScanResult(
                is_safe=False,
                static_classes=unpickler.static_classes,
                rejection_reason=unpickler.rejection_reason,
                warnings=unpickler.warnings
            )

        return ScanResult(
            is_safe=True,
            static_classes=unpickler.static_classes,
            warnings=unpickler.warnings
        )

    except PickleScannerError:
        # Already handled - rejection_reason is set
        return ScanResult(
            is_safe=False,
            static_classes=unpickler.static_classes,
            rejection_reason=unpickler.rejection_reason,
            warnings=unpickler.warnings
        )

    except Exception as e:
        return ScanResult(
            is_safe=False,
            static_classes=unpickler.static_classes,
            rejection_reason=f"Unpickling error: {type(e).__name__}: {e}",
            warnings=unpickler.warnings
        )


def scan_pickle_file(path: str, strict=True) -> ScanResult:
    """
    Scan a pickle file and return a safety verdict.

    Args:
        path: Path to pickle file
        strict: If True, warn about uncommon opcodes like EXT*

    Returns:
        ScanResult with safety verdict, list of static classes, and any warnings
    """
    with open(path, 'rb') as f:
        data = f.read()
    return scan_pickle(data, strict=strict)


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python scanner.py <pickle_file>")
        print()
        print("Scans a pickle file for malicious dynamic class construction.")
        print()
        print("Returns:")
        print("  - Exit code 0 if pickle is safe (static class names)")
        print("  - Exit code 1 if pickle is unsafe (dynamic class names)")
        sys.exit(1)

    pickle_path = sys.argv[1]

    try:
        result = scan_pickle_file(pickle_path)
    except FileNotFoundError:
        print(f"Error: File not found: {pickle_path}")
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)

    # Print results
    print(f"File: {pickle_path}")
    print(f"Safe: {result.is_safe}")
    print(f"Classes found: {len(result.static_classes)}")

    if result.static_classes:
        print("\nStatic class references:")
        for module, name in result.static_classes:
            print(f"  - {module}.{name}")

    if result.rejection_reason:
        print(f"\n❌ REJECTED: {result.rejection_reason}")

    if result.warnings:
        print("\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    if result.is_safe:
        print("\n✅ Pickle appears safe (all class names are static)")
        print("   Note: This scanner only checks for dynamic class construction.")
        print("   You should still validate that the classes themselves are safe!")

    sys.exit(0 if result.is_safe else 1)
