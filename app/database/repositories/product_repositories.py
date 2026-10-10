import csv
from decimal import Decimal, InvalidOperation
from uuid import UUID
from psycopg2.extras import execute_values

from app.database.connection import (
    get_db_connection,
    release_db_connection,
    init_db_pool,
)


REQUIRED_COLUMNS = {"category", "name", "price"}

# CSV header (lowercase)  ->  product table column
CSV_COLUMN_MAP = {
    "product category": "category",
    "product subcategory": "sub_category",
    "product name": "name",
    "product price": "price",
    "product rating": "rating",
    "total ratings": "total_rating",
    "product image": "image_url",
}


def _parse_product_row(row: dict, row_number: int) -> tuple:
    """Validate and convert one CSV row into a tuple for insertion."""

    category = (row.get("category") or "").strip()
    sub_category = (row.get("sub_category") or "").strip() or None
    name = (row.get("name") or "").strip()
    image_url = (row.get("image_url") or "").strip() or None

    if not category:
        raise ValueError(f"Row {row_number}: 'category' is required.")

    if not name:
        raise ValueError(f"Row {row_number}: 'name' is required.")

    # rating (0 - 5), defaults to 0
    raw_rating = (row.get("rating") or "").strip()
    try:
        rating = Decimal(raw_rating) if raw_rating else Decimal("0")
    except InvalidOperation:
        raise ValueError(f"Row {row_number}: invalid rating '{raw_rating}'.")

    if not (0 <= rating <= 5):
        raise ValueError(f"Row {row_number}: rating must be between 0 and 5.")

    # total_rating, defaults to 0
    raw_total = (row.get("total_rating") or "").strip().replace(",", "")
    try:
        total_rating = int(float(raw_total)) if raw_total else 0
    except ValueError:
        raise ValueError(
            f"Row {row_number}: invalid total_rating '{raw_total}'."
        )

    if total_rating < 0:
        raise ValueError(f"Row {row_number}: total_rating cannot be negative.")

    # price, strips currency symbols and thousand separators
    raw_price = (
        (row.get("price") or "")
        .strip()
        .replace(",", "")
        .replace("₹", "")
        .replace("$", "")
    )
    try:
        price = Decimal(raw_price)
    except InvalidOperation:
        raise ValueError(f"Row {row_number}: invalid price '{raw_price}'.")

    if price < 0:
        raise ValueError(f"Row {row_number}: price cannot be negative.")

    return (
        category,
        sub_category,
        name,
        image_url,
        rating,
        total_rating,
        price,
    )


def store_products_from_csv(
    csv_file_path: str,
    batch_size: int = 1000,
):
    """
    Read a CSV file and bulk insert its rows into the product table.

    Expected CSV headers:
        Product Category, Product Subcategory, Product Name, Product Price,
        Product Rating, Total Ratings, Product Image

    Required: Product Category, Product Name, Product Price
    Returns the list of inserted products.
    """
    conn = cur = None

    try:
        # ---------- READ + VALIDATE CSV ----------
        with open(csv_file_path, mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames:
                raise ValueError("CSV file is empty or has no header row.")

            # map CSV headers to DB column names:
            # "Product Subcategory" -> "sub_category"
            reader.fieldnames = [
                CSV_COLUMN_MAP.get(h.strip().lower(), h.strip().lower())
                for h in reader.fieldnames
            ]

            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(
                    f"CSV is missing required columns: {', '.join(sorted(missing))}"
                )

            values = [
                _parse_product_row(row, row_number)
                for row_number, row in enumerate(reader, start=2)
            ]

        if not values:
            raise ValueError("CSV file has no product rows.")

        # ---------- BULK INSERT ----------
        conn, cur = get_db_connection()

        query = """
            INSERT INTO product (
                category,
                sub_category,
                name,
                image_url,
                rating,
                total_rating,
                price
            )
            VALUES %s
            RETURNING
                product_id,
                category,
                sub_category,
                name,
                image_url,
                rating,
                total_rating,
                price,
                created_at,
                updated_at
        """

        inserted_products = []
        columns = None

        for start in range(0, len(values), batch_size):
            batch = values[start:start + batch_size]

            inserted_products.extend(
                execute_values(
                    cur,
                    query,
                    batch,
                    template="(%s, %s, %s, %s, %s, %s, %s)",
                    fetch=True,
                )
            )

            if columns is None:
                columns = [desc[0] for desc in cur.description]

        conn.commit()

        return [
            dict(zip(columns, product))
            for product in inserted_products
        ]

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(
            f"Failed to store products from CSV: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def create_product(
    category: str,
    name: str,
    price: Decimal | float,
    sub_category: str | None = None,
    image_url: str | None = None,
    rating: Decimal | float = 0,
    total_rating: int = 0,
) -> dict:
    """
    Create a new product in the database.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            INSERT INTO product (
                category,
                sub_category,
                name,
                image_url,
                rating,
                total_rating,
                price
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING
                product_id,
                category,
                sub_category,
                name,
                image_url,
                rating,
                total_rating,
                price,
                created_at,
                updated_at
            """,
            (
                category,
                sub_category,
                name,
                image_url,
                Decimal(str(rating)),
                total_rating,
                Decimal(str(price)),
            ),
        )

        product = cur.fetchone()
        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, product))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to create product: {e}")

    finally:
        release_db_connection(conn, cur)


