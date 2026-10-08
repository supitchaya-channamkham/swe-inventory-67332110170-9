import datetime

TAX_RATE = 0.07
member_points: dict[str, int] = {}
LOG: list[tuple[str | None, float]] = []


def calc(
    items: list[tuple[str, int, float]],
    member: str | None = None,
    coupon: str | None = None,
    today: datetime.date | None = None,
) -> float:
    total = 0.0

    # 1. คำนวณราคาสินค้ารายชิ้น พร้อมส่วนลดการซื้อจำนวนมาก
    for _, quantity, unit_price in items:
        if quantity <= 0:
            continue

        item_subtotal = quantity * unit_price
        if quantity >= 100:
            item_subtotal *= 0.90
        elif quantity >= 50:
            item_subtotal *= 0.95

        total += item_subtotal

    # 2. คำนวณส่วนลดสมาชิกและบันทึกแต้มสะสม
    if member is not None:
        if member not in member_points:
            member_points[member] = 0
        total *= 0.95
        member_points[member] += int(total / 100)

    # 3. คำนวณส่วนลดคูปอง
    if coupon is not None:
        if coupon == "SAVE50":
            total -= 50
        elif coupon == "HALF":
            total *= 0.50
        elif coupon == "NEWYEAR":
            current_date = today if today is not None else datetime.date.today()
            if current_date.month == 1:
                total *= 0.80

    # 4. ป้องกันยอดติดลบ
    if total < 0:
        total = 0.0

    # 5. คำนวณภาษีมูลค่าเพิ่มและปัดเศษทศนิยม
    final_total = round(total * (1 + TAX_RATE), 2)

    # 6. บันทึกประวัติการคำนวณ
    LOG.append((member, final_total))

    return final_total