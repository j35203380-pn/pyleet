from faststream import FastStream,ContextRepo
from connect_broker import broker
from contextlib import asynccontextmanager
import asyncio
from outbox.outbox_relay import outbox_run # вот это класс outbox котоый его запускает
from sqlalchemy.exc import SQLAlchemyError




@asynccontextmanager
async def lifespan(contex: ContextRepo):
        task=asyncio.create_task(outbox_run()) 

        yield
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
              print('Outbox завершен')

        except SQLAlchemyError as e:
              print(f"Ошибка базы данных в релее: {e}")


app=FastStream(broker,lifespan=lifespan)