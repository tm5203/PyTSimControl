import asyncio

from TSimControl.TaskBase import TaskBase
from TSimControl.Status import StatusEnum


class Task(TaskBase):
    
    def __init__(self, operation : tuple[str]):
        super().__init__()
        self._Operation = operation
        
    def PreOperation(self):
        self.Status = StatusEnum.PreOperation
    
    async def Operation(self):
        self.Status = StatusEnum.Operation
        p = await asyncio.create_subprocess_exec(*self._Operation)
        await p.wait()
    
    def PostOperation(self):
        self.Status = StatusEnum.PostOperation
        self.Status = StatusEnum.Finished

