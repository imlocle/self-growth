"""todo

Revision ID: 7be76ad19c3a
Revises: 
Create Date: 2024-03-06 14:02:40.527243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7be76ad19c3a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('to_do')
    op.drop_table('habit_history')
    op.drop_table('comment')
    op.drop_table('like')
    op.drop_table('habit')
    op.drop_table('blog_post')
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(length=150), nullable=False),
    sa.Column('username', sa.VARCHAR(length=150), nullable=False),
    sa.Column('password', sa.VARCHAR(length=150), nullable=False),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.Column('date_modified', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('blog_post',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=50), nullable=True),
    sa.Column('body', sa.TEXT(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('date_published', sa.DATETIME(), nullable=True),
    sa.Column('date_modified', sa.DATETIME(), nullable=True),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('habit',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('cues', sa.VARCHAR(length=200), nullable=True),
    sa.Column('current_routine', sa.VARCHAR(length=200), nullable=True),
    sa.Column('new_routine', sa.VARCHAR(length=200), nullable=True),
    sa.Column('change_routine', sa.BOOLEAN(), nullable=True),
    sa.Column('reward', sa.VARCHAR(length=200), nullable=True),
    sa.Column('note', sa.TEXT(), nullable=True),
    sa.Column('stage', sa.VARCHAR(length=100), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('date_started', sa.DATETIME(), nullable=True),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.Column('date_modified', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('like',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('blog_post_id', sa.INTEGER(), nullable=False),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['blog_post_id'], ['blog_post.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('text', sa.VARCHAR(length=200), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('blog_post_id', sa.INTEGER(), nullable=False),
    sa.Column('date_modified', sa.DATETIME(), nullable=True),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['blog_post_id'], ['blog_post.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('habit_history',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('is_completed', sa.BOOLEAN(), nullable=True),
    sa.Column('date_entry', sa.DATETIME(), nullable=True),
    sa.Column('habit_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['habit_id'], ['habit.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('to_do',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('todo', sa.VARCHAR(length=200), nullable=False),
    sa.Column('isCompleted', sa.BOOLEAN(), nullable=True),
    sa.Column('date_due', sa.DATETIME(), nullable=True),
    sa.Column('date_modified', sa.DATETIME(), nullable=True),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
