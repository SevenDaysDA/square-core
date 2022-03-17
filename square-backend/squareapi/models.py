from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


db = declarative_base()

def init_db(engine_string):
    """
    Initialize the database connection and prepare the db object.
    Set db.query and db.session to work similar to Flask_SQLAlchemy.SQLAlchemy
    :param engine_string: Database connenction string
    """
    engine = create_engine(engine_string)
    session = scoped_session(sessionmaker(bind=engine))
    db.query = session.query_property()
    db.metadata.create_all(bind=engine)
    db.session = session
    db.engine = engine


class User(db):
    """
    A user with a unique name.
    The password is only stored as hash (we do not salt currently).
    A user can own multiple skills.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(100), nullable=False)
    skills = relationship("Skill", backref="users")

    def __init__(self, name, password):
        self.name = name
        self.password_hash = generate_password_hash(password, method="sha256")

    @classmethod
    def authenticate(cls, username, password):
        if not username or not password:
            return None
        user = cls.query.filter_by(name=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return None
        return user

    def to_dict(self):
        return dict(id=self.id, name=self.name)

class Skill(db):
    """
    A skill with a unique name.
    It belongs to one user.
    It should be only visible to this user or to all if published.
    The URL is not validated by us.
    """
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(50), nullable=False, unique=True)
    is_published = Column(Boolean, nullable=False)
    url = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    examples = relationship("SkillExampleSentence", backref="skills")

    def __init__(self, user, skill):
        self.owner_id = user["id"]
        self.name = skill["name"]
        self.is_published = False
        self.description = skill["description"]
        url = skill["url"]
        if url[-1] == "/":
            url = url[:-1]
        self.url = url

    def update(self, skill):
        self.name = skill["name"]
        # self.is_published = skill["is_published"]
        self.description = skill["description"]
        url = skill["url"]
        if url[-1] == "/":
            url = url[:-1]
        self.url = url

    def set_publish(self, new_status):
        self.is_published = new_status

    def to_dict(self):
        return dict(id=self.id, name=self.name, owner_id=self.owner_id, is_published=self.is_published,
                    description=self.description, url=self.url)


class SkillExampleSentence(db):
    """
    An example sentence of a skill used for training and validation
    """
    __tablename__ = "skillexamplesentences"

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    is_dev = Column(Boolean, nullable=False)
    sentence = Column(String(300), nullable=False)

    def __init__(self, skill, sentence, is_dev):
        self.skill_id = skill["id"]
        self.sentence = sentence
        self.is_dev = is_dev