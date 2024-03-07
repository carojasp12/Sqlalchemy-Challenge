# Import the dependencies.

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text,inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"Welcome to SurfsUp<br/><br/>"
        f"Please take a look of the available routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"date format:(YYYY-MM-DD)<br/>"
        f"/api/v1.0/start_date<br/>"  
        f"/api/v1.0/start_date/end_date"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all precipitation for the last 12 months
    mr_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    oy_date = dt.datetime.strptime(mr_date,'%Y-%m-%d') - dt.timedelta(days=366)
   
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= oy_date)

    session.close()

    # Create a dictionary from the row data and append to a list of all precipitation

    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)

    #Return the JSON representation of your dictionary
    return jsonify(all_precipitation)


@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations
    results = session.query(measurement.station).distinct().all()
    session.close()

    #Return a JSON list of stations from the dataset
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route('/api/v1.0/tobs')
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)
  
    mr_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    oy_date = dt.datetime.strptime(mr_date,'%Y-%m-%d') - dt.timedelta(days=366)

    tn_stations = session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    m = tn_stations[0]
    ma_station_id = m[0]
    

    results = session.query(measurement.date,measurement.tobs).\
    filter(measurement.station == ma_station_id).filter(measurement.date >= oy_date).all()

    session.close()

    #Return a JSON list of temperature observations for the previous year.
    all_names = list(np.ravel(results))
    return jsonify(all_names)


 

@app.route('/api/v1.0/<start_date>')
def start(start_date):
    session = Session(engine)
    #Query the minimum temperature, the average temperature, and the maximum temperature and 
    #Filter for a specified start range
    sel = [func.min(measurement.tobs), 
       func.max(measurement.tobs), 
       func.avg(measurement.tobs), 
       ]
    results = session.query(*sel).\
    filter(measurement.date >= start_date).all()
    session.close()

    #Return a JSON list
    all_names = list(np.ravel(results))
    return jsonify(all_names)

    
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)
     #Query the minimum temperature, the average temperature, and the maximum temperature and
     #Filter for a specified start-end range.
    sel = [func.min(measurement.tobs), 
       func.max(measurement.tobs), 
       func.avg(measurement.tobs), 
       ]
    results = session.query(*sel).\
    filter(measurement.date >= start).\
    filter(measurement.date <= end).all()
    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names)


if __name__ == '__main__':
    app.run(debug=True)