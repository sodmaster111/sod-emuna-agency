"""Convert integer primary keys to UUIDs and add performance indexes.

Revision ID: 0001_uuid_upgrade
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_uuid_upgrade"
down_revision = None
branch_labels = None
depends_on = None


UUID_TYPE = postgresql.UUID(as_uuid=True)


def upgrade():
    # Ensure UUID generation is available in Postgres
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # --- Pinkas ---
    op.add_column(
        "pinkas",
        sa.Column(
            "new_id",
            UUID_TYPE,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
    )
    op.execute("UPDATE pinkas SET new_id = gen_random_uuid() WHERE new_id IS NULL;")
    op.drop_constraint("pinkas_pkey", "pinkas", type_="primary")
    op.alter_column("pinkas", "id", new_column_name="old_id")
    op.alter_column("pinkas", "new_id", new_column_name="id")
    op.create_primary_key("pinkas_pkey", "pinkas", ["id"])
    op.drop_column("pinkas", "old_id")
    op.alter_column(
        "pinkas",
        "id",
        server_default=None,
        existing_type=UUID_TYPE,
    )
    op.create_index(
        "idx_pinkas_timestamp",
        "pinkas",
        [sa.text("timestamp DESC")],
    )
    op.create_index("idx_pinkas_agent", "pinkas", ["agent"])
    op.create_index("idx_pinkas_status", "pinkas", ["status"])

    # --- Content categories & items ---
    op.add_column(
        "content_categories",
        sa.Column(
            "new_id",
            UUID_TYPE,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
    )
    op.execute(
        "UPDATE content_categories SET new_id = gen_random_uuid() WHERE new_id IS NULL;"
    )

    op.add_column(
        "content_items",
        sa.Column("new_category_id", UUID_TYPE, nullable=True),
    )
    op.add_column(
        "content_items",
        sa.Column(
            "new_id",
            UUID_TYPE,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
    )
    op.execute("UPDATE content_items SET new_id = gen_random_uuid() WHERE new_id IS NULL;")
    op.execute(
        """
        UPDATE content_items ci
        SET new_category_id = cc.new_id
        FROM content_categories cc
        WHERE ci.category_id = cc.id
        """
    )

    op.drop_constraint(
        "content_items_category_id_fkey", "content_items", type_="foreignkey"
    )
    op.drop_constraint("content_items_pkey", "content_items", type_="primary")
    op.drop_constraint("content_categories_pkey", "content_categories", type_="primary")

    op.alter_column("content_items", "id", new_column_name="old_id")
    op.alter_column("content_categories", "id", new_column_name="old_id")
    op.alter_column("content_categories", "new_id", new_column_name="id")
    op.create_primary_key("content_categories_pkey", "content_categories", ["id"])

    op.alter_column("content_items", "category_id", new_column_name="old_category_id")
    op.alter_column("content_items", "new_category_id", new_column_name="category_id")
    op.alter_column("content_items", "new_id", new_column_name="id")
    op.create_primary_key("content_items_pkey", "content_items", ["id"])
    op.create_foreign_key(
        "content_items_category_id_fkey",
        "content_items",
        "content_categories",
        ["category_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_column("content_items", "old_category_id")
    op.drop_column("content_items", "old_id")
    op.drop_column("content_categories", "old_id")
    op.alter_column(
        "content_items",
        "id",
        server_default=None,
        existing_type=UUID_TYPE,
    )
    op.alter_column(
        "content_categories",
        "id",
        server_default=None,
        existing_type=UUID_TYPE,
    )

    op.create_index("idx_content_category", "content_items", ["category_id"])
    op.create_index("idx_content_tags", "content_items", ["tags"])

    # --- Missions ---
    op.add_column(
        "mission_templates",
        sa.Column(
            "new_id",
            UUID_TYPE,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
    )
    op.execute(
        "UPDATE mission_templates SET new_id = gen_random_uuid() WHERE new_id IS NULL;"
    )

    op.add_column(
        "mission_instances",
        sa.Column("new_template_id", UUID_TYPE, nullable=True),
    )
    op.add_column(
        "mission_instances",
        sa.Column(
            "new_id",
            UUID_TYPE,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
    )
    op.execute(
        "UPDATE mission_instances SET new_id = gen_random_uuid() WHERE new_id IS NULL;"
    )
    op.execute(
        """
        UPDATE mission_instances mi
        SET new_template_id = mt.new_id
        FROM mission_templates mt
        WHERE mi.template_id = mt.id
        """
    )

    op.drop_constraint(
        "mission_instances_template_id_fkey",
        "mission_instances",
        type_="foreignkey",
    )
    op.drop_constraint("mission_instances_pkey", "mission_instances", type_="primary")
    op.drop_constraint("mission_templates_pkey", "mission_templates", type_="primary")

    op.alter_column("mission_templates", "id", new_column_name="old_id")
    op.alter_column("mission_templates", "new_id", new_column_name="id")
    op.create_primary_key("mission_templates_pkey", "mission_templates", ["id"])

    op.alter_column(
        "mission_instances", "template_id", new_column_name="old_template_id"
    )
    op.alter_column(
        "mission_instances", "new_template_id", new_column_name="template_id"
    )
    op.alter_column("mission_instances", "id", new_column_name="old_id")
    op.alter_column("mission_instances", "new_id", new_column_name="id")
    op.create_primary_key("mission_instances_pkey", "mission_instances", ["id"])
    op.create_foreign_key(
        "mission_instances_template_id_fkey",
        "mission_instances",
        "mission_templates",
        ["template_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_column("mission_instances", "old_template_id")
    op.drop_column("mission_instances", "old_id")
    op.drop_column("mission_templates", "old_id")
    op.alter_column(
        "mission_instances",
        "id",
        server_default=None,
        existing_type=UUID_TYPE,
    )
    op.alter_column(
        "mission_templates",
        "id",
        server_default=None,
        existing_type=UUID_TYPE,
    )

    op.create_index("idx_mission_status", "mission_instances", ["status"])
    op.create_index("idx_mission_template", "mission_instances", ["template_id"])


def downgrade():
    # Complex downgrade steps are intentionally not implemented to avoid data loss
    # when reverting UUID primary keys back to integers. Use database backups to
    # restore prior states if a rollback is required.
    raise NotImplementedError("Downgrade is not supported for UUID migration")
