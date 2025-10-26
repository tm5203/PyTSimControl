import random
import collections.abc
import pathlib

from TSimControl.TaskGeneratorBase import TaskGeneratorBase
from TSimControl.example.Task import Task
from TSimControl.TaskBase import TaskBase

class TaskGenerator(TaskGeneratorBase):
    def __init__(self):
        super().__init__()
        self._NumberOfTasks : int = 4
        
    async def __aiter__(self) -> collections.abc.AsyncGenerator[TaskBase | TaskGeneratorBase]:
        for c in range(self._NumberOfTasks):
            t = TaskGenerator2()
            t.ID = 'TaskGen2-{}'.format(c)
            yield t
        self.PartialDoneEvent.set()
        
class TaskGenerator2(TaskGeneratorBase):
    def __init__(self):
        super().__init__()
        self._NumberOfTasks : int = 4
        
    async def __aiter__(self) -> collections.abc.AsyncGenerator[TaskBase]:
        filePath = pathlib.Path(__file__).parent
        for c in range(self._NumberOfTasks):
            self._CountOfDependent += 1
            t = Task(('python', str(filePath.absolute() / 't2.py'), str(random.randint(5, 10)), self.ID, str(self._CountOfDependent)))
            t.Generator = self
            yield t
        self.PartialDoneEvent.set()
        
        await self.AllDependentDoneEvent.wait()
        yield Task(('python', str(filePath.absolute() / 't1.py'), str(random.randint(5, 10)), self.ID))
        
            