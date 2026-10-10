from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
from app.database.repositories.product_repositories import (
    create_product,
    get_product_by_id,
    get_all_products,
    get_products_by_category,
    get_all_categories,
    get_subcategories_by_category,
    update_product_by_id,
    delete_product_by_id,
)
from app.core.logger import logger
from app.model.product_routes_schema import (
    CreateProduct,
    UpdateProduct,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/")
def add_product(request: CreateProduct):
    """
    Create a new product.
    """
    try:
        product_data = create_product(
            category=request.category,
            name=request.name,
            price=request.price,
            sub_category=request.sub_category,
            image_url=request.image_url,
            rating=request.rating,
            total_rating=request.total_rating,
        )

        if product_data is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to create product.",
            )

        return product_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except ValueError as e:
        logger.error(f"Validation error while adding product: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while adding product: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/")
def list_all_products(
    limit: int = Query(100, ge=1, le=1000, description="Max products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
):
    """
    Get all products with pagination.
    """
    try:
        products = get_all_products(limit=limit, offset=offset)
        return products

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while fetching all products: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/categories")
def list_categories():
    """
    Get list of all product categories.
    """
    try:
        categories = get_all_categories()
        return categories

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while fetching categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/categories/{category}/subcategories")
@router.get("/category/{category}/subcategories")
def list_subcategories_by_category(category: str):
    """
    Get list of all subcategories for a given category.
    """
    try:
        subcategories = get_subcategories_by_category(category)
        return subcategories

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while fetching subcategories for category '{category}': {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/category/{category}")
def list_products_by_category(
    category: str,
    limit: int = Query(100, ge=1, le=1000, description="Max products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
):
    """
    Get category wise products.
    """
    try:
        products = get_products_by_category(
            category=category,
            limit=limit,
            offset=offset,
        )
        return products

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while fetching category products: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/{product_id}")
def get_product(product_id: UUID):
    """
    Get product by ID.
    """
    try:
        product_data = get_product_by_id(product_id)

        if product_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found.",
            )

        return product_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while fetching product: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.put("/{product_id}")
def update_product(product_id: UUID, request: UpdateProduct):
    """
    Update product details by product ID.
    """
    try:
        existing_product = get_product_by_id(product_id)
        if existing_product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found.",
            )

        update_dict = request.model_dump(exclude_unset=True)
        result = update_product_by_id(product_id, **update_dict)

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to update product.",
            )

        return result

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while updating product: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/{product_id}")
def delete_product(product_id: UUID):
    """
    Delete product by product ID.
    """
    try:
        existing_product = get_product_by_id(product_id)
        if existing_product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found.",
            )

        result = delete_product_by_id(product_id)

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete product.",
            )

        return result

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while deleting product: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
