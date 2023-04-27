from typing import Optional

from brickscout.models.base import ObjectListModel, BaseModel
from .base import APIEndpoint
from brickscout.utils import construct_url_with_filter
from brickscout.models.utils import construct_object_from_data, construct_error_from_data

class OrdersEndpoint(APIEndpoint):
    
    def __init__(self, api: object) -> None:
        endpoint = f'shops/{api._username}/orders'
        super().__init__(api, endpoint)
        
    def list(self, filter: Optional[dict] = None) -> ObjectListModel:
        """ Returns a list of orders. 
        :param filter: a dictionary of filters to apply to the list.
        :type filter: Optional[dict]
        :return: a list of orders.
        :rtype: ObjectListModel
        """
        
        url = construct_url_with_filter(self.endpoint, filter) if filter else self.endpoint
        status, headers, resp_json = self.api.get(url)
        if status > 299: return construct_error_from_data(resp_json)
        
        return construct_object_from_data(resp_json['representations'])
    
    def get(self, id: str) -> BaseModel:
        """ Returns the order with the given id. 
        :param id: the id of the order to get.
        :type id: str
        :return: the order with the given id.
        :rtype: BaseModel
        """
        
        status, headers, resp_json = self.api.get(f'{self.endpoint}/{id}')
        if status > 299: return construct_error_from_data(resp_json)
        
        return construct_object_from_data(resp_json)
    
    def get_open_orders(self) -> ObjectListModel:
        """ Returns a list of open orders. An order is considered open if it has not been deleted and has not been shipped. """
        
        filter = {
            'order.deleted' : 'isNull',
            'order.shipped' : 'isFalse'
        }
        
        orders = self.list(filter)
        
        # Orders that have no payment are not considered open
        # The API does not allow us to filter on the payment status
        # So we have to filter them out manually
        list_model = ObjectListModel()
        list_model.list = [order for order in orders.iterator() if order.payment]

        return list_model