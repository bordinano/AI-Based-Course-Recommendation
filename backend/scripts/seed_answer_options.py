from sqlalchemy import select

from app.database import SessionLocal
from app.models import AnswerOption


ANSWER_OPTIONS = [
    {"label": "Strongly Disagree", "score": 1},
    {"label": "Disagree", "score": 2},
    {"label": "Neutral", "score": 3},
    {"label": "Agree", "score": 4},
    {"label": "Strongly Agree", "score": 5},
]


def seed_answer_options():
    with SessionLocal.begin() as db:
        existing_options = db.scalars(
            select(AnswerOption)
        ).all()

        existing_by_label = {
            option.label: option.score
            for option in existing_options
        }

        existing_by_score = {
            option.score: option.label
            for option in existing_options
        }

        for option in ANSWER_OPTIONS:
            label = option["label"]
            score = option["score"]

            if label in existing_by_label:
                if existing_by_label[label] != score:
                    raise ValueError(
                        f"Incorrect score for {label}"
                    )
                continue

            if score in existing_by_score:
                raise ValueError(
                    f"Score {score} is already assigned to "
                    f"{existing_by_score[score]}"
                )

            db.add(AnswerOption(**option))

        print("Answer options seeded successfully.")


if __name__ == "__main__":
    seed_answer_options()