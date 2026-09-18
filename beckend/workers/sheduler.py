from workers.connect_broker import broker
from workers.clear_db import QUEUE_CL,EXCHANGE_CL
from taskiq_faststream import AppWrapper,StreamScheduler,BrokerWrapper
from taskiq.schedule_sources import LabelScheduleSource


taskiq_broker=BrokerWrapper(broker=broker)

taskiq_broker.task(
     message='clear_db',
     queue=QUEUE_CL,
     exchange=EXCHANGE_CL,
     schedule=[{"cron": "0 */2 * * *"}]
)




schedule=StreamScheduler(
    broker=taskiq_broker,
    sources=[LabelScheduleSource(broker=taskiq_broker)]
)
