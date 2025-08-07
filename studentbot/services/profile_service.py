from studentbot.utils.db import get_db, User
from sqlalchemy.orm import Session
from studentbot.utils.gsheets import delete_row_by_user_id

def create_profile(user_id: int, profile_data: dict) -> User:
    db: Session = next(get_db())
    user = User(
        user_id=user_id,
        first_name=profile_data["profile_name"],
        family_name=profile_data["profile_family_name"],
        age=profile_data["profile_age"],
        email=profile_data["profile_email"],
        field_of_study=profile_data["profile_field_of_study"],
        country=profile_data["profile_country"],
    )
    db.add(user)
    db.commit()
    return user

def delete_profile(user_id: int):
    # Delete from PostgreSQL
    db: Session = next(get_db())
    user = db.query(User).filter_by(user_id=user_id).first()
    if user:
        db.delete(user)
        db.commit()

    # Delete from Google Sheets
    delete_row_by_user_id("StudentBotQuestions", user_id)
