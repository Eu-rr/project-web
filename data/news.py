import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    t = datetime.datetime.now()
    s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
    s = s[:-7]
    created_date = sqlalchemy.Column(sqlalchemy.String, default=s)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    tag_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("category.name"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    users = orm.relation('Users')
    categories = orm.relation("Category",
                              secondary="association",
                              backref="news")


