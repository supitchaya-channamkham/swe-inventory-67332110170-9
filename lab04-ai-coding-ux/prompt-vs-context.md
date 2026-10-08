# การทดลองเปรียบเทียบ: Prompt Engineering vs Context Engineering

## 1. รอบที่ 1: Prompt Engineering ทั่วไป (ไม่มี Context)

### Prompt ที่ใช้:
> "เขียนฟังก์ชันใน Python สำหรับขายสินค้าหลายรายการพร้อมกัน (sell multiple items) ในระบบสต็อกสินค้า"

### ผลลัพธ์จาก AI:
```python
def sell_items(inventory, items_to_sell):
    for item, qty in items_to_sell.items():
        if item in inventory and inventory[item] >= qty:
            inventory[item] -= qty
        else:
            print("Stock not enough or item not found")
            return False
    return True
```
ข้อสังเกตและข้อบกพร่อง:
AI คาดเดาโครงสร้างข้อมูลเอง โดยมองว่า inventory เป็น dict ธรรมดา ไม่ได้ใช้คลาส Inventory และ InventoryItem ที่มีอยู่จริง

ไม่รองรับคุณสมบัติ Atomicity: หากตัดสต็อกชิ้นแรกผ่าน แต่ชิ้นที่สองไม่พอ สต็อกของชิ้นแรกจะถูกหักไปแล้วโดยไม่มีการ Rollback

การจัดการ Error ไม่ตรงตามมาตรฐานเดิมของระบบ (ใช้ print และคืนค่า False แทนที่จะ raise ValueError หรือ KeyError)


## รอบที่ 2: Context Engineering (แนบ Context และข้อจำกัดครบถ้วน)
## Prompt ที่ใช้:
ปรับปรุงเมธอด sell() ของคลาส Inventory ด้านล่างให้รองรับการขายหลายรายการพร้อมกัน

[แนบโค้ด inventory.py ฉบับถูกต้องทั้งไฟล์]

ข้อกำหนด:

เพิ่มเมธอด sell_many(orders: dict[str, int]) -> dict[str, int] คืนค่าเป็น {ชื่อสินค้า: จำนวนคงเหลือ}

ต้องเป็น Atomic: หากมีรายการใดสต็อกไม่พอหรือไม่มีสินค้า ต้อง raise Exception และต้องไม่มีสินค้าชิ้นใดถูกหักยอดเลยแม้แต่ชิ้นเดียว (All-or-Nothing)

ใช้ Exception แบบเดียวกับเมธอดเดิม (KeyError เมื่อไม่พบสินค้า, ValueError เมื่อจำนวนไม่พอหรือจำนวน <= 0)

ห้ามใช้ Library ภายนอก

ต้องผ่านเกณฑ์การทดสอบ:

ขายหลายรายการพร้อมกันสำเร็จ คืนยอดคงเหลือถูกต้อง

ถ้ารายการที่สองสต็อกไม่พอ ต้องไม่หักสต็อกของรายการแรก

## ผลลัพธ์จาก AI:
```python
def sell_many(self, orders: dict[str, int]) -> dict[str, int]:
    # Phase 1: Validation (ตรวจเช็กทุกรายการล่วงหน้าก่อนตัดยอด เพื่อให้เป็น Atomic)
    for name, amount in orders.items():
        if name not in self._items:
            raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
        if amount <= 0:
            raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
        if self._items[name].quantity < amount:
            raise ValueError(
                f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น "
                f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
            )

    # Phase 2: Execution (ตัดยอดจริงหลังตรวจสอบผ่านทั้งหมด)
    result = {}
    for name, amount in orders.items():
        self._items[name].quantity -= amount
        result[name] = self._items[name].quantity

    return result
```
## 3. สรุปความต่างและปัจจัยที่ทำให้ผลลัพธ์ต่างกัน

| ประเด็นเปรียบเทียบ | Prompt ทั่วไป (ขาด Context) | Context Engineering (มี Context ครบ) |
| :--- | :--- | :--- |
| **ความเข้ากันได้กับระบบ (Compatibility)** | ไม่สามารถนำมาใช้งานร่วมกับโค้ดเดิมได้ทันที เพราะ AI สุ่มสร้าง data structure ใหม่ | สอดคล้องกับคลาสเดิม 100% สามารถนำเข้าเป็น method ของ `Inventory` ได้ทันที |
| **ความถูกต้องของ Logic ธุรกิจ** | พังเมื่อเกิดข้อผิดพลาดกลางทาง สต็อกค้างคาเพราะขาด Atomicity | ทำงานแบบ All-or-Nothing ด้วยการแยก Pre-validation ก่อนตัดสต็อกจริง |
| **Error Handling** | ใช้การ print ข้อความ ไม่เกิด Exception ตามที่ระบบออกแบบ | raise `KeyError` และ `ValueError` สอดคล้องกับเมธอด `sell()` เดิม |

**สรุปสาเหตุความต่าง:** สิ่งที่ทำให้รอบที่ 2 ได้โค้ดที่ถูกต้องไม่ใช่การใช้คำสั่งที่ยาวขึ้น แต่เกิดจาก **Context ที่เพียงพอ** ทั้งตัวโครงสร้างโค้ดเดิม ขอบเขต Exception และเงื่อนไขทดสอบที่กำกับพฤติกรรมของ AI ไม่ให้เขียนโค้ดสุ่มสี่สุ่มห้า

