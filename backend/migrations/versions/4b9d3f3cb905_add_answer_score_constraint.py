"""add answer score constraint

Revision ID: 4b9d3f3cb905
Revises: c73e6c5427ff
Create Date: 2026-11-18 03:11:11.387025

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4b9d3f3cb905"
down_revision: Union[str, Sequence[str], None] = "c73e6c5427ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_answer_option_score_range",
        "answer_options",
        "score BETWEEN 1 AND 5",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_answer_option_score_range",
        "answer_options",
        type_="check",
    )
