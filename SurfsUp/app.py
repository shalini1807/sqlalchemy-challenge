# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
# Flask Setup
app = Flask(__name__)
# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve the last 12 months of precipitation data and convert to a dictionary."""
    try:
        most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        one_year_ago = datetime.datetime.strptime(most_recent_date, "%Y-%m-%d") - datetime.timedelta(days=365)
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
        precipitation_dict = {date: prcp for date, prcp in results}
        return jsonify(precipitation_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    results = session.query(Station.station).all()
    station_list = [station[0] for station in results]
    return jsonify(station_list)
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year from the most active station."""
    most_active_station = session.query(Measurement.station).group_by(Measurement.station)\
                                .order_by(func.count(Measurement.station).desc()).first()[0]
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = datetime.datetime.strptime(most_recent_date, "%Y-%m-%d") - datetime.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station)\
                     .filter(Measurement.date >= one_year_ago).all()
    temperature_data = [{"date": date, "temperature": tobs} for date, tobs in results]
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return the minimum, average, and maximum temperatures for all dates >= start date."""
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs))\
                     .filter(Measurement.date >= start).all()
    tmin, tavg, tmax = results[0]
    temp_data = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return the minimum, average, and maximum temperatures for dates between the start and end dates (inclusive)."""
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs))\
                     .filter(Measurement.date >= start)\
                     .filter(Measurement.date <= end).all()
    tmin, tavg, tmax = results[0]
    temp_data = {
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    }
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)


