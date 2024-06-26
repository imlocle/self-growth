"""habit events table

Revision ID: e56f186e5016
Revises: 0b01460ccfad
Create Date: 2024-03-28 15:45:40.566176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e56f186e5016'
down_revision = '0b01460ccfad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('habit_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('new', 'completed', name='statusenum'), nullable=True),
    sa.Column('reset_counter', sa.Enum('daily', 'weekly', 'monthly', name='resetcounterenum'), nullable=True),
    sa.Column('date_created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('date_modified', sa.DateTime(timezone=True), nullable=True),
    sa.Column('habit_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['habit_id'], ['habit.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('habit_history')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('habit_history',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('is_completed', sa.BOOLEAN(), nullable=True),
    sa.Column('reset_counter', sa.VARCHAR(length=7), nullable=True),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.Column('habit_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['habit_id'], ['habit.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('habit_events')
    # ### end Alembic commands ###
