import enum


class StreamMessagesId(str, enum.Enum):
    TRAIN_NODE_STREAM = 1
    TRAIN_NODE_STATE = 2

class TrainNodeStateEnum(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "CONNECTED"