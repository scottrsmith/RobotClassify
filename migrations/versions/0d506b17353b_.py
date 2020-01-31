"""empty message

Revision ID: 0d506b17353b
Revises: 95f0735a7c58
Create Date: 2020-01-30 13:36:23.314638

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0d506b17353b'
down_revision = '95f0735a7c58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Run', 'setProjectGoals')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Run', sa.Column('setProjectGoals', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
