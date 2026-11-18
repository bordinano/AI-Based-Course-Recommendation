from sqlalchemy.orm import Session

from app.models.interest import Interest


def get_all_interests(db: Session) -> list[Interest]:
    """Retrieve all interests ordered by name."""
    return db.query(Interest).order_by(Interest.name).all()