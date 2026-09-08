from app.database.connection import get_db_connection,release_db_connection
from app.services.hashing import hash_password

def create_new_customer(name: str, email: str, password: str):
    conn = cur = None
    try:
        conn, cur = get_db_connection()

        hased_password = hash_password(password)
        
        cur.execute(
            """
            INSERT INTO customer (name, email, password)
            VALUES (%s, %s, %s)
            RETURNING customer_id, name, email, created_at
            """,
            (name, email, hased_password)
        )

        created_customer = cur.fetchone()
        conn.commit()
        return created_customer

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to create customer: {e}")

    finally:
        release_db_connection(conn, cur)

def fetch_password_by_email(email: str):
    conn = cur = None
    try:
        conn, cur = get_db_connection()
        
        cur.execute(
            """
            SELECT customer_id,password FROM customer WHERE email = %s
            """,
            (email,)
        )

        result = cur.fetchone()
        
        if not result:
            raise Exception(f"Customer with email '{email}' not found")
        
        return {
            "customer_id": result[0],
            "password": result[1],
        }

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(f"Failed to fetch password: {e}")

    finally:
        release_db_connection(conn, cur)