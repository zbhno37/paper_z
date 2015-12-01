from mongoengine import Document, StringField, FloatField, IntField, DateTimeField

class Shop(Document):
    shop_id = StringField(primary_key=True, unique=True)
    title = StringField()
    star = FloatField()
    star_1_num = IntField()
    star_2_num = IntField()
    star_3_num = IntField()
    star_4_num = IntField()
    star_5_num = IntField()
    review_num = IntField()
    average = IntField()
    taste_score = FloatField()
    envir_score = FloatField()
    service_score = FloatField()
    telephone = StringField()
    address = StringField()

    meta = {'collection': 'shop'}

class User(Document):
    user_id = StringField(primary_key=True, unique=True)
    username = StringField()

    meta = {'collection': 'user'}

class Comment(Document):
    comment_id = StringField(primary_key=True, unique=True)
    # NO ReferenceField HERE
    user_id = StringField()
    shop_id = StringField()
    content = StringField()
    date = DateTimeField()
    average = IntField()
    # from 1 to 5
    star = IntField()
    taste_score = IntField()
    envir_score = IntField()
    service_score = IntField()

    meta = {'collection': 'comment'}

