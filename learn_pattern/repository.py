from typing import Protocol
from learn_pattern import Batch

class AbstractRepository(Protocol):

    def add(self, batch: Batch) -> None:
        raise NotImplementedError
    
    def get(self, reference) -> Batch:
        raise NotImplementedError
    
class SqlRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference) -> Batch:
        return self.session.query(Batch).filter_by(reference=reference).one()
    
    def list(self):
        return self.session.query(Batch).all()