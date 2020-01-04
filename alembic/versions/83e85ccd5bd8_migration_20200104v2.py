"""migration 20200104v2

Revision ID: 83e85ccd5bd8
Revises: 342a10305d8b
Create Date: 2020-01-04 16:33:11.213728

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '83e85ccd5bd8'
down_revision = '342a10305d8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('posts', 'created',
               new_column_name='created_ts',
               existing_type=sa.DateTime(),
               type_=sa.TIMESTAMP())
    op.add_column('posts', sa.Column('updated_ts', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'updated_ts')
    op.alter_column('posts', 'created_ts',
               new_column_name='created',
               existing_type=sa.TIMESTAMP(),
               type_=sa.DateTime())
    # ### end Alembic commands ###
