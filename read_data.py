from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:Harsh%40123@localhost:5432/capstone.db"

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM materials"))
    for row in result:
        print(row)
