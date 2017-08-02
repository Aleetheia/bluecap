from flask import Flask, render_template, request, json
#from flask.ext.mysql import MySQL
import MySQLdb as sql

#mysql = MySQL()
app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')


#@app.route("/showShowRaspberry")
#def showShowRaspberry():
    #return render_template('showRaspberry.html')

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

#@app.route('/showAddRaspberry')
#def showAddRaspberry():
    #return render_template('addRaspberry.html')


@app.route('/showAddRaspberry',methods=['POST'])
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
            if len(data) is 0:
                db.commit()
                return render_template('addRaspberry.html')
                #return json.dumps({'message':'Raspberry ajouté !'})    
            else:
                return json.dumps({'error':str(data[0])})
            cursor.close()
            db.close()

        else:
                return json.dumps({'html':'<span>Des champs requis sont manquant</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
        
        
        
@app.route('/results')
def analysis():
    import pandas as pd
    import math as math
    import MySQLdb as sql

    def load_data_mysql():
        db_connection = sql.connect(host='us-cdbr-iron-east-05.cleardb.net', database='heroku_8ed35d7a87fe1ad', user='b99b4e9fb9ac2b', password='8cf9b237')
        df = pd.read_sql('SELECT rasp_id,date,counter FROM counter_values', con=db_connection)
        print(df)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def rates(nb_of_desks, data, frequency):
        df = data.set_index('date').resample(frequency)['counter'].max()
        df = df.fillna(0)
        taux=[]
        if(frequency == 'C'):  
             taux.append(math.ceil(100*((df.sum()/df.astype(bool).sum(axis=0))/nb_of_desks)))
        else: 
            for x in range(len(df)):
                taux.append(math.ceil(100*((df[x].sum()/nb_of_desks))))
        return(taux) 

    def display_rates(taux):    
        for x in range(len(taux)):
            print('{} % de taux d\'occupation'.format(taux[x]))
        print('------------------------')   

    data = load_data_mysql()

    #display_rates(rates(16, data, 'H'))
    #display_rates(rates(16, data, 'D'))
    res =('{} % de taux d\'occupation'.format(rates(16, data, 'C')))
    return render_template("results.html", res=res)       

if __name__ == "__main__":
    app.run()
    
    
    
    
    
    

    

    