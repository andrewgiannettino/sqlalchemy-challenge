# Import the dependencies.
import numpy as np
import datetime as dt
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
Base.classes.keys()
M = Base.classes.measurement
S = Base.classes.station

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
    """List All Avalible Routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/Tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
        )

#Query for precipitation

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Precipitation data"""
    
    precipitation_results = session.query(M.prcp,M.date).filter(M.date > "2016-08-23").all()
    session.close()
    
    
    
    precipitaton_values = []
    for prcp, date in precipitation_results:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict["date"] = date
        precipitaton_values.append(precipitation_dict)

    return jsonify(precipitaton_values)

#Query for stations

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    """List of Stations"""
    
    results = session.query(S.station, S.name).all()
    session.close()
    
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


#Query for tobs over last 12 months for most active station
@app.route("/api/v1.0/tobs") 
def tobs():
    session = Session(engine)
    
    """TOBS for most active station over last 12 months"""
    
    last_year_results = session.query(M.date).\
        order_by(M.date.desc()).first() 


    
    last_year_values = []
    for date in last_year_results:
        last_year_dict = {}
        last_year_dict["date"] = date
        last_year_values.append(last_year_dict) 


    start_date = dt.date(2017, 8, 23)-dt.timedelta(days =365) 
   

    active_station= session.query(M.station, func.count(M.station)).\
        order_by(func.count(M.station).desc()).\
        group_by(M.station).first()
    most_active_station = active_station[0] 

    session.close() 

    dates_tobs_last_year_results = session.query(M.date, M.tobs, M.station).\
        filter(M.date > start_date).\
        filter(M.station == most_active_station) 
    

    dates_tobs_last_year_values = []
    for date, tobs, station in dates_tobs_last_year_results:
        dates_tobs_dict = {}
        dates_tobs_dict["date"] = date
        dates_tobs_dict["tobs"] = tobs
        dates_tobs_dict["station"] = station
        dates_tobs_last_year_values.append(dates_tobs_dict)
        
    return jsonify(dates_tobs_last_year_values) 


#start

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine) 

    

    start_date_tobs_results = session.query(func.min(M.tobs),func.avg(M.tobs),func.max(M.tobs)).\
        filter(M.date >= start).all()
    
    session.close() 

    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["avreage"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)



#Start End

@app.route("/api/v1.0/<start>/<end>")

def Start_end_date(start, end):
    session = Session(engine)

    
    

    start_end_date_tobs_results = session.query(func.min(M.tobs), func.avg(M.tobs), func.max(M.tobs)).\
        filter(M.date >= start).\
        filter(M.date <= end).all()

    session.close()
  
    start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict) 
    

    return jsonify(start_end_tobs_date_values)
    
    
if __name__ == "__main__":
    app.run()

    