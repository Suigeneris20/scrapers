"""Un-nullable brand

Revision ID: 7633bfa59b92
Revises: 50f30edd4889
Create Date: 2025-03-29 00:18:16.276708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7633bfa59b92'
down_revision = '50f30edd4889'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('brand',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('brand',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###
