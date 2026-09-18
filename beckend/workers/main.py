from faststream import FastStream,ContextRepo
from workers.connect_broker import broker
from contextlib import asynccontextmanager
import asyncio
# вот это класс outbox котоый его запускает
from workers.outbox.outbox_relay import outbox_run
from sqlalchemy.exc import SQLAlchemyError
from workers.inbox.inbox_relay import queue_work,inbox_workers



@asynccontextmanager
async def lifespan(contex: ContextRepo):
      task=asyncio.create_task(outbox_run()) 
      item=asyncio.create_task(inbox_workers(queue_work,2))
      yield
      
      task.cancel()
      item.cancel()
      try:
          await task
      except asyncio.CancelledError:
            print('Outbox завершен')

      except SQLAlchemyError as e:
            print(f"Ошибка базы данных в релее: {e}")
      

      try:
          await item
      except asyncio.CancelledError:
            print('inbox_workers завершен')

      except SQLAlchemyError as e:
            print(f"Ошибка базы данных в релее: {e}")
      

app=FastStream(broker,lifespan=lifespan)

