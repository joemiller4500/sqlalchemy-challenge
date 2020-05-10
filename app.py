# Import components

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify, request, Response

# Setup Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measure = Base.classes.measurement
Station = Base.classes.station

# Create an app, being sure to pass __name__
app = Flask(__name__)

# 3. Define what to do when a user hits the index route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Weather API.<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations/<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session link
    session = Session(engine)

    year_ago = session.query(func.strftime("%m, %d %Y", Measure.date)).\
        order_by(desc(Measure.date)).offset(365).limit(1).all()
    year_ago = year_ago[0]
    year_ago

    last_year = session.query(Measure.date, Measure.prcp).\
        filter(func.strftime("%Y-%m-%d", Measure.date) > '2016-08-23').all()

    session.close()

    results = []
    for date, prcp in last_year:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        results.append(prcp_dict)
    
    return jsonify(results)

@app.route("/api/v1.0/stations")
def stations():
    # Create session link
    session = Session(engine)

    sel = [Measure.station, func.count(Measure.date)]
    station_counts = session.query(*sel).\
        group_by(Measure.station).\
        order_by(desc(func.count(Measure.date))).all()

    session.close()

    results = []
    for station, count in station_counts:
        station_dict = {}
        station_dict["station"] = station
        station_dict["count"] = count
        results.append(station_dict)
    
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session link
    session = Session(engine)

    last_year = session.query(Measure.date, Measure.tobs).\
        filter(func.strftime("%Y-%m-%d", Measure.date) > '2016-08-23').\
        filter(Measure.station == 'USC00519281').all()

    session.close()

    results = []
    for date, tobs in last_year:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        results.append(tobs_dict)
    
    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start_stats(start):

    # Create session link
    session = Session(engine)
    sel = [func.max(Measure.tobs)]
    high = session.query(*sel).\
        filter(Measure.station == 'USC00519281').\
        filter(Measure.date > start).all()

    sel = [func.min(Measure.tobs)]
    low = session.query(*sel).\
        filter(Measure.station == 'USC00519281').\
        filter(Measure.date > start).all()

    sel = [func.avg(Measure.tobs)]
    mean = session.query(*sel).\
        filter(Measure.station == 'USC00519281').\
        filter(Measure.date > start).all()

    session.close()

    results = []
    start_dict = {}
    start_dict["high"] = high
    start_dict["low"] = low
    start_dict["avg"] = mean
    results.append(start_dict)

    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end_stats(start, end):

    # Create session link
    session = Session(engine)
    sel = [func.max(Measure.tobs)]
    high = session.query(*sel).\
        filter(Measure.station == 'USC00519281').\
        filter(Measure.date > start).\
        filter(Measure.date < end).all()

    sel = [func.min(Measure.tobs)]
    low = session.query(*sel).\
        filter(Measure.station == 'USC00519281').\
        filter(Measure.date > start).\
        filter(Measure.date < end).all()

    sel = [func.avg(Measure.tobs)]
    mean = session.query(*sel).\
        filter(Measure.station == 'USC00519281').\
        filter(Measure.date > start).\
        filter(Measure.date < end).all()

    session.close()

    results = []
    start_end_dict = {}
    start_end_dict["high"] = high
    start_end_dict["low"] = low
    start_end_dict["avg"] = mean
    results.append(start_end_dict)

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
