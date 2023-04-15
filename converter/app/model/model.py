from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate
from enum import Enum
import datetime

db = SQLAlchemy()

class Status(Enum):
    UPLOADED = 0
    PROCESSED = 1

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(128))
    newFormat = db.Column(db.String(10))
    status = db.Column(db.Enum(Status), nullable=False, default=Status.UPLOADED)
    timeStamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return "fileName: {} - newFormat: {} - status: {} - timeStamp: {}".format(self.fileName, self.newFormat, self.status.value, self.timeStamp)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    email = db.Column(db.String(128))
    password = db.Column(db.String(128))
    tasks = db.relationship('Task', cascade='all, delete, delete-orphan')

    def __repr__(self) -> str:
        return "username: {} - email: {} - password: {}".format(self.username, self.email, self.password)
    
class EnumToDictionary(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {'key': value.name, 'value': value.value}
    
class TaskSchema(SQLAlchemyAutoSchema):
    id = fields.Int()
    fileName = fields.Str()
    newFormat = fields.Str()
    status = EnumToDictionary(attribute=('status'))
    timeStamp = fields.DateTime()
    class Meta:
        model = Task
        include_relationships = True
        load_instance = True
        ordered = True

class UserSchema(SQLAlchemyAutoSchema):
    id = fields.Int()
    username = fields.Str()
    password = fields.Str()
    email = fields.Email()
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        ordered = True

class UserSignupSchema(UserSchema):
    username = fields.Str(required=True)
    password1 = fields.Str(required=True, validate=validate.Length(min=8, max=16))
    password2 = fields.Str(required=True, validate=validate.Length(min=8, max=16))
    email = fields.Email(required=True)

    class Meta:
        model = User
        ordered = True

class UserLoginSchema(UserSchema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)