from database.database import get_connection


with get_connection() as connection:
    rows = connection.execute(
        """
        SELECT
            telegram_message_id,
            site_name,
            promo_code,
            url,
            is_valid,
            status,
            result_message,
            created_at
        FROM promo_messages
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()


if not rows:
    print("Henüz kayıtlı mesaj yok.")

else:
    for row in rows:
        print("\n" + "=" * 70)
        print(f"Mesaj ID : {row['telegram_message_id']}")
        print(f"Site      : {row['site_name']}")
        print(f"Kod       : {row['promo_code']}")
        print(f"URL       : {row['url']}")
        print(f"Geçerli   : {bool(row['is_valid'])}")
        print(f"Durum     : {row['status']}")
        print(f"Sonuç     : {row['result_message']}")
        print(f"Kayıt     : {row['created_at']}")