from typing import List
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
        return (
            self.session.query(table1, table2)
            .join(table2)
            .filter(table1.id == id)
            .all()
        )

    def get_all(self, table):
        return self.session.query(table).all()

    def get_all_by_habit_id(self, id: int, table) -> List:
        return self.session.query(table).filter_by(habit_id=id).all()

    def create(self, data) -> None:
        print(f"Session: Created")
        self.session.add(data)
        self.session.commit()

    def update(self, data, table):
        print(f"Session: Update: ID: {data.id}")
        self.session.query(table).filter_by(id=data.id).update(data.to_dict())
        self.session.commit()

    def delete(self, id: int, table):
        print(f"Session: Delete: ID: {id}")
        self.session.query(table).filter_by(id=id).update({"status": "deleted"})
        self.session.commit()

    def close(self):
        print("Session: Closed")
        self.session.close
