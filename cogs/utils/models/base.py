from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

engine = create_engine(f'postgresql://postgres:{settings.DB_PASS}@localhost:5432/{settings.DB_NAME}')
Session = sessionmaker(bind=engine)
Base = declarative_base()
