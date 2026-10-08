import datetime

import pytest

import pricing_legacy


@pytest.fixture(autouse=True)
def reset_globals():
    """ล้าง Global State ก่อนและหลังรันเทสแต่ละข้อเพื่อป้องกันค่าตกค้าง"""
    pricing_legacy.member_points.clear()
    pricing_legacy.LOG.clear()
    yield
    pricing_legacy.member_points.clear()
    pricing_legacy.LOG.clear()


def test_normal_pricing():
    """ราคาปกติ: ซื้อน้อย ไม่ใช้สิทธิ์ใดๆ"""
    items = [("สมุด", 2, 50.0)]
    result = pricing_legacy.calc(items)
    # 2 * 50 = 100 -> บวกภาษี 7% = 107.0
    assert result == 107.0


def test_bulk_discount_thresholds():
    """ซื้อจำนวนมาก: ตรวจสอบที่เกณฑ์ 50 ชิ้น (ลด 5%) และ 100 ชิ้น (ลด 10%) พอดี"""
    # 50 ชิ้น ชิ้นละ 10 บาท: 500 * 0.95 = 475 -> ภาษี 7% = 508.25
    assert pricing_legacy.calc([("ปากกา", 50, 10.0)]) == 508.25

    # 100 ชิ้น ชิ้นละ 10 บาท: 1000 * 0.9 = 900 -> ภาษี 7% = 963.0
    assert pricing_legacy.calc([("ดินสอ", 100, 10.0)]) == 963.0


def test_zero_and_negative_quantity():
    """จำนวนเป็นศูนย์หรือติดลบ: ต้องข้ามไม่นำมาคิดราคา"""
    items = [("ยางลบ", 0, 20.0), ("ไม้บรรทัด", -5, 30.0), ("ปากกา", 1, 10.0)]
    # คิดเฉพาะปากกา 1 ชิ้น: 10 * 1.07 = 10.7
    assert pricing_legacy.calc(items) == 10.7


def test_member_discount_and_points():
    """สมาชิก: ได้ลด 5% และสะสมแต้ม 1 แต้มต่อ 100 บาท"""
    items = [("กระเป๋า", 1, 1000.0)]
    result = pricing_legacy.calc(items, member="Ploy")
    # 1000 * 0.95 = 950 -> แต้ม = int(950 / 100) = 9
    # 950 + 7% = 1016.5
    assert result == 1016.5
    assert pricing_legacy.member_points["Ploy"] == 9


def test_coupon_save50():
    """คูปอง SAVE50: หัก 50 บาท"""
    items = [("หนังสือ", 1, 200.0)]
    result = pricing_legacy.calc(items, coupon="SAVE50")
    # 200 - 50 = 150 -> ภาษี 7% = 160.5
    assert result == 160.5


def test_coupon_half():
    """คูปอง HALF: ลด 50%"""
    items = [("หนังสือ", 1, 200.0)]
    result = pricing_legacy.calc(items, coupon="HALF")
    # 200 * 0.5 = 100 -> ภาษี 7% = 107.0
    assert result == 107.0


def test_coupon_newyear_january_and_other_month():
    """คูปอง NEWYEAR: ลด 20% เฉพาะเดือนมกราคม"""
    items = [("หนังสือ", 1, 200.0)]
    january_date = datetime.date(2026, 1, 15)
    other_date = datetime.date(2026, 5, 20)

    # เดือน ม.ค. ได้ลด 20%: 200 * 0.8 = 160 -> ภาษี 7% = 171.2
    assert pricing_legacy.calc(items, coupon="NEWYEAR", today=january_date) == 171.2

    # เดือนอื่น ไม่ได้ลด: 200 -> ภาษี 7% = 214.0
    assert pricing_legacy.calc(items, coupon="NEWYEAR", today=other_date) == 214.0


def test_negative_total_floored_to_zero():
    """ยอดติดลบ: ส่วนลดมากกว่าราคา ยอดเงินต้องถูกจำกัดไว้ที่ 0 ไม่ติดลบ"""
    items = [("ยางลบ", 1, 20.0)]
    result = pricing_legacy.calc(items, coupon="SAVE50")
    # 20 - 50 = -30 -> ปรับเป็น 0 -> ภาษี 7% = 0.0
    assert result == 0.0


def test_log_side_effect():
    """ค่าที่ฟังก์ชันเก็บไว้: ตรวจสอบการบันทึก LOG ทุกครั้งที่เรียก"""
    pricing_legacy.calc([("ดินสอ", 1, 100.0)], member="Alice")
    assert len(pricing_legacy.LOG) == 1
    assert pricing_legacy.LOG[0] == ("Alice", 101.65)