"""Reproduce the lab's quantity batching and signed 32-bit total offline.

This companion script performs no network requests and uses no session cookie.
"""


def batch_quantities(total, per_request=99):
    full_requests, remainder = divmod(total, per_request)
    quantities = [per_request] * full_requests
    if remainder:
        quantities.append(remainder)
    return quantities


def signed_32bit(value):
    return ((value + (1 << 31)) % (1 << 32)) - (1 << 31)


jacket_price_cents = 133_700
jacket_quantity = 32_123
belt_price_cents = 161
belt_quantity = 790

jacket_batches = batch_quantities(jacket_quantity)
belt_batches = batch_quantities(belt_quantity)
jacket_total_cents = signed_32bit(jacket_price_cents * jacket_quantity)
belt_total_cents = belt_price_cents * belt_quantity
cart_total_cents = jacket_total_cents + belt_total_cents

assert sum(jacket_batches) == jacket_quantity
assert sum(belt_batches) == belt_quantity
assert jacket_total_cents == -122_196
assert cart_total_cents == 4_994

print(f"Jacket: {jacket_quantity} units in {len(jacket_batches)} requests")
print(f"Belt:   {belt_quantity} units in {len(belt_batches)} requests")
print(f"Wrapped jacket line total: {jacket_total_cents} cents")
print(f"Final cart total: {cart_total_cents} cents (${cart_total_cents / 100:.2f})")
