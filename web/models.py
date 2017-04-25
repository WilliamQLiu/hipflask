from datetime import datetime

from hipflask import application


class Buzz(db.Model):
    __tablename__ = "buzz"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256))
    pub_date = db.Column(db.DateTime)

    def __init__(self, url, pub_date=None):
        self.url = url
        if pub_date is None:
            pub_date = datetime.utcnow()

    def __repr__(self):
        return "<Buzz %r>" % self.id
