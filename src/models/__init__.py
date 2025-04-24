from sqlalchemy import create_engine

favorites_engine = create_engine(
    'sqlite:///data/favorites.db?check_same_thread=False')
