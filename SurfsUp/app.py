# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Home page
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        "Welcome to the Home page!<br><br>"
        "Here is a list of all available API routes:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br><br>"
        "Please include the start date and end date between the slashes:<br>"
        "/api/v1.0/<start><br>"
        "/api/v1.0/<start>/<end><br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    try:
        # Find the most recent date in the data set
        recent_date = session.query(func.max(measurement.date)).scalar()

        # Retrieve the last 12 months of precipitation data
        results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= func.date(recent_date, '-365 days')).all()

        # Convert the results to a dictionary
        precipitation_dict = {date: prcp for date, prcp in results}

        # Return the JSON representation of the dictionary
        return jsonify(precipitation_dict)
    finally:
        session.close()


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    try:
        # Query distinct station names
        stations = session.query(station.station, station.name).distinct().all()

        # Convert the results to a dictionary
        stations_dict = {station: name for station, name in stations}

        # Return the JSON representation of the dictionary
        return jsonify(stations_dict)
    finally:
        session.close()


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    try:
        results = session.query(measurement.date, measurement.tobs).filter(measurement.date > "2016-08-23").filter(measurement.station == 'USC00519281').all()

        all_tobs = []
        for date, tobs in results:
            all_tobs.append({"date": date, "tobs": tobs})

        return jsonify(all_tobs)
    finally:
        session.close()


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp(start, end=None):
    session = Session(engine)
    try:
        if end is None:
            end = "2017-08-23"  # Default end date

        # Min, max, and average temp for dates between start and end
        results = session.query(
            func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)
        ).filter(
            measurement.date >= start
        ).filter(
            measurement.date <= end
        ).all()

        temp_min, temp_avg, temp_max = results[0]

        # Prepare the data in dictionary format
        all_data = {
            "TMIN": temp_min,
            "TAVG": temp_avg,
            "TMAX": temp_max
        }

        # Return the JSONified result
        return jsonify(all_data)
    finally:
        session.close()


if __name__ == '__main__':
    app.run(debug=True)
