from dataclasses import dataclass
from datetime import datetime
from typing import NewType, List
from collections import namedtuple


#Batch Type
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)

#OrderLine Type
OrderReference = NewType("OrderReference", str)
ProductReference = NewType("ProductReference", str)

#ALL
Quantity = NewType("Quantity", int)

@dataclass(frozen=True)
class OrderLine:
    orderid: OrderReference
    sku: ProductReference
    qty: Quantity

@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str

@dataclass(frozen=True)
class Money:
    currency: str
    value: int

    def _validate_currency(self, currency, method):
        if currency != self.currency:
            raise ValueError(f"Cannot {method} {self.currency} to {currency}")
        return True

    def __add__(self, other) -> 'Money':
        self._validate_currency(other.currency, "add")
        return Money(self.currency, self.value+other.value)

    def __sub__(self, other) -> 'Money':
        self._validate_currency(other.currency, "sub")
        return Money(self.currency, self.value-other.value)
    
    def __mul__(self, other) -> 'Money':
        if type(other) != int and not self._validate_currency(other.currency,"mul"):
            raise ValueError(f"Me need INT or you Money -> {type(other)}")
        return Money(self.currency, self.value*other)
        

Line = namedtuple("Line", ["sku", "qty"])

class Batch:
    def __init__(self, ref: Reference, sku: Sku, qty: Quantity, eta: datetime | None = None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)
    
    @property
    def allocated_quntity(self) -> int:
        return sum(line.qty for line in self._allocations)
    
    @property
    def aviable_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quntity

    def can_allocate(self, line: OrderLine) -> bool:
        return bool(self.sku == line.sku and self.aviable_quantity >= line.qty)
    
    @classmethod
    def __validate_type(cls, other) -> int:
        if not isinstance(other, (int, Batch)):
            raise TypeError(f"ALERT you !{type(other)} me need 'int' or 'Batch'")
        return other if isinstance(other, int) else other.allocated_quntity

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.allocated_quntity > 0:
            return iter(self.allocated_quntity)
        else:
            raise StopIteration

    def __lt__(self, other) -> bool:
        quantity = self.__validate_type(other)
        return self.allocated_quntity < quantity
    
    def __gt__(self, other) -> bool:
        quantity = self.__validate_type(other)
        return self.allocated_quntity > quantity
    
    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference==self.reference
    
    def __hash__(self):
        return hash(self.reference)
    
    @staticmethod
    def other_allocate(line: OrderLine, batches: List['Batch']) -> str:
        batches = sorted(batches)
        for batch in batches:
            if not batch.can_allocate(line):
                raise ValueError(f"out of stock - {line.sku}")
            else:
                batch.allocate(line)
                return batch.reference

class Person:
    def __init__(self, name: Name):
        self.name = name