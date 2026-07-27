from telegram_client.parser import parse_message


samples = [
    """
🔥 CHATBET

Kod: CHAT500

1 yatırım şartlı

https://example.com/promo
""",
    """
ROBIN

RBNCMTTIME

Promosyonu almak için:
https://example.org/register
""",
    """
Site: BETDUNYASI
Bonus Kodu: BONUS250
https://example.net
""",
]


for index, message in enumerate(samples, start=1):
    result = parse_message(message)

    print("\n" + "=" * 50)
    print(f"TEST {index}")
    print(f"Site    : {result.site_name}")
    print(f"Kod     : {result.promo_code}")
    print(f"URL     : {result.url}")
    print(f"Geçerli : {result.is_valid}")