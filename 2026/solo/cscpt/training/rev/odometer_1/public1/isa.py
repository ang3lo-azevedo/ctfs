from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

TAPE = Dict[int,int]
make_tape = lambda: defaultdict(lambda: 1)
tape: TAPE = make_tape()

@dataclass
class Odometer:
  x: int = 0
  pebbles: int = 1000000

  def copy(self) -> 'Odometer':
    return Odometer(self.x, self.pebbles)


class Instruction:
  def apply(self, o: Odometer, t: TAPE) -> Odometer:
    return o.copy()
  def simplifiable(self) -> bool: return False
  def simplify(self) -> List['Instruction']: return [self]
  def __str__(self):
    return "NOP"

class ComplexInstruction(Instruction):
  def simplifiable(self) -> bool: return True


class INCX(Instruction):
  def apply(self, o: Odometer, t: TAPE) -> Odometer:
    ret = o.copy()
    ret.x += 1
    return ret
  def __str__(self):
    return "INCX"

class DECX(Instruction):
  def apply(self, o: Odometer, t: TAPE) -> Odometer:
    ret = o.copy()
    ret.x -= 1
    return ret
  def __str__(self):
    return "DECX"

class DROP(Instruction):
  def apply(self, o: Odometer, t: TAPE) -> Odometer:
    ret = o.copy()
    if ret.pebbles > 0:
      t[ret.x] += 1
      ret.pebbles -= 1
    return ret
  def __str__(self):
    return "DROP"
  
class PICKUP(Instruction):
  def apply(self, o: Odometer, t: TAPE) -> Odometer:
    ret = o.copy()
    if t[ret.x] > 0:
      t[ret.x] -= 1
      ret.pebbles += 1
    return ret
  def __str__(self):
    return "PICKUP"

class ZSTEP(Instruction):
  def apply(self, o: Odometer, t: TAPE) -> Odometer:
    ret = o.copy()
    if t[ret.x] == 0:
      ret.x += 1
    else:
      ret.x -= 1
    return ret
  
  def __str__(self):
    return "ZSTEP"
