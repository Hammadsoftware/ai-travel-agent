from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.database import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =====================================================
# Schemas
# =====================================================

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class SigninRequest(BaseModel):
    email: EmailStr
    password: str


# =====================================================
# SIGNUP
# =====================================================

@router.post("/signup")
def signup(user: SignupRequest):

    try:

        with get_db() as conn:

            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE email = %s
                    """,
                    (user.email,),
                )

                existing_user = cursor.fetchone()

                if existing_user:
                    raise HTTPException(
                        status_code=400,
                        detail="Email already registered",
                    )

                cursor.execute(
                    """
                    INSERT INTO users
                        (name, email, password)
                    VALUES
                        (%s, %s, %s)
                    RETURNING
                        id,
                        name,
                        email,
                        created_at
                    """,
                    (
                        user.name,
                        user.email,
                        user.password,
                    ),
                )

                new_user = cursor.fetchone()

            conn.commit()

        return {
            "message": "Signup successful",
            "user": new_user,
        }

    except HTTPException:
        raise

    except Exception as e:

        print("SIGNUP ERROR:", type(e).__name__, str(e))

        raise HTTPException(
            status_code=500,
            detail="Database error during signup",
        )


# =====================================================
# SIGNIN
# =====================================================

@router.post("/signin")
def signin(user: SigninRequest):

    try:

        with get_db() as conn:

            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        email
                    FROM users
                    WHERE email = %s
                    AND password = %s
                    """,
                    (
                        user.email,
                        user.password,
                    ),
                )

                existing_user = cursor.fetchone()

        if not existing_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        return {
            "message": "Signin successful",
            "user": existing_user,
        }

    except HTTPException:
        raise

    except Exception as e:

        print("SIGNIN ERROR:", type(e).__name__, str(e))

        raise HTTPException(
            status_code=500,
            detail="Database error during signin",
        )