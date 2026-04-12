"""rename_books_table_to_listings

Revision ID: e8a1c3b2d4f5
Revises: c7e2a4f91b00
Create Date: 2026-04-12

"""

from typing import Sequence, Union

from alembic import op


revision: str = "e8a1c3b2d4f5"
down_revision: Union[str, Sequence[str], None] = "c7e2a4f91b00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("books", "listings")
    op.execute('ALTER INDEX "ix_books_url" RENAME TO "ix_listings_url"')


def downgrade() -> None:
    op.execute('ALTER INDEX "ix_listings_url" RENAME TO "ix_books_url"')
    op.rename_table("listings", "books")
