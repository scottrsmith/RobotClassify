"""empty message

Revision ID: 21a09eecccb3
Revises: 
Create Date: 2020-02-06 19:39:31.710085

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21a09eecccb3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.String(length=100), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(length=120), nullable=True),
    sa.Column('trainingFile', sa.String(length=120), nullable=True),
    sa.Column('testingFile', sa.String(length=120), nullable=True),
    sa.Column('savedTrainingFile', sa.PickleType(), nullable=True),
    sa.Column('savedTestingFile', sa.PickleType(), nullable=True),
    sa.Column('columns', sa.ARRAY(sa.String()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Run',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(length=120), nullable=True),
    sa.Column('results', sa.PickleType(), nullable=True),
    sa.Column('account_id', sa.String(length=100), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('targetVariable', sa.String(length=120), nullable=True),
    sa.Column('key', sa.String(length=120), nullable=True),
    sa.Column('predictSetOut', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('predictFile', sa.PickleType(), nullable=True),
    sa.Column('modelList', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('scoring', sa.String(length=120), nullable=True),
    sa.Column('basicAutoMethod', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['Project.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Run')
    op.drop_table('Project')
    # ### end Alembic commands ###