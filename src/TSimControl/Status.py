import enum
import threading

class StatusEnum(enum.Enum):
    Idle = enum.auto()
    PreOperation = enum.auto()
    Operation = enum.auto()
    PostOperation = enum.auto()
    Finished = enum.auto()
    Error = enum.auto()

class Status:
    
    def __init__(self):
        self._Status : StatusEnum = StatusEnum.Idle
        self.Condition : threading.Condition | None = None 
        
    @property
    def Status(self) -> StatusEnum:
        return self._Status

    @Status.setter
    def Status(self, status : StatusEnum):
        if self.Condition is not None:
            self.Condition.acquire()
        
        self._Status = status
        
        if self.Condition is not None:
            if self._Status in (StatusEnum.Finished, StatusEnum.Error):
                self.Condition.notify_all()
            self.Condition.release()
        