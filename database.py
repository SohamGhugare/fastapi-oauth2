from sqlmodel import create_engine, Session, select, SQLModel
from models import UserModel

import warnings
warnings.filterwarnings("ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*")

class Database:
    """ Database Utility Functions """
    def __init__(self):
        self.db_uri = "sqlite:///data/users.db"

    @property
    def engine(self):
        return create_engine(self.db_uri, echo=False)

    @property
    def session(self) -> Session:
        return Session(self.engine)

    def get_user(self, username: str):
        with self.session as session:
            user = session.exec(select(UserModel).where(UserModel.username == username)).first()
        return user

    def create_user(self, user: UserModel):
        with self.session as session:
            session.add(user)
            session.commit()   
        return True    


if __name__ == "__main__":
    SQLModel.metadata.create_all(Database().engine)