class Item:
    def __init__(self, name: str, quantity: int, price: float = 0.0):
        self.name = name
        self.quantity = quantity
        self.price = price


class Inventory:
    def __init__(self):
        self._items: dict[str, Item] = {}

    @property
    def items(self) -> dict[str, Item]:
        return self._items

    def add_item(self, name: str, quantity: int, price: float = 0.0) -> None:
        if price < 0:
            raise ValueError("ราคาต้องไม่ติดลบ")
        if quantity < 0:
            raise ValueError("จำนวนต้องไม่ติดลบ")

        if name in self._items:
            self._items[name].quantity += quantity
            self._items[name].price = price
        else:
            self._items[name] = Item(name=name, quantity=quantity, price=price)

    def remove_item(self, name: str) -> None:
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า: {name}")
        del self._items[name]

    def sell(self, name: str, quantity: int) -> float:
        if quantity <= 0:
            raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า: {name}")

        item = self._items[name]
        if item.quantity < quantity:
            raise ValueError("สินค้าไม่เพียงพอ")

        item.quantity -= quantity
        return item.price * quantity

    def total_inventory_value(self) -> float:
        return sum(item.price * item.quantity for item in self._items.values())

    def low_stock_items(self, threshold: int = 5) -> list[str]:
        matching_items = [
            item.name
            for item in self._items.values()
            if item.quantity <= threshold
        ]
        return sorted(matching_items)