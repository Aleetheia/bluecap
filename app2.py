from flask import Flask, render_template, request, json
from flask.ext.mysql import MySQL
import MySQLdb as sql

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'b99b4e9fb9ac2b'
app.config['MYSQL_DATABASE_PASSWORD'] = '8cf9b237'
app.config['MYSQL_DATABASE_DB'] = 'heroku_8ed35d7a87fe1ad'
app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-iron-east-05.cleardb.net'
mysql.init_app(app)

@app.route("/")
def main():
    def load_data_from_mysql_to_rasp():
        from uuid import getnode as get_mac
        h = hex(get_mac())[2:].zfill(12)
        addr_mac = (":".join(i + j for i, j in zip(h[::2], h[1::2])))
        db = sql.connect(host='localhost', database='blue_captain', user='root', password='password')
        cursor = db.cursor()
        cursor.execute("UPDATE blue_captain.raspberries SET mac_address=%s WHERE registered=FALSE",[addr_mac])
        cursor.execute('SELECT num_desks FROM raspberries WHERE mac_address=%s',[addr_mac])
        results = cursor.fetchall()
        num_desks=[]
        for row in results:
            num_desks.append(row[0])
        cursor.execute("UPDATE blue_captain.raspberries SET registered=TRUE WHERE mac_address=%s",[addr_mac])
        db.commit()
        db.close()
        return num_desks[0]

    results = load_data_from_mysql_to_rasp()
    print(results)
    return render_template('index.html')

@app.route("/showShowRaspberry")
def showShowRaspberry():
    try:
        conn = mysql.connect()    
        cursor = conn.cursor()         
        cursor.callproc('show_raspberry')
        data = cursor.fetchall()
        
        return render_template('showRaspberry.html', data = data)
        
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

    #return render_template('showRaspberry.html')

@app.route("/showRaspberry",methods=['GET'])
def showRaspberry():
    try:
        conn = mysql.connect()    
        cursor = conn.cursor()         
        cursor.callproc('show_raspberry')
        #data = cursor.fetchall()
        print(load_data_from_mysql_to_rasp())

        return render_template('showRaspberry.html', data = data)
        
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/showAddRaspberry')
def showAddRaspberry():
    return render_template('addRaspberry.html')

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
            
            conn = mysql.connect()    
            cursor = conn.cursor()
            cursor.callproc('insert_raspberry',(_id,_country,_city,_building,_floor,_bench,_desks))
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'Raspberry ajouté !'})    
            else:
                return json.dumps({'error':str(data[0])})

            cursor.close() 
            conn.close()
        else:
                return json.dumps({'html':'<span>Des champs requis sont manquant</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
        
        
        
@app.route('/results')
def analysis():
    import pandas as pd
    import math as math
    import MySQLdb as sql

    def load_csv(csv_file):   
        df = pd.read_csv(csv_file,sep=';',names = ['Rasp', 'DateTime', 'Counter'])
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        return df

    def load_data_mysql():
        db_connection = sql.connect(host='localhost', database='blue_captain', user='root', password='password')
        df = pd.read_sql('SELECT rasp_id,date,counter FROM counter_values', con=db_connection)
        print(df)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def rates(nb_of_desks, data,frequency):
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
    
    
    
    
    
    

    

    