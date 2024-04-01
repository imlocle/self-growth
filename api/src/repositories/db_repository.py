from sqlalchemy.orm import Session

DB_NAME = "database.db"
DB_PATH = f"sqlite:///src/{DB_NAME}"


class DbRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, id: str, table):
        try:
            return self.session.query(table).filter_by(id=id).first()
        except Exception as e:
            raise e
        finally:
            self.session.close()

    def get_join(self, id: str, table1, table2):
        try:
            return (
                self.session.query(table1, table2)
                .join(table2)
                .filter(table1.id == id)
                .all()
            )
        except Exception as e:
            raise e
        finally:
            self.session.close()

    def get_all(self, table):
        try:
            return self.session.query(table).all()
        except Exception as e:
            raise e
        finally:
            self.session.close()

    def create(self, data, close=True) -> None:
        try:
            self.session.add(data)
            self.session.commit()
            if close:
                self.session.close()
        except Exception as e:
            raise e

    def update(self, data, table):
        try:
            self.session.query(table).filter_by(id=data.id).update(data.to_dict())
            self.session.commit()
            return
        except Exception as e:
            raise e
        finally:
            self.session.close()
