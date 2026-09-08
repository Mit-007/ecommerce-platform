from fastapi import APIRouter
from app.database.repositories.user_repositories import create_new_customer,fetch_password_by_email
from app.utils.jwt import create_access_token,create_refresh_token,refresh_access_token
from app.services.hashing import verify_password 
from app.model.auth_routes_schema import RefreshTokenRequest

router = APIRouter(prefix="", tags=["auth"])


@router.post("/auth/register")
def register_new_custmer(name,email,password):
    try:
        new_customer = create_new_customer(name,email,password)
        return new_customer
    except Exception as e:
        print(e)
        return {
            "message" : "not crate user !!"
        }

@router.post("/auth/login")
def login_user(email,password):
    try:
        customer_data = fetch_password_by_email(email)
    
        if verify_password(password,customer_data['password']):
            data = {"sub":customer_data['customer_id']}
            return {
                "message":"you are login sucessfully !!",
                "access_token" : create_access_token(data),
                "refresh_token" : create_refresh_token(data)
            }
        else :
            return {
                "message":"password Incorrect , please try again !!"
            }

    except Exception as e:
        print(e)
        return {
            "message" : "error !!"
        }

@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest):

    new_access_token = refresh_access_token(
        request.refresh_token
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }