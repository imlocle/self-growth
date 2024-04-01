"""todo table

Revision ID: deca1df09632
Revises: e934652e4139
Create Date: 2024-03-06 14:31:11.591595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'deca1df09632'
down_revision = 'e934652e4139'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('to_do',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('isCompleted', sa.Boolean(), nullable=True),
    sa.Column('date_due', sa.DateTime(timezone=True), nullable=True),
    sa.Column('date_modified', sa.DateTime(timezone=True), nullable=True),
    sa.Column('date_created', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('to_do')
    # ### end Alembic commands ###
