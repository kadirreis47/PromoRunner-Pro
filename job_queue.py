import asyncio

from models.job import PromoJob


class JobQueue:

    def __init__(self):

        self.queue = asyncio.Queue()

    async def put(self, job: PromoJob):

        await self.queue.put(job)

        print(f"[QUEUE] İş eklendi : {job.site_name}")

    async def get(self) -> PromoJob:

        job = await self.queue.get()

        return job

    def done(self):

        self.queue.task_done()


job_queue = JobQueue()