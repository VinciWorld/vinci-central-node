from fastapi import FastAPI
import logging


logging.config.fileConfig('logging.conf', disable_existing_loggers=False)  #type: ignore


app = FastAPI()