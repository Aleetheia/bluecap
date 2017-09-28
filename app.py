from flask import Flask, render_template, request, json, flash, session, redirect, url_for 
import MySQLdb as sql
import pandas as pd
import math as math
import numpy as np
    
app = Flask(__name__)
app.secret_key = 'TEST'
app.config['SESSION_TYPE'] = 'filesystem'

#@app.route("/")
#def main():
    #return render_template('index.html')

@app.route("/")
def main():
    import pandas as pd
    import math as math

    def load_data_mysql():
        db_connection = sql.connect(host='us-cdbr-iron-east-05.cleardb.net', database='heroku_8ed35d7a87fe1ad', user='b99b4e9fb9ac2b', password='8cf9b237')
        df = pd.read_sql('SELECT rasp_id,date,counter FROM counter_values', con=db_connection)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def rates(nb_of_desks, data, frequency):
        df = data.set_index('date').resample(frequency)['counter'].max()
        df = df.fillna(0)
        dfs= df.to_frame()
        taux=[]
        
        if(frequency == 'C'):  
             taux.append(math.ceil(100*((df.sum()/df.astype(bool).sum(axis=0))/nb_of_desks)))
        else: 
            for x in range(len(df)):
                taux.append(math.ceil(100*((df[x].sum()/nb_of_desks))))
        
        return(taux, dfs) 

    def display_rates(taux):    
        for x in range(len(taux)):
            print('{} % de taux d\'occupation'.format(taux[x]))
        print('------------------------')   

    data = load_data_mysql()

    #display_rates(rates(16, data, 'H'))
    #display_rates(rates(16, data, 'D'))
    #taux, df = rates(16, data, 'C')
    #dft=df.to_html()
    #res =('{} % de taux d\'occupation'.format(taux))
    
    
    taux, df = rates(16, data, 'D')
    dfa =((df.index).to_datetime()).strftime('%Y-%m-%d')
    d = dict(zip(dfa, taux))
    return render_template("index.html", res=d)       
    
    
@app.route("/showShowRaspberry",methods=['GET'])
def showRaspberry():
    try:
        db = sql.connect(host='us-cdbr-iron-east-05.cleardb.net', database='heroku_8ed35d7a87fe1ad', user='b99b4e9fb9ac2b', password='8cf9b237')   
        cursor = db.cursor()     
        cursor.callproc('show_raspberry')
        data = cursor.fetchall()
        return render_template('showRaspberry.html', data = data)
        
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        db.close()

@app.route('/showAddRaspberry')
def showAddRaspberry():
    return render_template('addRaspberry.html')


@app.route('/plotResults')
def plotResults():
    import plotly.plotly as py
    import plotly.graph_objs as go

    fig = {
  "data": [
    {
      "values": [16, 15, 12, 6, 5, 4, 42],
      "labels": [
        "US",
        "China",
        "European Union",
        "Russian Federation",
        "Brazil",
        "India",
        "Rest of World"
      ],
      "domain": {"x": [0, .48]},
      "name": "GHG Emissions",
      "hoverinfo":"label+percent+name",
      "hole": .4,
      "type": "pie"
    },     
    {
      "values": [27, 11, 25, 8, 1, 3, 25],
      "labels": [
        "US",
        "China",
        "European Union",
        "Russian Federation",
        "Brazil",
        "India",
        "Rest of World"
      ],
      "text":"CO2",
      "textposition":"inside",
      "domain": {"x": [.52, 1]},
      "name": "CO2 Emissions",
      "hoverinfo":"label+percent+name",
      "hole": .4,
      "type": "pie"
    }],
  "layout": {
        "title":"Global Emissions 1990-2011",
        "annotations": [
            {
                "font": {
                    "size": 20
                },
                "showarrow": False,
                "text": "GHG",
                "x": 0.20,
                "y": 0.5
            },
            {
                "font": {
                    "size": 20
                },
                "showarrow": False,
                "text": "CO2",
                "x": 0.8,
                "y": 0.5
            }
        ]
    }}
    figpy = py.iplot(fig, filename='donut')
    return render_template("plotResults.html", fig=figpy)

@app.route('/addRaspberry',methods=['POST'])
def addRaspberry():
    try:
        _id = request.form['inputId']
        _country = request.form['inputCountry']
        _city = request.form['inputCity']
        _building = request.form['inputBuilding']
        _floor = request.form['inputFloor']
        _bench = request.form['inputBench']
        _desks = request.form['inputDesks']   
    
        if _id and _country and _city and _building and _floor and _bench and _desks:
                      
            db = sql.connect(host='us-cdbr-iron-east-05.cleardb.net', database='heroku_8ed35d7a87fe1ad', user='b99b4e9fb9ac2b', password='8cf9b237')   
            cursor = db.cursor()         
            cursor.callproc('insert_raspberry',(_id,_country,_city,_building,_floor,_bench,_desks))
            data = cursor.fetchall()
            db.commit()
            db.close()
            return json.dumps({'Raspberry ajouté !'})
        
        else:
            return json.dumps({'html':'<span>Des champs requis sont manquant</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    
if __name__ == "__main__":
    app.run()
    
    
    
    
    
    

    

    