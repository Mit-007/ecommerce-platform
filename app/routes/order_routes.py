from fastapi import APIRouter
from uuid import UUID
from app.database.repositories.order_repositories import create_new_order,get_order_by_id,update_order_status_by_id,delete_order_by_id,list_products_by_id,tracking_order_by_id
from app.database.repositories.product_items_repositories import create_order_products_bulk
from app.core.logger import logger
from app.model.order_routes_schema import CreateOrder
from fastapi import APIRouter, HTTPException
from app.database.repositories.tracking_repositories import create_tracking_event

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/")
def create_order(data : CreateOrder):
    try:
        order_data = create_new_order(data.customer_id,data.invoice_id,data.status,data.estimated_delivery_date)

        order_id = order_data["order_id"] 

        product_data = create_order_products_bulk(order_id,data.product_list,data.returnable)

        return {
            "order_details": order_data,
            "products_item_details" :product_data
        }
    
    except Exception as e:
        print(e)
        return {
            "message" : "not craete new order !!"
        }

    
@router.get("/{order_id}")
def get_order(order_id):
    try:
        order_data = get_order_by_id(order_id)
        return order_data
    
    except Exception as e:
        print(e)
        return {
            "message" : "not get order !!"
        }

@router.put("/{order_id}")
def update_order_status(order_id,new_status):
    try:
        result = update_order_status_by_id(order_id,new_status)
        return result 
    except Exception as e:
        print(e)
        return {
            "message" : "not update order !!"
        }
    

@router.delete("/{order_id}")
def delete_order(order_id:UUID):
    try:
        result = delete_order_by_id(order_id)

        return result
    except Exception as e:
        print(e)
        return {
            "message" : "not delete order !!"
        }


@router.get("/{order_id}/items")
def list_order_products(order_id: UUID):
    try:
        product_list = list_products_by_id(order_id)
        return product_list
    
    except Exception as e:
        print(e)
        return {
            "message" : "not list products !!"
        }   

    
