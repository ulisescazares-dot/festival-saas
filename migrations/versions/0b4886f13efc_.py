"""empty message

Revision ID: 0b4886f13efc
Revises: c7ec05a840f9
Create Date: 2026-03-06 22:14:34.461720

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0b4886f13efc'
down_revision = 'c7ec05a840f9'
branch_labels = None
depends_on = None


def upgrade():

    # Primero borrar tabla dependiente
    op.drop_table('contest_registration')

    # Luego borrar contest
    op.drop_table('contest')

    # ### end Alembic commands ###


def downgrade():

    op.create_table(
        'contest',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('festival_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(150)),
        sa.Column('description', sa.Text()),
        sa.Column('slug', sa.String(150))
    )

    op.create_table(
        'contest_registration',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('contest_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(150)),
        sa.Column('email', sa.String(150))
    )

    op.create_table('contest_registration',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('contest_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('full_name', sa.VARCHAR(length=150), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=150), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['contest_id'], ['contest.id'], name=op.f('contest_registration_contest_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('contest_registration_pkey'))
    )
    op.create_table('contest',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('festival_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=150), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('slug', sa.VARCHAR(length=150), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['festival_id'], ['festival.id'], name=op.f('contest_festival_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('contest_pkey')),
    sa.UniqueConstraint('slug', name=op.f('contest_slug_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    # ### end Alembic commands ###
