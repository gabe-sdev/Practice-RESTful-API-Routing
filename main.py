from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
# from flask.ext.restless import APIManager

#Initialize Flask app
app = Flask(__name__)


# Create DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        # dictionary = {}
        # # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     # Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


#Create DB tables
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(Cafe))
    # Use .scalars() to get the elements rather than entire rows from the database
    # and .all() to convert the Scalar results into a Python list
    all_cafes = result.scalars().all()
    ran_cafe = random.choice(all_cafes)
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=ran_cafe.to_dict())
    # return jsonify(Cafe={"id":ran_cafe.id,
    #                      "name":ran_cafe.name,
    #                      "map_url":ran_cafe.map_url,
    #                      "img_url":ran_cafe.img_url,
    #                      "location":ran_cafe.location,
    #                      "seats":ran_cafe.seats,
    #                      "has_toilet":ran_cafe.has_toilet,
    #                      "has_wifi":ran_cafe.has_wifi,
    #                      "has_sockets":ran_cafe.has_sockets,
    #                      "can_take_calls":ran_cafe.can_take_calls,
    #                      "coffee_price":ran_cafe.coffee_price
    #                      })


@app.route("/all")
def get_all_cafes():
    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(Cafe))
    # Use .scalars() to get the elements rather than entire rows from the database
    # and .all() to convert the Scalar results into a Python list
    all_cafes = result.scalars().all()
    # Loop through each cafe in the Cafe DB and convert the data in each row to a dictionary of key-value pairs.
    # josonify the new dictionaries
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def search_cafes():
    query_location = request.args.get("loc")
    # Construct a query to select from the database. Returns the rows in the database
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    # Use .scalars() to get the elements rather than entire rows from the database
    # and .all() to convert the Scalar results into a Python list
    all_cafes = result.scalars().all()
    # Loop through each cafe in the Cafe DB and convert the data in each row to a dictionary of key-value pairs.
    # josonify the new dictionaries
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    data = Cafe(
                name=request.form["name"],
                map_url=request.form["map_url"],
                img_url=request.form["img_url"],
                location=request.form["location"],
                seats=request.form["seats"],
                has_toilet=bool(request.form["has_toilet"]),
                has_wifi=bool(request.form["has_wifi"]),
                has_sockets=bool(request.form["has_sockets"]),
                can_take_calls=bool(request.form["can_take_calls"]),
                coffee_price=request.form["coffee_price"]
                )
    db.session.add(data)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>")
def update_price(cafe_id):
    u_price = request.args.get("new_price")
    if u_price:
        price_to_update = db.session.get(Cafe, cafe_id)
        price_to_update.coffee_price = u_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "test":
        cafe_to_remove = db.session.get(Cafe, cafe_id)
        db.session.delete(cafe_to_remove)
        db.session.commit()
        return jsonify(response={"success": "Successfully deleted the coffee shop."}), 200
    elif cafe_id > 22:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key"), 403


if __name__ == '__main__':
    app.run(debug=True)
