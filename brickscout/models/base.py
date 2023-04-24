from typing import Union, Optional
from types import SimpleNamespace

class BaseModel:
    
    def __init__(self) -> None:
        self.has_error = False
        self.error = None
    
    def construct_from_response(self, resp_data: dict) -> 'BaseModel':
        """ Construct an object from the returned response data. """
        
        for key, value in resp_data.items():
            if isinstance(value, dict):
                sub_object = self.construct_from_response(value)
                setattr(self, key, sub_object)
            else:
                setattr(self, key, value)
        
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
    
    def construct_from_response(self, json: Union[dict, list]) -> 'ObjectListModel':
        """ Construct a list of objects from the returned response data. """
        
        if isinstance(json, dict):
            item_obj = BaseModel().construct_from_response(json)
            self.add(item_obj)
        elif isinstance(json, list):
            for item in json:
                item_obj = BaseModel().construct_from_response(item)
                self.add(item_obj)

        return self
    
    def items(self) -> list:
        return self.list