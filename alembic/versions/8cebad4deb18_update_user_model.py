"""update user model

Revision ID: 8cebad4deb18
Revises: 80a2f718fe50
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "8cebad4deb18"
down_revision: Union[str, Sequence[str], None] = "80a2f718fe50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the PostgreSQL enum type before using it.
    user_role = postgresql.ENUM(
        "customer",
        "admin",
        "product_manager",
        "fulfilment",
        name="user_role",
        create_type=False,
    )
    user_role.create(op.get_bind(), checkfirst=True)

    # 2. Add the new columns.
    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role,
            server_default=sa.text("'customer'"),
            nullable=False,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "phone_verified",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    op.add_column(
        "users",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 3. Update email indexes.
    op.drop_index(op.f("ix_users_email"), table_name="users")

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=False,
    )

    op.create_index(
        op.f("ix_users_role"),
        "users",
        ["role"],
        unique=False,
    )

    op.create_index(
        "uq_users_email_lower",
        "users",
        [sa.literal_column("lower(email)")],
        unique=True,
    )

    # 4. Ensure phone numbers are unique.
    op.create_unique_constraint(
        "uq_users_phone",
        "users",
        ["phone"],
    )


def downgrade() -> None:
    # Reverse the changes in a safe order.
    op.drop_constraint("uq_users_phone", "users", type_="unique")

    op.drop_index("uq_users_email_lower", table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    op.drop_column("users", "deleted_at")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "phone_verified")
    op.drop_column("users", "role")

    # Remove the enum after removing the column that uses it.
    user_role = postgresql.ENUM(
        "customer",
        "admin",
        "product_manager",
        "fulfilment",
        name="user_role",
        create_type=False,
    )
    user_role.drop(op.get_bind(), checkfirst=True)