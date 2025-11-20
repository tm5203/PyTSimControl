import logging
import sys
import argparse
import pathlib
import importlib
import threading
import asyncio

from TSimControl.Constant import Constant
from TSimControl.Config import Config
from TSimControl.Status import StatusEnum
from TSimControl.TaskBase import TaskBase
from TSimControl.TaskGeneratorBase import TaskGeneratorBase

class App:

    def __init__(self):
        self._Logger : logging.Logger | None = None
        self._Config : Config
        
        self._WaitingTask : asyncio.Queue | None = None
        self._ConcurrentTaskSemaphore : asyncio.Semaphore | None = None
        
        self._GeneratorList : list = []
                
        self._TaskStatusChanedCondition : threading.Condition = threading.Condition()



    def Main(self, argv : list[str] | None = None):
        '''!
        @startuml
            start

            :BuildLoggingSystem()\nログシステム設定;
            :BuildOperationSetting()\n動作設定構築;
                        
            if (Config.Daemonize) then (yes)
                :Daemonize()\nプロセスデーモン化;
            endif
            :メインループ実行準備;
            group メインループ\nRunTasksk()
                while (IsRemainTasks()\n未実行 or 実行中タスクがある) 
                    :LaunchNewTasks()\n新タスク立ち上げ;
                    :WaitRunningTasks()\n実行中タスクの終了待機;
                end while
                :WaitRemainingTasks()\n実行中の残りタスクの終了待機;
            end group
            
            end
        @enduml
        '''

        self.BuildLoggingSystem()
        self.BuildOperationSetting()
        if self._Config.Daemonize:
            self.Daemonize()
        
        self.Prepare()
        asyncio.run(self.Run())

        return 0
    
    
    
    def Daemonize(self):
        self.Logger.debug('プロセスデーモン化')



    def BuildLoggingSystem(self):
        self.Logger = logging.getLogger(Constant.Name)
        logHandler = logging.StreamHandler(sys.stdout)
        logHandler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logHandler.setLevel(logging.DEBUG)
        self.Logger.addHandler(logHandler)
        self.Logger.setLevel(logging.INFO)



    def BuildOperationSetting(self, argv : list[str] | None = None):
        '''!
        @startuml
            start
            :コマンドラインオプション解釈;
            :設定ファイル読み込み;
            :設定をコマンドラインオプションの指定でオーバーライド;
            end
        @enduml
        '''
        self.Logger.debug('動作設定構築')

        parser = argparse.ArgumentParser(Constant.Name, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('config', type = pathlib.Path, default = pathlib.Path('TSimControl.conf'), help = '設定ファイルパス')
        parser.add_argument('-d', '--daemon', action = 'store_true', help = 'デーモンとして動作させる')
        parser.add_argument('-v', '--verbose', action = 'store_true', help = '動作詳細表示')
        parser.add_argument('-V', '--version', action = 'version', version = Constant.Version, help = 'バージョン表示')
        
        args = parser.parse_args(argv)

        self._Config = Config(args.config)
        
        if args.verbose != Config.DefaultValue['Verbose'][3]:
            self._Config.Verbose = args.verbose
        if args.daemon != Config.DefaultValue['Daemonize'][3]:
            self._Config.Daemonize = args.daemon
        
        self.Logger.setLevel(logging.DEBUG if self._Config.Verbose else logging.INFO)



    def Prepare(self):
        '''!
        @startuml
            start
            :説体で指定されたタスクコレクションモジュールを読み込み;
            :読み込んだタスクコレクションモジュールのクラスのインスタンスを作成;
            end
        @enduml
        '''
        taskCollectionName = self._Config.TaskGenerator.split('.')
        m = importlib.import_module('.'.join(taskCollectionName[:-1]))
        self._TaskGenerator = getattr(m, taskCollectionName[-1])(self._Config.TaskGeneratorArgs)
        self._WaitingTask = asyncio.Queue(self._Config.MaxTasks)
        self._ConcurrentTaskSemaphore = asyncio.Semaphore(self._Config.MaxTasks)



    async def GetTasks(self, taskGenerator):
        self._GeneratorList.append(taskGenerator)

        async for t in taskGenerator:
            if isinstance(t, TaskGeneratorBase):
                asyncio.create_task(self.GetTasks(t))
                await t.PartialDoneEvent.wait()
            if isinstance(t, TaskBase):
                await self._WaitingTask.put(t)
            else:
                await asyncio.sleep(0)
                
        self._GeneratorList.remove(taskGenerator)
        if not self._GeneratorList:
            await self._WaitingTask.join()
            self._WaitingTask.shutdown(True)



    async def RunTasks(self):
        listTask = []
        while True:
            try:
                t = await self._WaitingTask.get()
            except asyncio.QueueShutDown:
                break
            if self._ConcurrentTaskSemaphore.locked() and listTask:
                _, listTask = await asyncio.wait(listTask, return_when = asyncio.FIRST_COMPLETED)
                listTask = list(listTask)
            await self._ConcurrentTaskSemaphore.acquire()
            listTask.append(asyncio.create_task(self.ExecuteProcess(t)))
        if listTask:
            await asyncio.wait(listTask)
        


    async def Run(self):
        taskList = []
        taskList.append(asyncio.create_task(self.GetTasks(self._TaskGenerator)))
        taskList.append(asyncio.create_task(self.RunTasks()))
        await asyncio.wait(taskList)



    async def ExecuteProcess(self, t):
        await t.Run()
        self._ConcurrentTaskSemaphore.release()
        self._WaitingTask.task_done()
    