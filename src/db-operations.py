from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, aliased

DATABASE_URL = "postgresql+psycopg2://user:pass@localhost:5432/knowledge_db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


# Database table classes==============================================================

class Entity(Base):
    __tablename__ = 'entities'

    entity_id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), nullable=False)
    entity_name = Column(Text, nullable=False)


class Predicate(Base):
    __tablename__ = 'predicates'

    predicate_id = Column(Integer, primary_key=True)
    predicate_name = Column(String(100), nullable=False, unique=True)

    triples = relationship("Triple", back_populates="predicate")


class Triple(Base):
    __tablename__ = 'triples'

    triple_id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('entities.entity_id', ondelete='CASCADE'), nullable=False)
    predicate_id = Column(Integer, ForeignKey('predicates.predicate_id', ondelete='CASCADE'), nullable=False)
    object_id = Column(Integer, ForeignKey('entities.entity_id', ondelete='CASCADE'), nullable=False)

    subject = relationship("Entity", foreign_keys=[subject_id] )
    predicate = relationship("Predicate", back_populates="triples")
    object = relationship("Entity", foreign_keys=[object_id] )


# DB service class==============================================================

class DBService:
    def __init__(self):
        self.session = SessionLocal()

    def add_entity(self, entity_type, entity_name):
        entity = Entity(entity_type=entity_type, entity_name=entity_name)
        self.session.add(entity)
        self.session.commit()
        return entity

    def add_predicate(self, predicate_name):
        predicate = Predicate(predicate_name=predicate_name)
        self.session.add(predicate)
        self.session.commit()
        return predicate

    def add_triple(self, subject_id, predicate_id, object_id):
        triple = Triple(subject_id=subject_id, predicate_id=predicate_id, object_id=object_id)
        self.session.add(triple)
        self.session.commit()
        return triple

    def delete_entity(self, entity_id):
        entity = self.session.query(Entity).get(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False

    def delete_predicate(self, predicate_id):
        predicate = self.session.query(Predicate).get(predicate_id)
        if predicate:
            self.session.delete(predicate)
            self.session.commit()
            return True
        return False

    def delete_triple(self, triple_id):
        triple = self.session.query(Triple).get(triple_id)
        if triple:
            self.session.delete(triple)
            self.session.commit()
            return True
        return False


    def get_triples(self, triple_ids=None):

        SubjectEntity = aliased(Entity)
        ObjectEntity = aliased(Entity)

        query = self.session.query(Triple) \
        .join(SubjectEntity, Triple.subject_id == SubjectEntity.entity_id) \
        .join(Predicate, Triple.predicate_id == Predicate.predicate_id) \
        .join(ObjectEntity, Triple.object_id == ObjectEntity.entity_id)

        if triple_ids:
            query = query.filter(Triple.triple_id.in_(triple_ids))

        triples = query.all()

        result = []
        for t in triples:
            result.append((
                t.subject.entity_name, 
                t.predicate.predicate_name,
                t.object.entity_name  
            ))
        return result   

    def close(self):
        self.session.close()


if __name__ == "__main__":
    service = DBService()

    # alice = service.add_entity("Person", "Alice")
    # bob = service.add_entity("Person", "Bob")
    # knows = service.add_predicate("knows")

    # triple = service.add_triple(subject_id=alice.entity_id, predicate_id=knows.predicate_id, object_id=bob.entity_id)
    
    # print(f"Triple ID: {triple.triple_id}")


    all_triples = service.get_triples()

    print(all_triples)

    service.close()

