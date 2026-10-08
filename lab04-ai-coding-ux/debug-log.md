# Debugging Log: discount.py

บันทึกกระบวนการ Evidence-Based Debugging ตามขั้นตอน Reproduce -> Traceback -> Hypothesis -> Confirm -> Fix & Re-run

---

## 1. ผลลัพธ์จากการรันรอบแรก (Initial Run Output)

คำสั่งที่ใช้: `python -m pytest tests/test_discount.py -v`

```text
FAILED tests/test_discount.py::test_apply_discount_basic - assert 99.9 == 90.0
FAILED tests/test_discount.py::test_bulk_total - assert 299.9 == 270.0
FAILED tests/test_discount.py::test_average_price_empty - ZeroDivisionError: division by zero
FAILED tests/test_discount.py::test_cheapest_n - AssertionError: assert [20.0] == [10.0, 20.0]
PASSED tests/test_discount.py::test_apply_discount_zero
PASSED tests/test_discount.py::test_average_price
======================== 4 failed, 2 passed in 0.05s =========================

| test ที่ไม่ผ่าน | traceback หรือ assertion ที่เห็น | สมมติฐาน root cause | วิธียืนยัน | การแก้ |
| :--- | :--- | :--- | :--- | :--- |
| `test_apply_discount_basic` | `assert 99.9 == 90.0`<br>`Where: 99.9 = apply_discount(100.0, 10)` | สูตรคิดส่วนลดผิด โดยนำ `percent / 100` ไปลบออกจากราคาตรง ๆ แทนที่จะคิดตามสัดส่วนของราคา (`price * (percent / 100)`) | คำนวณมือตามสูตรเดิม: `100 - (10/100) = 99.9` ซึ่งตรงกับ assertion error | เปลี่ยนสูตรการคำนวณเป็น `return price * (1 - percent / 100)` |
| `test_bulk_total` | `assert 299.9 == 270.0`<br>`Where: 299.9 = bulk_total([100.0, 100.0, 100.0], 10)` | ฟังก์ชันรวมผลรวมราคาถูกต้อง (300) แต่เรียก `apply_discount` ต่อ ทำให้รับผลกระทบจากสูตรคิดส่วนลดที่ผิดพลาดมาด้วย | ตรวจสอบค่าผลบวกพบว่าได้ 300 ถูกต้อง แต่เมื่อผ่าน `apply_discount(300, 10)` กลับได้ 299.9 | แก้ไขฟังก์ชัน `apply_discount` ให้ถูกต้อง เคสนี้จะผ่านทันที |
| `test_average_price_empty` | `ZeroDivisionError: division by zero`<br>ที่บรรทัด `sum(prices) / len(prices)` | ไม่มีการดักกรณีรับลิสต์ว่าง (`prices = []`) ทำให้ `len(prices)` มีค่าเป็น 0 จนเกิดการหารด้วยศูนย์ | ส่ง `[]` เข้าฟังก์ชันแล้วพบว่าโค้ดไม่มีเงื่อนไขตรวจสอบความยาวลิสต์ก่อนหาร | เพิ่มเงื่อนไข `if not prices: return 0.0` ไว้ด้านบนสุดก่อนทำการหาร |
| `test_cheapest_n` | `AssertionError: assert [20.0] == [10.0, 20.0]`<br>`Left contains 1 item, Right contains 2` | ใช้ Slicing ผิดตำแหน่ง โดยใช้ `ordered[1:n]` ทำให้เริ่มตัดที่ index 1 ข้ามตัวที่ราคาถูกที่สุดตัวแรก (index 0) ไป | ทดลองตัดลิสต์ `[10, 20, 30, 50][1:2]` พบว่าได้ `[20]` ขาด index 0 ที่มีค่า 10 ไป | ปรับ Slicing ให้เริ่มจาก index แรก โดยเปลี่ยนเป็น `ordered[:n]` |

## 3. สรุปผลหลังการแก้ไขโค้ด (Verification)

```text
tests/test_discount.py::test_apply_discount_basic PASSED                 [ 16%]
tests/test_discount.py::test_apply_discount_zero PASSED                  [ 33%]
tests/test_discount.py::test_bulk_total PASSED                           [ 50%]
tests/test_discount.py::test_average_price PASSED                        [ 66%]
tests/test_discount.py::test_average_price_empty PASSED                  [ 83%]
tests/test_discount.py::test_cheapest_n PASSED                          [100%]
========================== 6 passed in 0.03s ===========================

