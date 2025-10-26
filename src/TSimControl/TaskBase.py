from TSimControl.Status import Status as TSimStatus, StatusEnum

class TaskBase:
    
    def __init__(self):
        self._Status = TSimStatus()
        self.Generator : 'TaskGeneratorBase' = None
    
    @property
    def Status(self) -> StatusEnum:
        return self._Status.Status
    
    @Status.setter
    def Status(self, status : StatusEnum):
        self._Status.Status = status
        
    async def Run(self):
        try:
            self.PreOperation()
            await self.Operation()
            self.PostOperation()
        except Exception as e:
            self.Status = StatusEnum.Error
        finally:
            self.Done()

    def PreOperation(self):
        pass
    
    async def Operation(self):
        pass
    
    def PostOperation(self):
        pass
        
    def Done(self):
        if self.Generator:
            self.Generator.DependentDone()
