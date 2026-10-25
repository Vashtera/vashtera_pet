"""add exclusion constraint on bookings

Revision ID: a4a4865b4059
Revises: 787371544de0
Create Date: 2026-10-25 13:58:48.684904

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a4a4865b4059"
down_revision: Union[str, Sequence[str], None] = "787371544de0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT bookings_premise_id_during_excl
        EXCLUDE USING gist (premise_id WITH =, during WITH &&)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE bookings DROP CONSTRAINT bookings_premise_id_during_excl")
