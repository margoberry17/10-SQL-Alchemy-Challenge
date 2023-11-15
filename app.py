# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Hawaii Climate App<br/><br/>"
        f"Available api Routes:<br/><br/>"
        f"Daily Precipitation Totals for last year: <br/> /api/v1.0/precipitation<br/><br/>"
        f"Weather Stations: <br/> /api/v1.0/stations<br/><br/>"
        f"Daily Temperature Observations for Station USC00519281 for last year: <br/> /api/v1.0/tobs<br/><br/>"
        f"Minimum, Maximum, & Average Temperatures for a given date: <br/> /api/v1.0/YYYY-MM-DD<br/><br/>"
        f"Minimum, Maximum, & Average Temperatures for a given date range: <br/> /api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """Retrieve the last 12 months of precipitation data"""
    # Query all percipitation
    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).\
        filter(Measurement.date >= dt.date(2016,8,23)).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list
    precipitation_list = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)

    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Return a JSON list of stations from the dataset
    stations_list = []
    for station, name in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_list.append(stations_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temperatures():
    session = Session(engine)

    # Query dates and temp observations of most-active station for the previous year of data.
    results = session.query(Measurement.tobs, Measurement.date).\
        filter(Measurement.station == "USC00519281").\
        order_by(Measurement.date).\
        filter(Measurement.date > dt.date(2016,8,23)).all()
    
    session.close()

   # Return a JSON list of temperature observations for the previous year.
    temp_list = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_list.append(temp_dict)
    
    return jsonify(temp_list)
    
#For a specified start, calculate TMIN, TAVG, and TMAX 
#for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    session = Session(engine)

    # Query start date
    start_date = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).all()
    
    session.close()

    # Convert to List
    start_date_list = list(np.ravel(start_date))
    
    # Return a JSON list
    return jsonify(start_date_list)

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX 
#for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end_dates(start, end):
    
    session = Session(engine)

    # Query start and end date
    start_end_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        group_by(Measurement.date).all()
    
    session.close()

    # Convert to List
    start_end_dates_list = list(np.ravel(start_end_dates))
    
    # Return a JSON list
    return jsonify(start_end_dates_list)


if __name__ == '__main__':
     app.run()