import socket
from datetime import datetime
import logging
import boto3

class CloudWatchLogHandler(logging.Handler):
    def __init__(self, log_group, stream_name):
        logging.Handler.__init__(self)
        self.log_group = log_group
        self.stream_name = stream_name
        self.logs_client = boto3.client('logs', region_name="eu-central-1")
        self.sequence_token = None
        # Ensure the current log stream exists before sending logs
        self.ensure_log_stream_exists()

    def ensure_log_stream_exists(self):
        try:
            logging.info(
                "[CloudWatchLogHandler] - creating log stream with name: %s", self.stream_name)
            self.logs_client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.stream_name
            )
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            logging.info("[CloudWatchLogHandler] - log stream already exists")
            pass

    def emit(self, record):
        log_entry = self.format(record)
        try:
            if self.sequence_token:
                response = self.logs_client.put_log_events(
                    logGroupName=self.log_group,
                    logStreamName=self.stream_name,
                    logEvents=[
                        {'timestamp': int(record.created * 1000), 'message': log_entry}],
                    sequenceToken=self.sequence_token
                )
            else:
                response = self.logs_client.put_log_events(
                    logGroupName=self.log_group,
                    logStreamName=self.stream_name,
                    logEvents=[
                        {'timestamp': int(record.created * 1000), 'message': log_entry}]
                )
            self.sequence_token = response['nextSequenceToken']
        except Exception as e:
            print(f"Failed to send log to CloudWatch: {e}")


def setup_cloudwatch_logging(log_group):
    hostname = socket.gethostname()
    current_date = datetime.now().strftime('%Y-%m-%d')
    runner_id = "runnerX?"
    stream_name = f"{hostname}_{current_date}"

    # Setting up logging with CloudWatch integration
    ch = CloudWatchLogHandler(
        log_group=log_group, stream_name=stream_name)
    
    formatter = logging.Formatter(
        '%(name)s - %(levelname)s - %(funcName)s - %(message)s')
    ch.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    # root_logger.setLevel(logging.INFO)
    root_logger.addHandler(ch)
    
    # uicheckapp_logger = logging.getLogger('uicheckapp')
    # uicheckapp_logger.setLevel(logging.INFO)
    # uicheckapp_logger.addHandler(ch)