from peewee import *
from FlaskBots.db.MailRepository import MailRepository
from FlaskBots.db.UserRepository import UserRepository


class DB:
    def __init__(self):
        self.mail_repo = None
        self.user_repo = None

    def connect(self, port):
        conn = SqliteDatabase(f'FlaskBots/db/db{port}.sqlite')
        conn.connect()

        class BaseModel(Model):
            class Meta:
                database = conn

        class Message(BaseModel):
            message_id = AutoField(column_name='MessageId')
            pub_k = TextField(column_name='Pub_K', null=False)
            text = TextField(column_name='Message_text', null=False)
            timestamp = DateTimeField(column_name="sending_time", null=False)

            class Meta:
                table_name = 'Message'

        class User(BaseModel):
            pub_k = TextField(column_name='Pub_K', null=False, unique=True)
            nickname = TextField(column_name='nickname', null=False)

        conn.create_tables([Message, User])
        self.mail_repo = MailRepository(Message)
        self.user_repo = UserRepository(User)
