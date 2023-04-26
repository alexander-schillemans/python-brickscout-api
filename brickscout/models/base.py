from typing import Union, Optional
from types import SimpleNamespace

def construct_from_data(data: Union[dict, list]) -> 'BaseModel':
    """ Construct an object from the given data. """
    
    if isinstance(data, list):
        object = ObjectListModel()
        
        for item in data:
            if isinstance(item, dict) or isinstance(item, list):
                sub_object = construct_from_data(item)
                object.add(sub_object)
            else:
                object.add(item)
        
    elif isinstance(data, dict):
        object = BaseModel()
    
        for key, value in data.items():
            if isinstance(value, dict) or isinstance(value, list):
                sub_object = construct_from_data(value)
                setattr(object, key, sub_object)
            else:   
                setattr(object, key, value)
    else:
        raise TypeError(f'Cannot construct object from data of type {type(data)}')
    
    return object

class BaseModel:
    
    def __init__(self) -> None:
        self.has_error = False
        self.error = None
    
    def construct_from_response(self, resp_data: dict) -> 'BaseModel':
        """ Construct an object from the returned response data. """
        
        self = construct_from_data(resp_data)
        return self
    
    def set_error_from_response(self, response: dict) -> 'BaseModel':
        return self.set_error(
            response['type'],
            response['exceptionCode'],
            response['developerMessage'],
            response['moreInfoUrl'],
            response['timeStamp']
        )
    
    def set_error(self,
        type: str,
        exception_code: str,
        developer_message: str,
        more_info_url: str,
        timestamp: str          
        ) -> 'BaseModel':
        
        """ Sets the error flag to True and assigns the status code to it. """
        from .errors import Error
        self.has_error = True
        self.error = Error(
            type=type,
            exception_code=exception_code,
            developer_message=developer_message,
            more_info_url=more_info_url,
            timestamp=timestamp
        )
        
        return self
    
    def __getattr__(self, name: str) -> None:
        """ Gets called when an attribute is not found. Always returns None."""
        return None

class ObjectListModel(BaseModel):
    
    def __init__(self, list: Optional[list] = None) -> None:
        super().__init__()
        self.list = list if list else []

    def add(self, item: object) -> list:
        self.list.append(item)
        return self.list
    
    def remove(self, item: object) -> list:
        self.list.remove(item)
        return self.list
    
    def iterator(self) -> list:
        return self.list