from fastapi import APIRouter
from uuid import UUID
from app.database.repositories.customer_repositories import update_customer_password,delete_customer_by_id,get_customer_by_id
from app.core.logger import logger
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/customer", tags=["customer"])


@router.get("/{customer_id}")
def get_customer(customer_id):
    try:
        customer_data = get_customer_by_id(customer_id)
        return customer_data
    
    except Exception as e:
        print(e)
        return {
            "message" : "not get user !!"
        }

@router.put("/{customer_id}")
def change_customer_password(customer_id,new_password):
    try:
        result = update_customer_password(customer_id,new_password)
        return result 
    except Exception as e:
        print(e)
        return {
            "message" : "not update user !!"
        }
    

@router.delete("/{customer_id}")
def delete_customer(customer_id):
    try:
        result = delete_customer_by_id(customer_id)

        return result
    except Exception as e:
        print(e)
        return {
            "message" : "not update user !!"
        }