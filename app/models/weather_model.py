from app import db


class WeatherData(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    city = db.Column(db.String(100))

    temperature = db.Column(db.Float)

    humidity = db.Column(db.Integer)

    weather = db.Column(db.String(100))

    timestamp = db.Column(db.String(100))