from collections import defaultdict
from dateutil import parser


class MailRepository:
    def __init__(self, message_model):
        self.message_model = message_model

    def add_message(self, recv_pub_k, message, timestamp: str):
        created = self.message_model(pub_k=recv_pub_k, text=message, timestamp=parser.parse(timestamp))
        created.save()

    def get_messages_by_recv_pub_k(self, recv_pub_k):
        query = self.message_model.select().where(self.message_model.pub_k == recv_pub_k)
        messages_selected = query.namedtuples().execute()
        return [record.text for record in messages_selected]
