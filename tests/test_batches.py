from learn_pattern import Batch, OrderLine, Money, Name, Line, Person
from datetime import date, timedelta

import pytest

def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty)
    )

def test_can_allocate_if_avilable_great_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)

def test_cannot_allocate_if_aviable_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False

def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2,2)
    assert batch.can_allocate(line)

def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False

def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.aviable_quantity == 20

def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK",20,2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.aviable_quantity == 18

def test_equality():
    assert Money("gbp", 10) == Money("gbp", 10)
    assert Name("Harry", "Percival") != Name("Bob", "Gregory")
    assert Line("RED-CHAIR", 5) == Line("RED-CHAIR", 5)

def test_name_equality():
    assert Name("Harry", "Percival") != Name("Barry", "Percival")

def test_barry_is_harry():
    harry = Person(Name("Harry", "Percival"))
    barry = harry

    barry.name = Name("Barry", "Percival")

    assert harry is barry and barry is harry

def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=(date.today()+timedelta(days=1)))
    
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    Batch.other_allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.aviable_quantity == 90
    assert shipment_batch.aviable_quantity == 100

def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, date.today())
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, (date.today()+timedelta(days=1)))

    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, (date.today()+timedelta(days=10)))

    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    Batch.other_allocate(line, [earliest, medium, latest])

    assert earliest.aviable_quantity == 90
    assert medium.aviable_quantity == 100
    assert latest.aviable_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, None)

    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", (date.today()+timedelta(days=1)))

    line  = OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = Batch.other_allocate(line, [in_stock_batch, shipment_batch])
    
    assert allocation == in_stock_batch.reference

def test_raises_out_of_stock_exeption_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK",10, date.today())
    batch.other_allocate(OrderLine("order1","SMALL-FORK",10), [batch])

    with pytest.raises(ValueError, match="SMALL-FORK"):
        batch.other_allocate(OrderLine('order2', 'SMALL-FORK', 1), [batch])