def parse_query(text: str) -> tuple[float, str, str]:
    parts = text.replace(",", ".").upper().split()
    parts = [p for p in parts if p not in ("B", "IN", "TO")]
    if len(parts) != 3:
        raise ValueError("Неверный формат")
    amount = float(parts[0])
    if amount <= 0:
        raise ValueError("Сумма должна быть больше нуля")
    return amount, parts[1], parts[2]

def convert(amount: float, from_code: str, to_code: str, rates: dict) -> float:
    return amount * rates[from_code] / rates[to_code]
