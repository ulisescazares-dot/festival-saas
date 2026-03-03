"""update exhibitor full structure

Revision ID: c7ec05a840f9
Revises: 8aa48bf6473a
Create Date: 2026-03-03
"""

from alembic import op
import sqlalchemy as sa

revision = 'c7ec05a840f9'
down_revision = '8aa48bf6473a'
branch_labels = None
depends_on = None


def upgrade():

    # =========================
    # EVENT - ADD SLUG SAFELY
    # =========================
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=150), nullable=True))

    connection = op.get_bind()
    results = connection.execute(sa.text("SELECT id, city FROM event")).fetchall()

    for row in results:
        slug_value = row.city.lower().replace(" ", "-")
        connection.execute(
            sa.text("UPDATE event SET slug = :slug WHERE id = :id"),
            {"slug": slug_value, "id": row.id}
        )

    with op.batch_alter_table('event') as batch_op:
        batch_op.alter_column('slug', nullable=False)
        batch_op.create_unique_constraint(None, ['slug'])


    # =========================
    # EXHIBITOR - NEW FIELDS
    # =========================
    with op.batch_alter_table('exhibitor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column('instagram', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('total_amperage', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('voltage', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('needs_220', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('own_generator', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('electrical_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('accepted_reglamento', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('accepted_carta_responsiva', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('signer_name', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('signature_base64', sa.Text(), nullable=True))
        batch_op.drop_column('payment_status')


    # =========================
    # EXHIBITOR DOCUMENT
    # =========================
    with op.batch_alter_table('exhibitor_document', schema=None) as batch_op:
        batch_op.alter_column(
            'file_path',
            existing_type=sa.VARCHAR(length=255),
            type_=sa.String(length=500),
            nullable=False
        )
        batch_op.drop_column('uploaded_at')


    # =========================
    # FESTIVAL - ADD SLUG SAFELY
    # =========================
    with op.batch_alter_table('festival', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=150), nullable=True))

    results = connection.execute(sa.text("SELECT id, name FROM festival")).fetchall()

    for row in results:
        slug_value = row.name.lower().replace(" ", "-")
        connection.execute(
            sa.text("UPDATE festival SET slug = :slug WHERE id = :id"),
            {"slug": slug_value, "id": row.id}
        )

    with op.batch_alter_table('festival') as batch_op:
        batch_op.alter_column('slug', nullable=False)
        batch_op.create_unique_constraint(None, ['slug'])
        batch_op.alter_column('organization_id', nullable=False)


def downgrade():

    with op.batch_alter_table('festival', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('organization_id', nullable=True)
        batch_op.drop_column('slug')

    with op.batch_alter_table('exhibitor_document', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uploaded_at', sa.TIMESTAMP(), nullable=True))
        batch_op.alter_column(
            'file_path',
            existing_type=sa.String(length=500),
            type_=sa.VARCHAR(length=255),
            nullable=True
        )

    with op.batch_alter_table('exhibitor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_status', sa.VARCHAR(length=30), nullable=True))
        batch_op.drop_column('signature_base64')
        batch_op.drop_column('signer_name')
        batch_op.drop_column('accepted_carta_responsiva')
        batch_op.drop_column('accepted_reglamento')
        batch_op.drop_column('electrical_notes')
        batch_op.drop_column('own_generator')
        batch_op.drop_column('needs_220')
        batch_op.drop_column('voltage')
        batch_op.drop_column('total_amperage')
        batch_op.drop_column('instagram')
        batch_op.drop_column('address')

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('slug')