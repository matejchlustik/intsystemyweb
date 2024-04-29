from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask import render_template
from sqlalchemy import create_engine
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import random

app = Flask(__name__)

# MySQL configurations
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "wifishield"

mysql = MySQL(app)


model = joblib.load("hourly_temperature_forest_regressor.joblib")
# IMPORT DAT
# df = pd.read_csv("data_to_db.csv")

# def create_table_and_insert():
#     engine = create_engine("mysql://{}:{}@localhost/{}".format(app.config['MYSQL_USER'], app.config['MYSQL_PASSWORD'], app.config['MYSQL_DB']))
# #     #sql_create = 'CREATE TABLE IF NOT EXISTS weather_prediction (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,hour INT,temp FLOAT,temp_before_1 FLOAT,temp_before_2 FLOAT,temp_before_3 FLOAT,temp_before_4 FLOAT,temp_before_5 FLOAT,temp_before_6 FLOAT,temp_before_7 FLOAT,temp_before_8 FLOAT,temp_before_9 FLOAT,temp_before_10 FLOAT,temp_before_11 FLOAT,temp_before_12 FLOAT,temp_before_13 FLOAT,temp_before_14 FLOAT,temp_before_15 FLOAT,temp_before_16 FLOAT,temp_before_17 FLOAT,temp_before_18 FLOAT,temp_before_19 FLOAT,temp_before_20 FLOAT,temp_before_21 FLOAT,temp_before_22 FLOAT,temp_before_23 FLOAT);'

#     #Insert data
#     df.to_sql('weather_prediction', con=engine, if_exists='append', index=False)
# create_table_and_insert()
# @app.route('/')
# def index(name=None):
#     create_table_and_insert()
#     return 'DataFrame imported to MySQL!'

# return render_template('index.html', name=name)


@app.route("/")
def index(name=None):
    cur = mysql.connection.cursor()

    cur.execute("SELECT id, hour, temp FROM ( SELECT id, hour, temp FROM weather_prediction ORDER BY id DESC LIMIT 25 ) AS subquery ORDER BY id ASC;")

    data = cur.fetchall()
    labels = [row[1] for row in data]  # Extract hour values
    temp_data = [row[2] for row in data]  # Extract temp values

    cur.close()
    return render_template('index.html', labels=labels, temp_data=temp_data)


@app.route("/arduino/<temperature>")
def get_temperature(temperature):
    temperature = float(temperature)

    cur = mysql.connection.cursor()
    cur.execute(f"INSERT INTO senzor_data (temperature) VALUES ({temperature})")
    mysql.connection.commit()
    cur.execute("SELECT id, temp FROM weather_prediction ORDER BY id DESC LIMIT 1 OFFSET 24;")
    record_id = cur.fetchone()
    pred_temp = record_id[1]
    first_id = record_id[0]
    future_temp = [temperature]
    cur.execute(
        f"UPDATE weather_prediction SET temp = {temperature} WHERE id = {record_id[0]};"
    )
    cur.execute("SELECT id FROM `senzor_data` ORDER BY id DESC LIMIT 1 OFFSET 1;")
    senzor_data_record = cur.fetchone()
    id_senzor_data = senzor_data_record[0]
    cur.execute(f"UPDATE senzor_data SET temperature_pred = {pred_temp} WHERE id = {id_senzor_data}")
    mysql.connection.commit()
    for i in range(23,0,-1):
        for j in range(i,0,-1):
            cur.execute(f"UPDATE weather_prediction SET temp_before_{j} = {future_temp[0]} WHERE id = {first_id+j}")
            
        
        cur.execute(f"SELECT id, hour, temp, temp_before_1, temp_before_2, temp_before_3, temp_before_4, temp_before_5, temp_before_6, temp_before_7, temp_before_8, temp_before_9,  temp_before_10, temp_before_11, temp_before_12, temp_before_13, temp_before_14, temp_before_15, temp_before_16, temp_before_17, temp_before_18, temp_before_19, temp_before_20, temp_before_21, temp_before_22, temp_before_23 FROM weather_prediction WHERE id = {first_id}")
        first_id += 1
        # Fetch the last row
        row = cur.fetchone()
        columns = [desc[0] for desc in cur.description]
    
        # # Convert the row to DataFrame
        df = pd.DataFrame([row],columns=columns)
        df = df.drop(["id"], axis=1)
        df = df.drop(["temp"], axis=1)
        future_temp = model.predict(df)
        cur.execute(f"UPDATE weather_prediction SET temp = {future_temp[0]} WHERE id = {first_id};")
        mysql.connection.commit()
    cur.execute(f"SELECT id, hour, temp, temp_before_1, temp_before_2, temp_before_3, temp_before_4, temp_before_5, temp_before_6, temp_before_7, temp_before_8, temp_before_9, temp_before_10, temp_before_11, temp_before_12, temp_before_13, temp_before_14, temp_before_15, temp_before_16, temp_before_17, temp_before_18, temp_before_19, temp_before_20, temp_before_21, temp_before_22, temp_before_23 FROM weather_prediction ORDER BY id DESC LIMIT 1")
    
    row = cur.fetchone()
    columns = [desc[0] for desc in cur.description]

    # Convert the row to DataFrame
    df = pd.DataFrame([row],columns=columns)
    df = df.drop(["id"], axis=1)
    temp = df["temp"].iloc[0]
    df = df.drop(["temp"], axis=1)
    def getHour(last_hour):
        if last_hour == 23:
            newHour = 0
        else:
            newHour = last_hour + 1
        return newHour
    hour = getHour(df["hour"].iloc[0])
    future_temp = model.predict(df)
    data = (
        hour,
        future_temp[0],
        temp,
        df['temp_before_1'].iloc[0],
        df['temp_before_2'].iloc[0],
        df['temp_before_3'].iloc[0],
        df['temp_before_4'].iloc[0],
        df['temp_before_5'].iloc[0],
        df['temp_before_6'].iloc[0],
        df['temp_before_7'].iloc[0],
        df['temp_before_8'].iloc[0],
        df['temp_before_9'].iloc[0],
        df['temp_before_10'].iloc[0],
        df['temp_before_11'].iloc[0],
        df['temp_before_12'].iloc[0],
        df['temp_before_13'].iloc[0],
        df['temp_before_14'].iloc[0],
        df['temp_before_15'].iloc[0],
        df['temp_before_16'].iloc[0],
        df['temp_before_17'].iloc[0],
        df['temp_before_18'].iloc[0],
        df['temp_before_19'].iloc[0],
        df['temp_before_20'].iloc[0],
        df['temp_before_21'].iloc[0],
        df['temp_before_22'].iloc[0]
    )
    query = "INSERT INTO weather_prediction (hour, temp, temp_before_1, temp_before_2, temp_before_3, temp_before_4, temp_before_5, temp_before_6,  temp_before_7, temp_before_8, temp_before_9,   temp_before_10,  temp_before_11,   temp_before_12,  temp_before_13,   temp_before_14,   temp_before_15,   temp_before_16,   temp_before_17,   temp_before_18,   temp_before_19,   temp_before_20,   temp_before_21,   temp_before_22,  temp_before_23) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(query, data)
    mysql.connection.commit()

    cur.close()

    return "Success"


if __name__ == "__main__":
    app.run()
