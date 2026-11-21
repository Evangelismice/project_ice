from sqlalchemy import inspect, text

from app.database import engine
from app.models.base import Base
from app import main  # noqa: F401

insp = inspect(engine)
with engine.begin() as conn:
    for table in Base.metadata.sorted_tables:
        if not insp.has_table(table.name):
            print(f'{table.name}: table missing (created when the server starts)')
            continue
        have = {c['name'] for c in insp.get_columns(table.name)}
        for col in table.columns:
            if col.name in have:
                continue
            if col.nullable:
                ctype = col.type.compile(dialect=engine.dialect)
                conn.execute(text(f'ALTER TABLE {table.name} ADD COLUMN {col.name} {ctype}'))
                print(f'{table.name}.{col.name}: added')
            else:
                print(f'{table.name}.{col.name}: NOT NULL, add it by hand or delete ice.db')
print('check finished')
