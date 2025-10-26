import collections.abc
import asyncio

from TSimControl.TaskBase import TaskBase

class TaskGeneratorBase:

    def __init__(self):
        self.TaskList : collections.abc.Iterable = ()
        self.PartialDoneEvent : asyncio.Event = asyncio.Event()
        self.AllDependentDoneEvent : asyncio.Event = asyncio.Event()
        
        self._CounterLock : asyncio.Lock = asyncio.Lock()
        self._CountOfDependent : int = 0

    async def __aiter__(self) -> TaskBase:
        for t in self.TaskList:
            yield t
        self.PartialDoneEvent.set()
        
    def DependentDone(self):
        self._CountOfDependent -= 1
        if self._CountOfDependent <= 0:
            self.AllDependentDoneEvent.set()
        