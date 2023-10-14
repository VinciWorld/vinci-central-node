from fastapi import HTTPException
import uuid
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.domains.core.models.user import User
from app.domains.core.schemas.user import UserSchema
from app.domains.train_job.models.train_job import TrainJob
from app.domains.train_job.schemas.train_job import TrainJobCreate, TrainJobSchema


class TrainJobRepository():
    def __init__(self, db_session: Session):
        self.db_session = db_session
    

    def get_most_recent_train_job_by_run_id(self, run_id: uuid.UUID) -> TrainJobSchema:
        model = self.db_session.query(TrainJob)\
            .filter_by(run_id=run_id)\
            .order_by(desc(TrainJob.created_at))\
            .first()

        if not model:
            raise HTTPException(status_code=404, detail=f"No train jobs found for run_id: {run_id}")

        return TrainJobSchema.model_validate(model, from_attributes=True)

    def get_by_run_id(
            self,
            run_id = uuid.UUID
    )-> TrainJobSchema:
        model = self.db_session.query(TrainJob).filter_by(run_id=run_id).first()

        if not model:
            raise HTTPException(status_code=404,
                                 detail=f"Train job with run_id: {run_id} not found.")
        
        return TrainJobSchema.model_validate(model, from_attributes=True)
    
    def get_all(self) -> list[TrainJobSchema] | list:
        models = self.db_session.query(TrainJob).all()

        return [
            TrainJobSchema.model_validate(
                model, from_attributes=True
            ) 
            for model in models
        ]

    def add_train_job(
            self,
            train_job: TrainJobCreate,
            user: UserSchema

            ) -> TrainJobSchema:


        user_db = self.db_session.query(User).filter_by(user_id=user.user_id).first()

        model = TrainJob(
            **train_job.model_dump(),
            created_by_id=user_db.id
            )

        self.db_session.add(model)
        self.db_session.commit()
        self.db_session.refresh(model)

        print(model)

        return TrainJobSchema.model_validate(model, from_attributes=True)


    
    def update_train_job_status(self, run_id: uuid.UUID, status: str) -> TrainJobSchema | None:
        model = self.db_session.query(TrainJob).filter_by(run_id=run_id).first()
        

        if not model:
            return None
        
        model.job_status = status

        self.db_session.commit()
        self.db_session.refresh(model)

        return TrainJobSchema.model_validate(model, from_attributes=True)
    
    def delete_by_run_id(self, run_id: str) -> None:
        train_job = self.db_session.query(TrainJob).filter(TrainJob.run_id == run_id).first()
        
        if train_job:
            self.db_session.delete(train_job)
            self.db_session.commit()