def get_product_by_id(product_id: UUID) -> dict | None:
    """
    Fetch a product by its product_id.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                product_id,
                category,
                sub_category,
                name,
                image_url,
                rating,
                total_rating,
                price,
                created_at,
                updated_at
            FROM product
            WHERE product_id = %s
            """,
            (str(product_id),),
        )

        product = cur.fetchone()

        if not product:
            return None

        columns = [desc[0] for desc in cur.description]

        return dict(zip(columns, product))

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(f"Failed to fetch product: {e}")

    finally:
        release_db_connection(conn, cur)


def get_all_products(limit: int = 100, offset: int = 0) -> list[dict]:
    """
    Fetch all products with pagination.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                product_id,
                category,
                sub_category,
                name,
                image_url,
                rating,
                total_rating,
                price,
                created_at,
                updated_at
            FROM product
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )

        products = cur.fetchall()

        if not products:
            return []

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, product))
            for product in products
        ]

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(f"Failed to fetch products: {e}")

    finally:
        release_db_connection(conn, cur)


def get_products_by_category(category: str, limit: int = 100, offset: int = 0) -> list[dict]:
    """
    Fetch products by category (case-insensitive) with pagination.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                product_id,
                category,
                sub_category,
                name,
                image_url,
                rating,
                total_rating,
                price,
                created_at,
                updated_at
            FROM product
            WHERE LOWER(category) = LOWER(%s)
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            (category, limit, offset),
        )

        products = cur.fetchall()

        if not products:
            return []

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, product))
            for product in products
        ]

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(f"Failed to fetch products by category: {e}")

    finally:
        release_db_connection(conn, cur)


def update_product_by_id(product_id: UUID, **fields) -> dict | None:
    """
    Update product fields by product_id.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        allowed_fields = {
            "category": lambda v: v,
            "sub_category": lambda v: v,
            "name": lambda v: v,
            "image_url": lambda v: v,
            "rating": lambda v: Decimal(str(v)),
            "total_rating": lambda v: int(v),
            "price": lambda v: Decimal(str(v)),
        }

        set_clauses = []
        values = []

        for key, val in fields.items():
            if key in allowed_fields and val is not None:
                set_clauses.append(f"{key} = %s")
                values.append(allowed_fields[key](val))

        if not set_clauses:
            return get_product_by_id(product_id)

        values.append(str(product_id))

        query = f"""
            UPDATE product
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE product_id = %s
            RETURNING
                product_id,
                category,
                sub_category,
                name,
                image_url,
                rating,
                total_rating,
                price,
                created_at,
                updated_at
        """

        cur.execute(query, tuple(values))

        product = cur.fetchone()

        if not product:
            return None

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, product))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update product: {e}")

    finally:
        release_db_connection(conn, cur)


def delete_product_by_id(product_id: UUID) -> dict | None:
    """
    Delete product by product_id.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            DELETE FROM product
            WHERE product_id = %s
            RETURNING product_id
            """,
            (str(product_id),),
        )

        result = cur.fetchone()

        if not result:
            return None

        conn.commit()

        return {
            "product_id": result[0],
            "message": "Product deleted successfully",
        }

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete product: {e}")

    finally:
        release_db_connection(conn, cur)


if __name__ == "__main__":
    init_db_pool()

    products = store_products_from_csv("product_data.csv")

    print(f"Inserted {len(products)} products")