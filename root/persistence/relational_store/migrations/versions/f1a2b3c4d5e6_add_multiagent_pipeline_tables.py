"""add_multiagent_pipeline_tables

Revision ID: f1a2b3c4d5e6
Revises: e8a1c3b2d4f5
Create Date: 2026-04-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e8a1c3b2d4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "listing_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("idempotency_key", sa.String(length=256), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("listing_id", sa.String(length=128), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("last_seen_price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("content_hash_light", sa.String(length=64), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_seen_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_listing_state_idempotency_key",
        "listing_state",
        ["idempotency_key"],
        unique=True,
    )

    op.create_table(
        "listing_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("idempotency_key", sa.String(length=256), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description_markdown", sa.Text(), nullable=False, server_default=""),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="RUB"),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "attributes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_listing_versions_idempotency_key", "listing_versions", ["idempotency_key"])
    op.create_index("ix_listing_versions_content_hash", "listing_versions", ["content_hash"])

    op.create_table(
        "ingestion_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=256), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ok"),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ingestion_events_stage", "ingestion_events", ["stage"])
    op.create_index("ix_ingestion_events_idempotency_key", "ingestion_events", ["idempotency_key"])


def downgrade() -> None:
    op.drop_index("ix_ingestion_events_idempotency_key", table_name="ingestion_events")
    op.drop_index("ix_ingestion_events_stage", table_name="ingestion_events")
    op.drop_table("ingestion_events")

    op.drop_index("ix_listing_versions_content_hash", table_name="listing_versions")
    op.drop_index("ix_listing_versions_idempotency_key", table_name="listing_versions")
    op.drop_table("listing_versions")

    op.drop_index("ix_listing_state_idempotency_key", table_name="listing_state")
    op.drop_table("listing_state")
