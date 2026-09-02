from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'aa27ccefbc9f'
down_revision: Union[str, Sequence[str], None] = '623f7ebae03b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


difficulty_enum = sa.Enum(
    'EASY',
    'MEDIUM',
    'HARD',
    name='difficultylevel',
)


def upgrade() -> None:
    # 1. Создаём enum в PostgreSQL
    difficulty_enum.create(op.get_bind(), checkfirst=True)

    # 2. Меняем тип колонки с VARCHAR на ENUM
    op.alter_column(
        'tasks',
        'difficulty',
        existing_type=sa.VARCHAR(),
        type_=difficulty_enum,
        existing_nullable=False,
        postgresql_using='difficulty::difficultylevel',
    )


def downgrade() -> None:
    # 1. Возвращаем VARCHAR
    op.alter_column(
        'tasks',
        'difficulty',
        existing_type=difficulty_enum,
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using='difficulty::text',
    )

    # 2. Удаляем enum
    difficulty_enum.drop(op.get_bind(), checkfirst=True)