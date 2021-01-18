"""add language to posts

Revision ID: 327a10c7d431
Revises: 209e93a56951
Create Date: 2021-01-18 11:17:59.331291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '327a10c7d431'
down_revision = '209e93a56951'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('language', sa.String(length=5), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'language')
    # ### end Alembic commands ###
