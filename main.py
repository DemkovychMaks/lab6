from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json


with open("secret.json") as f:
    SECRET = json.load(f)

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
    user=SECRET["user"],
    password=SECRET["password"],
    host=SECRET["host"],
    port=SECRET["port"],
    db=SECRET["db"])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Bulb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False)
    origin_country = db.Column(db.String(20), unique=False)
    producer = db.Column(db.String(20), unique=False)
    price = db.Column(db.Integer, unique=False)
    size_in_cm = db.Column(db.Integer, unique=False)
    power_in_watts = db.Column(db.Integer, unique=False)
    expiration_date = db.Column(db.Integer, unique=False)

    def __init__(self, name, origin_country, producer, price, size_in_cm, power_in_watts, expiration_date):
        self.name = name
        self.origin_country = origin_country
        self.producer = producer
        self.price = price
        self.size_in_cm = size_in_cm
        self.power_in_watts = power_in_watts
        self.expiration_date = expiration_date

class BulbSchema(ma.Schema):
    class Meta:
        fields = ('name', 'origin_country', 'producer', 'price', 'size_in_cm', 'power_in_watts', 'expiration_date')


bulb_schema = BulbSchema() # стеціалізація
bulbs_schema = BulbSchema(many=True)


@app.route("/bulb", methods=["POST"]) # адреса і метод
def add_bulb():
    name = request.json['name']
    origin_country = request.json['origin_country']
    producer = request.json['producer']
    price = request.json['price']
    size_in_cm = request.json['size_in_cm']
    power_in_watts = request.json['power_in_watts']
    expiration_date = request.json['expiration_date']
    new_bulb = Bulb(name, origin_country, producer, price, size_in_cm, power_in_watts, expiration_date)
    db.session.add(new_bulb)
    db.session.commit() # глобальні обєкти через які доступаєся проксі
    return bulb_schema.jsonify(new_bulb)


@app.route("/bulb", methods=["GET"])
def get_bulb():
    all_bulbs = Bulb.query.all() # база даних
    result = bulbs_schema.dump(all_bulbs) # спеціалізує
    return jsonify({'bulbs_schema': result}) # jsonify serializes data to
    # JavaScript Object Notation (JSON) format,
    # wraps it in a Response object with the application


@app.route("/bulb/<id>", methods=["GET"])
def bulb_detail(id):
    bulb = Bulb.query.get(id)
    if not bulb:
        abort(404)
    return bulbs_schema.jsonify(bulb)


@app.route("/bulb/<id>", methods=["PUT"])
def bulb_update(id):
    bulb = Bulb.query.get(id)
    if not bulb:
        abort(404)
    bulb.name = request.json['name']
    bulb.origin_country = request.json['origin_country']
    bulb.producer = request.json['producer']
    bulb.price = request.json['price']
    bulb.size_in_cm = request.json['size_in_cm']
    bulb.power_in_watts = request.json['power_in_watts']
    bulb.expiration_date = request.json['expiration_date']

    db.session.commit() # завершення сесії
    return bulbs_schema.jsonify(bulb)


@app.route("/bulb/<id>", methods=["DELETE"])
def bulb_delete(id):
    bulb = Bulb.query.get(id)
    if not bulb:
        abort(404)
    db.session.delete(bulb)
    db.session.commit()
    return bulbs_schema.jsonify(bulb)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='127.0.0.1')
