import pytest

from inventory import Inventory


@pytest.fixture
def sample_inventory():
    """สร้างคลังสินค้าจำลองสำหรับทดสอบ"""
    inv = Inventory()
    inv.add_item("สมุดโน้ต", 10, 25.0)
    inv.add_item("ปากกา", 5, 15.0)
    inv.add_item("ดินสอ", 2, 5.0)
    inv.add_item("ยางลบ", 0, 10.0)
    return inv


# กรณีที่ 1: สินค้าทุกรายการมีจำนวนมากกว่า threshold -> ต้องคืน list ว่าง
def test_low_stock_items_none_below_threshold(sample_inventory):
    # สินค้าน้อยสุดคือ 0 ชิ้น ถ้า threshold เป็น -1 ต้องไม่เจออะไรเลย
    result = sample_inventory.low_stock_items(-1)
    assert result == []


# กรณีที่ 2: มีสินค้าที่จำนวนเท่ากับ threshold พอดี -> ต้องถูกนับรวมด้วย (<=)
def test_low_stock_items_exact_threshold(sample_inventory):
    # ปากกามี 5 ชิ้น พอดีกับ threshold 5
    result = sample_inventory.low_stock_items(5)
    # ต้องมี ยางลบ (0), ดินสอ (2), ปากกา (5)
    assert "ปากกา" in result
    assert "ดินสอ" in result
    assert "ยางลบ" in result


# กรณีที่ 3: มีสินค้าเข้าเกณฑ์หลายรายการ -> ผลลัพธ์ต้องเรียงตามชื่อ (Alphabetical)
def test_low_stock_items_sorted_by_name(sample_inventory):
    # สินค้าที่มี <= 5 ชิ้น ได้แก่ ปากกา, ดินสอ, ยางลบ
    result = sample_inventory.low_stock_items(5)
    # เรียงตามลำดับพยัญชนะไทย: ดินสอ -> ปากกา -> ยางลบ
    assert result == ["ดินสอ", "ปากกา", "ยางลบ"]


# กรณีที่ 4: คลังว่างเปล่า -> ต้องคืน list ว่าง ไม่ใช่ error
def test_low_stock_items_empty_inventory():
    empty_inv = Inventory()
    result = empty_inv.low_stock_items(5)
    assert result == []


# กรณีที่ 5: threshold เป็น 0 -> คืนเฉพาะสินค้าที่เหลือ 0
def test_low_stock_items_threshold_zero(sample_inventory):
    # ยางลบเหลือ 0 ชิ้น
    result = sample_inventory.low_stock_items(0)
    assert result == ["ยางลบ"]


# กรณีที่ 6: threshold ติดลบ -> คืน list ว่าง (เนื่องจากสต็อกต่ำสุดคือ 0)
def test_low_stock_items_negative_threshold(sample_inventory):
    result = sample_inventory.low_stock_items(-5)
    assert result == []

# --- ขั้นที่ 4: เสริม Test กรณีขอบและ Error ของเมธอด sell ---


def test_sell_exact_stock_remaining_zero(sample_inventory):
    """ค่าขอบ: ขายหมดเกลี้ยงพอดี สต็อกต้องเหลือ 0"""
    # ดินสอมี 2 ชิ้น ขาย 2 ชิ้น
    sample_inventory.sell("ดินสอ", 2)
    assert sample_inventory._items["ดินสอ"].quantity == 0


def test_sell_negative_quantity(sample_inventory):
    """ค่าที่ไม่ควรรับ: ขายจำนวนติดลบ ต้องเกิด ValueError"""
    with pytest.raises(ValueError, match="จำนวนที่ขายต้องมากกว่าศูนย์"):
        sample_inventory.sell("ปากกา", -1)


def test_sell_zero_quantity(sample_inventory):
    """ค่าที่ไม่ควรรับ: ขายจำนวน 0 ต้องเกิด ValueError"""
    with pytest.raises(ValueError, match="จำนวนที่ขายต้องมากกว่าศูนย์"):
        sample_inventory.sell("ปากกา", 0)


def test_sell_item_not_found(sample_inventory):
    """เส้นทาง error: ขายสินค้าที่ไม่มีในระบบ ต้องเกิด KeyError"""
    with pytest.raises(KeyError, match="ไม่พบสินค้า"):
        sample_inventory.sell("ไม้บรรทัด", 1)


def test_sell_exceed_available_quantity(sample_inventory):
    """เส้นทาง error: ขายเกินจำนวนที่มี ต้องเกิด ValueError"""
    # ปากกามี 5 ชิ้น ขาย 10 ชิ้น
    with pytest.raises(ValueError, match="ไม่เพียงพอ"):
        sample_inventory.sell("ปากกา", 10)