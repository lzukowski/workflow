"""BuyOrder for ordering module

Revision ID: 83b698eb2648
Revises:
Create Date: 2021-12-09 17:53:03.693385

"""
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy_utils as sa_utils
from alembic import op

revision = '83b698eb2648'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "buy_orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa_utils.UUIDType, unique=True),
        sa.Column("request_id", sa_utils.UUIDType, unique=True),
        sa.Column("paid", sa.BigInteger),
        sa.Column("bought", sa.BigInteger),
        sa.Column("currency", sa.String(3)),
        sa.Column("price", sa.BigInteger),
        sa.Column("rate_date", sa.DateTime),
        sa.Column("when_created", sa.DateTime, default=datetime.utcnow),
        sa.Column("when_updated", sa.DateTime, onupdate=datetime.utcnow),
    )


def downgrade():
    op.drop_table("buy_orders")
