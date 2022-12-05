from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_path = ''

eng = create_engine(db_path)
Base = declarative_base()

class Survey(Base):
    __tablename__ = "Survey"
    id = Column(Integer, primary_key=True, autoincrement=True)
    survey_id = Column(String)
    approved = Column(Boolean)
    completed = Column(Boolean)
    recording_id = Column(Integer)
    horizontal_or_vertical = Column(VARCHAR)
    timestamp = Column(TIMESTAMP)

    def __init__(self,survey_id, timestamp):
        self.survey_id = survey_id
        self.timestamp = timestamp


class Annotation(Base):
    __tablename__ = "Annotation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    survey_id = Column(String)
    recording_id = Column(Integer)
    source_count = Column(Integer)
    user_note = Column(String)
    practice_round = Column(Boolean)
    vertical = Column(Boolean)

    def __init__(self,survey_id,recording_id,source_count,user_note,practice_round,vertical):
        self.survey_id = survey_id
        self.recording_id = recording_id
        self.source_count = source_count
        self.user_note = user_note
        self.practice_round = practice_round
        self.vertical = vertical


class Interaction(Base):
    __tablename__ = "Interaction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    annotation_id = Column(String)
    action_type = Column(String)
    value = Column(String)
    timestamp = Column(TIMESTAMP)
    practice_round = Column(Boolean)

    def __init__(self,annotation_id,action_type,value,timestamp,practice_round):
        self.annotation_id = annotation_id
        self.action_type = action_type
        self.value = value
        self.timestamp = timestamp
        self.practice_round = practice_round


class Location(Base):
    __tablename__ = "Location"

    id = Column(Integer, primary_key=True, autoincrement=True)
    annotation_id = Column(String)
    azimuth = Column(Integer)
    elevation = Column(Integer)
    color = Column(Integer)
    practice_round = Column(Boolean)

    def __init__(self,annotation_id,azimuth,elevation,color,practice_round):
        self.annotation_id = annotation_id
        self.azimuth = azimuth
        self.elevation = elevation
        self.color = color
        self.practice_round = practice_round


class Confirmation(Base):
    __tablename__ = "Confirmation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recording_id = Column(Integer)
    source_id = Column(Integer)
    location_id = Column(Integer)
    practice_round = Column(Boolean)
    annotation_id = Column(String)

    def __init__(self,recording_id,source_id,location_id,annotation_id,practice_round):
        self.recording_id = recording_id
        self.source_id = source_id
        self.location_id = location_id
        self.annotation_id = annotation_id
        self.practice_round = practice_round


Base.metadata.bind = eng
Session = sessionmaker(bind=eng)
ses = Session()

Base.metadata.bind = eng
Session = sessionmaker(bind=eng)
ses = Session()

Base.metadata.create_all()
