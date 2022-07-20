import sqlalchemy as sq
import enum
from var_name import database_name
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database

engine = sq.create_engine(database_name)
Session = sessionmaker(bind=engine)
if not database_exists(engine.url):
     create_database(engine.url)

Base = declarative_base()
engine = sq.create_engine(database_name)
Session = sessionmaker(bind=engine)


class EnumRelations(enum.Enum):
    not_specified = 0
    single = 1
    have_a_friend = 2
    engaged = 3
    married = 4
    complicated = 5
    actively_searching = 6
    in_love = 7
    in_a_civil_marriage = 8


class EnumSex(enum.Enum):
    not_specified = 0
    female = 1
    male = 2


class Users(Base):
    __tablename__ = 'users'
    id_user = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, nullable=False)
    first_name = sq.Column(sq.String(50), nullable=False)
    last_name = sq.Column(sq.String(50), nullable=False)
    id_city = sq.Column(sq.Integer, nullable=False)
    bdate = sq.Column(sq.String(10), nullable=False)
    is_closed = sq.Column(sq.Boolean, nullable=False)
    id_relation = sq.Column(sq.Enum(EnumRelations))
    id_sex = sq.Column(sq.Enum(EnumSex))


class Customers(Base):
    __tablename__ = 'customers'
    id_customer = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('users.id_user'))
    user = relationship('Users', backref='customer', uselist=False)
    candidates = relationship('Candidates', secondary='friends', backref='customers')


class Candidates(Base):
    __tablename__ = 'candidates'
    id_candidate = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('users.id_user'))
    user = relationship('Users', backref='candidate', uselist=False)


candidate_to_customer = sq.Table(
    'friends', Base.metadata,
    sq.Column('id_customer', sq.Integer, sq.ForeignKey('customers.id_customer')),
    sq.Column('id_candidate', sq.Integer, sq.ForeignKey('candidates.id_candidate')),
)
