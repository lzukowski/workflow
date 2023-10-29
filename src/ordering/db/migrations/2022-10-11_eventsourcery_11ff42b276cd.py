"""EventSourcery

Revision ID: 11ff42b276cd
Revises: 83b698eb2648
Create Date: 2022-10-11 16:31:20.204806

"""
import sqlalchemy as sa
from alembic import op
from event_sourcery_sqlalchemy.guid import GUID
from event_sourcery_sqlalchemy.jsonb import JSONB


revision = '11ff42b276cd'
down_revision = '83b698eb2648'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "event_sourcery_streams",
        sa.Column("uuid", GUID(), primary_key=True),
        sa.Column("version", sa.BigInteger(), nullable=False),
    )

    op.create_table(
        "event_sourcery_events",
        sa.Column("id", sa.BigInteger(), primary_key=True,),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("uuid", GUID(), index=True, unique=True),
        sa.Column("stream_id", GUID(), nullable=False, index=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column("event_metadata", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, index=True),
    )
    op.create_index(
        "ix_events_stream_id_version",
        "event_sourcery_events",
        columns=["stream_id", "version"],
        unique=True,
    )

    op.create_table(
        "event_sourcery_snapshots",
        sa.Column("uuid", GUID, primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("stream_id", GUID(), nullable=False, index=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column("event_metadata", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "event_sourcery_outbox_entries",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column("tries_left", sa.Integer(), nullable=False, server_default="3"),
    )


def downgrade():
    op.drop_table("event_sourcery_streams")
    op.drop_table("event_sourcery_events")
    op.drop_table("event_sourcery_snapshots")
    op.drop_table("event_sourcery_outbox_entries")
