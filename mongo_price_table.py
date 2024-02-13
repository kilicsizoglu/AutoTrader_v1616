from datetime import datetime

from mongoengine import Document, StringField, DateTimeField, FloatField


class CryptoPriceClass(Document):
    symbol = StringField(required=True, max_length=50)
    time = DateTimeField(default=datetime.utcnow)
    price = FloatField()
    ratio = FloatField()
    predict = FloatField()