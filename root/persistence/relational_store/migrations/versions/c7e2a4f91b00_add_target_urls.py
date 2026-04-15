"""add_target_urls

Revision ID: c7e2a4f91b00
Revises: d979cc07a71d
Create Date: 2026-04-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7e2a4f91b00"
down_revision: Union[str, Sequence[str], None] = "d979cc07a71d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "target_urls",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_scraped_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )
    op.create_index(
        "ix_target_urls_last_scraped_at", "target_urls", ["last_scraped_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_target_urls_last_scraped_at", table_name="target_urls")
    op.drop_table("target_urls")
