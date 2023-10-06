import asyncio
import json
import logging

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, WebSocket
from app.clients.s3.interface import S3ClientInterface
from app.clients.s3.s3_client import get_s3_client
from app.db.connection import get_db_session
from app.domains.train_job.repository.train_job import TrainJobRepository
from app.domains.train_job.schemas.train_job_constants import TrainJobStatus
from app.domains.train_stream.utils.websocket_manager import websocket_manager

logger = logging.getLogger(__name__) 

train_stream_router = APIRouter(
    prefix='/ws/v1',
    tags=["Train Stream"]
)



@train_stream_router.websocket("/client-stream")
async def ws_client_stream(
        ws_client: WebSocket,
        db_session: Session = Depends(get_db_session),
        s3_client: S3ClientInterface = Depends(get_s3_client)
    ):
    logger.info(f"New client: {ws_client.client.host}:{ws_client.client.port}")
    await ws_client.accept()
    logger.info(f"Accepted")

    trainJobRespository = TrainJobRepository(db_session)

    try:
        data = await ws_client.receive_text()
        run_id = json.loads(data)["run_id"]
        logger.info(f"Run_id: {run_id}")

        websocket_manager.add(run_id, ws_client)
        logger.info(f"ws_clinet: {websocket_manager.get_by_id(run_id)}")

        train_job_status = TrainJobStatus.SUBMITTED
        while train_job_status != TrainJobStatus.SUCCEEDED and train_job_status != TrainJobStatus.FAILED:
            train_job = trainJobRespository.get_by_run_id(run_id)
            train_job_status = train_job.job_status

            await ws_client.send_text(json.dumps(
            {
                "msg_id":2,
                "run_id":run_id,
                "status":train_job.job_status.value
            }))

            if train_job_status == TrainJobStatus.SUCCEEDED:
                break
            
            await asyncio.sleep(2)

        nn_model = s3_client.get_nn_model(run_id)
        await ws_client.send_bytes(nn_model)
    
    
    except Exception as e:
        logger.info(f"ERROR: {e}")
    finally:
        try:
           await websocket_manager.remove(run_id)
        except Exception as e:
            logger.error(f"Error unity client WebSocket: {e}")

    logger.info(f"Ws closed  STATE: {ws_client.application_state}")

@train_stream_router.websocket("/train-node-stream")
async def ws_train_node_stream(ws_node: WebSocket):
    await ws_node.accept()

    run_id = None
    ws_client = None
    try:
        data = await ws_node.receive_text()
        logger.info(data)
        run_id = json.loads(data)["run_id"]

        logger.info(f"WebSocket train-node-stream run_id: {run_id}")

        while True:
            data = await ws_node.receive_text()
            ws_client = websocket_manager.get_by_id(run_id)
          
            if data and ws_client:
                #train_node_data = TrainNodeDataStream(
                #    msg_id=StreamMessagesId.TRAIN_NODE_STREAM,
                #    data=data
                #)
                
                await ws_client.send_text(data)


    except Exception as e:
        logger.error(f"Error in WebSocket train-node-stream: {e}")
    finally:
        logger.info(f"Removed from websocket  manager")
        try:
            await ws_node.close()
            logger.info(f"Closed")
        except Exception as e:
            logger.error(f"Error closing train Node WebSocket: {e}")
