import enum


class TrainJobStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    LAUNCHED = "LAUNCHED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class TrainJobType(str, enum.Enum):

    CREATE = "CREATE"
    RESUME = "RESUME"

