import logging
import pathlib
import xml.etree.ElementTree
import typing

from TSimControl.Constant import Constant

class Config:
    
    DefaultValue : dict[str, tuple[str, typing.Any, typing.Any, typing.Any]] = {
        'Verbose' : ('./Verbose', lambda x: x.capitalize() == 'True', True, False),
        'Daemonize' : ('./Daemonize', lambda x: x.capitalize() == 'True', True, False),
        'TaskGenerator' : ('./TaskGenerator', str, False, 'TaskGenerator.TaskGenerator'),
        'MaxTasks' : ('./MaxTasks', int, False, 3)
        }

    def __init__(self, configPath : pathlib.Path | str):
        
        self.Logger : logging.Logger = logging.getLogger(Constant.Name) 
        self._ConfigPath : pathlib.Path | None = None

        self._Content : xml.etree.ElementTree.ElementTree | None = None
        self._Config : dict[str, typing.Any] = {}
        for k in Config.DefaultValue:
            self._Config[k] = None

        self.Load(configPath)
        
    def Load(self, configPath : pathlib.Path | str):
        if isinstance(configPath, str):
            configPath = pathlib.Path(configPath)
            
        if not configPath.is_file():
            self.Logger.critical('設定ファイル[%s]が見つかりません', str(configPath))
        self._Content = xml.etree.ElementTree.parse(configPath)
        self._ConfigPath = configPath
    
    @staticmethod
    def _Get(name : str) -> typing.Any:
        def wrapper(self):
            if self._Config[name] is None:
                dValue = Config.DefaultValue[name]
                if isinstance(dValue[2], list):
                    x = self._Content.findall(dValue[0])
                    if x:
                        self._Config[name] = [dValue[1](y.text) for y in x]
                    else:
                        self._Config[name] = list(dValue[3])
                else:
                    x = self._Content.find(dValue[0])
                    if x is not None:
                        self._Config[name] = dValue[1](x.text)
                    else:
                        self._Config[name] = dValue[3]
                    
            return self._Config[name]
        
        return wrapper
    
    @staticmethod
    def _Set(name : str):
        def wrapper(self, value : typing.Any):
            self._Config[name] = value
            
        return wrapper
    
for k, v in Config.DefaultValue.items():
    setattr(Config, k, property(Config._Get(k), Config._Set(k)))
