import asyncio

from browser.browser_manager import BrowserManager
from database.database import update_message_status
from job_queue import job_queue
from site_handlers.router import router


class PromoWorker:
    def __init__(self) -> None:
        self.browser = BrowserManager()

    async def run(self) -> None:
        await self.browser.start()
        print("[WORKER] Hazır.")

        while True:
            job = await job_queue.get()

            try:
                print()
                print("=" * 60)
                print(f"[WORKER] İşleniyor : {job.site_name}")
                print(f"[WORKER] Kod       : {job.promo_code}")
                print(f"[WORKER] URL       : {job.url}")

                update_message_status(
                    telegram_chat_id=job.telegram_chat_id,
                    telegram_message_id=job.telegram_message_id,
                    status="processing",
                    result_message="İş worker tarafından alındı.",
                )

                if not job.url:
                    raise ValueError("İş içerisinde URL bulunamadı.")

                if not job.promo_code:
                    raise ValueError("İş içerisinde promosyon kodu bulunamadı.")

                page = await self.browser.open_url(job.url)

                print("[WORKER] URL başarıyla açıldı.")

                handler = router.get_handler(job.site_name)

                print(
                    f"[WORKER] Seçilen handler: "
                    f"{handler.__class__.__name__}"
                )

                handler_result = await handler.handle(
                    page=page,
                    promo_code=job.promo_code,
                )

                if handler_result:
                    status = "handler_completed"
                    result_message = (
                        "URL açıldı ve site handler çalıştırıldı."
                    )
                    print("[WORKER] Handler başarıyla tamamlandı.")

                else:
                    status = "unsupported"
                    result_message = (
                        "URL açıldı ancak desteklenen site handler bulunamadı."
                    )
                    print("[WORKER] Site henüz desteklenmiyor.")

                update_message_status(
                    telegram_chat_id=job.telegram_chat_id,
                    telegram_message_id=job.telegram_message_id,
                    status=status,
                    result_message=result_message,
                )

                print("=" * 60)

            except Exception as error:
                error_message = str(error)

                update_message_status(
                    telegram_chat_id=job.telegram_chat_id,
                    telegram_message_id=job.telegram_message_id,
                    status="failed",
                    result_message=error_message,
                )

                print(f"[WORKER] Hata: {error_message}")

            finally:
                job_queue.done()

            await asyncio.sleep(1)


worker = PromoWorker()