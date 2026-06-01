from sqlalchemy.orm import Session

from backend.database.models import User


def get_user_by_email(
    email: str,
    db: Session
):

    return db.query(User).filter(
        User.email == email
    ).first()