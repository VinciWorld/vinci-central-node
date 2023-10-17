import json
import logging
from typing import Callable
import uuid
import pika

from app.domains.train_job.schemas.train_job import TrainJobQueue
from app.settings.settings import settings, Environments, rabbitmq_settings
from app.domains.train_job.schemas.train_job_constants import TrainJobStatus

logger = logging.getLogger(__name__) 

class RabbitMQClient:
    def __init__(self, connection: pika.BlockingConnection):
        self.connection = connection
        self.channel = self.connection.channel()
        self.is_consuming = True

        self.channel.basic_qos(prefetch_count=1)
        
        try:
            # Declare the 'jobs' queue with max priority 5
            self.channel.queue_declare(queue='jobs', durable=True, arguments={'x-max-priority': 5})
            # Declare the 'status_updates' queue
            self.channel.queue_declare(queue='train_job_status_update', durable=True)
        except pika.exceptions.ChannelClosedByBroker as e:
            print(f"Failed to declare queue: {e}")
            raise

    def enqueue_train_job(self, job_data: 'TrainJobQueue', priority: int):
        job_json = job_data.model_dump_json()
        self.channel.basic_publish(
            exchange='',
            routing_key='jobs',
            body=job_json,
            properties=pika.BasicProperties(
                delivery_mode=2,
                priority=priority
            )
        )

    def enqueue_train_job_status_update(self, run_id: uuid.UUID, status: TrainJobStatus):
        status_update = {
            'run_id': str(run_id),
            'status': status.value
        }
        self.channel.basic_publish(
            exchange='',
            routing_key='train_job_status_update',
            body=json.dumps(status_update),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )

    def consume_jobs(self, callback: Callable):
        self.channel.basic_consume(queue='jobs', on_message_callback=callback)
        while self.is_consuming:
            self.channel.connection.process_data_events(time_limit=1)

        # Assuming you have a logger object
        logger.info("Stop consuming jobs")

    def consume_status_updates(self, callback: Callable):
        self.channel.basic_consume(queue='train_job_status_update', on_message_callback=callback)
        while self.is_consuming:
            self.channel.connection.process_data_events(time_limit=1)

        # Assuming you have a logger object
        logger.info("Stop consuming status updates")

    def acknowledge_job(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)

    def close(self):
        self.is_consuming = False
    



    def dequeue_train_job(self):
        method_frame, header_frame, body = self.channel.basic_get(queue='jobs')
        if method_frame:
            train_job = json.loads(body)
            return method_frame.delivery_tag, train_job
        else:
            return None, None


def get_rabbitmq_client() -> RabbitMQClient:
    
    if settings.env == Environments.LOCAL:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
        return RabbitMQClient(connection)

    else:

        parameters = pika.URLParameters(rabbitmq_settings.url)
        parameters.ssl_options = pika.SSLOptions(context=rabbitmq_settings.ssl_context)
        parameters.heartbeat = 60

        connection = pika.BlockingConnection(parameters)
        return RabbitMQClient(connection) 