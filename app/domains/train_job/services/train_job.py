from functools import partial
import json
import logging
import uuid

from fastapi import HTTPException

from app.clients.rabbitmq_client import RabbitMQClient
from app.db.connection import Session, get_db_session
from app.domains.core.schemas.user import UserSchema
from app.domains.train_job.repository.train_job import TrainJobRepository
from app.domains.train_job.schemas.train_job import TrainJobBody, TrainJobCreate, TrainJobQueue, TrainJobSchema
from app.domains.train_job.schemas.train_job_constants import TrainJobStatus, TrainJobType
from app.settings.settings import settings

logger = logging.getLogger(__name__) 


class TrainJobService():
    def __init__(
            self,
            repository: TrainJobRepository
    ):
        
        self.repository = repository


    async def add_train_job(
            self,
            train_job_body: TrainJobBody,
            user: UserSchema,
            rabbitmq_client: RabbitMQClient
    ) -> TrainJobSchema:
           
        run_id = None
        job_type = TrainJobType.CREATE

        train_job_db = self.repository.get_most_recent_train_job_by_user_id(user.id)

        if train_job_db is not None:
            # Each user can only have on job training 
            if is_job_in_initial_statuses(train_job_db):
                return train_job_db

        # 1 - Check if the is a job with the provided run id
        if train_job_body.run_id is not None:
            
            if train_job_db is not None:
                run_id = train_job_db.run_id

                if train_job_db.job_status == TrainJobStatus.SUCCEEDED:
                    logger.info(f"Last Train job is SUCCEEDED! {train_job_db.run_id}")
                    logger.info(f"Preparing to resume {train_job_db.run_id}")
                    job_type = TrainJobType.RESUME
                    
                elif train_job_db.job_status == TrainJobStatus.FAILED:
                    logger.info(f"Last Train job is FAILED! {train_job_db.run_id}")
                    return train_job

                else:
                    logger.info(f"Train job is running: {train_job_db.run_id}")
                    return train_job_db
                
            else:
                raise HTTPException(status_code=404, detail=f"No train jobs found for user: {user.id}")

        else:
        # 2 - Generate a new run id
            run_id = uuid.uuid4()

        train_job_queue = TrainJobQueue(
            run_id=run_id,
            job_type=job_type,
            agent_config=train_job_body.agent_config,
            nn_model_config=train_job_body.nn_model_config,
            env_config=train_job_body.env_config,
            centra_node_id=settings.node_id,
            central_node_url=settings.node_domain # Switch to an env variable
        )

        # 3 - Save Train job on db
        train_job_created = TrainJobCreate(
            **train_job_queue.__dict__,
            job_status=TrainJobStatus.SUBMITTED,
        )
        train_job = self.repository.add_train_job(train_job_created, user)
        logger.info(f"Train job added to db: {train_job_created}")

        # 4 - Add train job to queue
        rabbitmq_client.enqueue_train_job(train_job_queue, 2)
        logger.info(f"Train job added to the queue: {train_job_queue.run_id}")
  
 
     

        return train_job
    
    
    def update_train_jobs_status(
            self,
            rabbitmq_client: RabbitMQClient
    ):
        
        try:
            logger.info("Start consuming train jobs status...")
            rabbitmq_client.consume_status_updates(_update_train_job_status)
        except Exception as e:
            logger.info(f"Rabbitmq stream connection lost: {e}")
  
        logger.info("Waitting for train jobs...")


    def get_train_jobs(self) -> list[TrainJobSchema] | list:
        
        train_jobs = self.repository.get_all()

        return train_jobs


    def delete_train_job(self, run_id: uuid.UUID) -> None:
        self.repository.delete_by_run_id(run_id)


    def get_most_recent_train_job_by_run_id(self, run_id: uuid.UUID) -> TrainJobSchema:
        model = self.repository.get_most_recent_train_job_by_run_id(run_id)

        return TrainJobSchema.model_validate(model)

    

def _update_train_job_status(
        channel,
        method,
        properties,
        body
):
    logger.info(f"callback status")
    body_json = json.loads(body.decode('utf-8'))
    run_id = body_json.get("run_id")
    status = body_json.get("status")
    logger.info(body_json)

    repository = TrainJobRepository(Session())

    logger.info(f"Update train job status run_id: {run_id} - status: {status}")

    model = repository.update_train_job_status(
        uuid.UUID(run_id), status
    )

    if not model:
        logger.info(f"Not Found train job with run_id: {run_id}")
        return
        
    channel.basic_ack(delivery_tag=method.delivery_tag)


def is_job_in_initial_statuses(train_job: TrainJobSchema) -> bool:
    return train_job.job_status in {
        TrainJobStatus.SUBMITTED, 
        TrainJobStatus.LAUNCHED, 
        TrainJobStatus.STARTING
    }