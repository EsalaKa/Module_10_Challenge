# Import the dependencies.

from flask import Flask, jsonify
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from climate_starter import Measurement
import datetime

# Create a Flask app
app = Flask(__name__)

# SQLite database connection
engine = create_engine('sqlite:///hawaii.sqlite')

# Create a session
session = Session(engine)



# Define available routes
@app.route('/')
def home():
    return (
        "Welcome to the Weather API!<br/>"
        "Here are the available routes:<br/>"
        "<strong>/api/v1.0/precipitation</strong>: Precipitation data for the last 12 months.<br/>"
        "<strong>/api/v1.0/stations</strong>: List of weather stations.<br/>"
        "<strong>/api/v1.0/tobs</strong>: Temperature observations for the most active station.<br/>"
        "<strong>/api/v1.0/<start></strong>: Temperature statistics from a start date.<br/>"
        "<strong>/api/v1.0/<start>/<end></strong>: Temperature statistics for a date range."
    )

# Define a route: precipitation data for the last 12 months
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the last date in the database
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary
    precipitation_data = {date: p for date, precipitation in results}

    return jsonify(precipitation_data)

# Define a route: list of weather stations
@app.route('/api/v1.0/stations')
def stations():
    # Query all stations from the database
    station_results = session.query(Measurement.station).all()

    # Convert the list of station results
    station_names = [station[0] for station in station_results]

    return jsonify(station_names)

# Define a route: temperature observations, 12 months most active
@app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year ago from the last date
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Find the most active station in the last 12 months
    most_active_station = session.query(Measurement.station, func.count(Measurement.tobs)).filter(
        Measurement.date >= one_year_ago
    ).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).first()

    # Query temperature observations for the last 12 months for the most active station
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.date >= one_year_ago,
        Measurement.station == most_active_station[0]
    ).all()

    # Create a list of temperature observations
    temperature_observations = [{"date": date, "tobs": tobs} for date, tobs in tobs_results]

    return jsonify(temperature_observations)

# Define a route to get temperature statistics
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temperature_stats(start, end=None):
    # Convert start and end to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d') if end else None

    # Query temperature statistics
    if end_date:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(
            Measurement.date >= start_date,
            Measurement.date <= end_date
        ).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(
            Measurement.date >= start_date
        ).all()

    # Create a dictionary of temperature statistics
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temperature_stats)


if __name__ == '__main__':
    app.run(debug=True)
