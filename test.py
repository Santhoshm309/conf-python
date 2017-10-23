from flask import Flask,request,jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS



app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Santi_39'
app.config['MYSQL_DB'] = 'conf'
CORS(app)


mysql = MySQL(app)


def construct_response(code, message, data):
    return {'code' : code, 'message': message, 'data': data}

@app.route('/test', methods=['POST'])
def hello_world():
    if request.method == 'POST':
        try:
            cur = mysql.connection.cursor()
            content =  request.json['data']
            print('Success')
            message = { 'code': 'Success'}
            return jsonify(message)
        except Exception as e:
            return jsonify(str(e))



@app.route('/signup', methods=['POST'])
def signup():
    try :
        conn = mysql.connect
        cur = conn.cursor()
        request_data = request.json['data']
        if request_data['email'] and request_data['password'] and request_data['name']:
            query = """INSERT INTO users(name, email, password,role) VALUE ( %s, %s, %s, %s)"""
            print(query)
            cur.execute(query,(str(request_data['name']),str(request_data['email']), str(request_data['password']), 'user'))
            conn.commit()
            return jsonify(construct_response(200, 'OK', 0))
        else:
            return jsonify(construct_response(400, 'Data Incomplete', 0)), 400


    except Exception as e:
        code, message = e.args
        return jsonify(construct_response(code, message, str(e))), 500





@app.route('/login', methods=['POST'])
def signin():
    try:
        conn = mysql.connect
        cur = conn.cursor()
        request_data = request.json['data']
        if request_data['email'] and request_data['password']:
            query = """SELECT * from users WHERE email = %s"""
            cur.execute(query,[request_data['email']])
            db_data = [dict((cur.description[i][0], value)
                            for i, value in enumerate(row)) for row in cur.fetchall()]
            user_data = {'role': db_data[0]['role'], 'uid': db_data[0]['id']}
            if len(db_data)> 0 and db_data[0]['password'] == request_data['password']:
                return jsonify(construct_response(200, 'OK', user_data))
            else:
                return jsonify(construct_response(401, 'Unauthorized',   0)), 401
        else:
            return jsonify(construct_response(400,'Improper data', 0)), 400
    except Exception as e:
        return jsonify(construct_response(500, str(e), 0)), 500




@app.route('/conference', methods=['POST', 'GET'])
def conference():
    try:
        conn = mysql.connect
        cur = conn.cursor()
        if request.method == 'GET':
            query = """select name, venue, judge, id from conferences"""
            cur.execute(query)
            db_data = [dict((cur.description[i][0], value)
                            for i, value in enumerate(row)) for row in cur.fetchall()]

            return jsonify(construct_response(200, 'OK', db_data))
        elif request.method == 'POST':
            request_data = request.json['data']
            if request_data['name']  and request_data['category'] and request_data['judge'] and request_data['venue'] and request_data['eventdate'] and request_data['description']:
                query = """INSERT INTO conferences(name, category, judge, venue, eventdate, description) VALUE( %s, %s, %s , %s, %s, %s)"""
                cur.execute(query,(request_data['name'] , request_data['category'] , request_data['judge'] , request_data['venue'] , request_data['eventdate'], request_data['description']))
                conn.commit()
                return jsonify(construct_response(200, 'OK', 0)), 200


    except Exception as e:
        return jsonify(construct_response(500, str(e), 0)), 500

@app.route('/conference/<cid>', methods=['GET'])
def conf_details(cid):
    try:
        conn= mysql.connect
        cur = conn.cursor()
        query = """SELECT co.name as name,co.description as description ,co.venue as venue, co.judge as judge, co.category as category \
                  , co.eventdate as eventdate, co.user_count as user_count, u.name as user_name  from conferences co \
                              left join user_conf_map  ucm on ucm.conf_id = co.id \
                              left join users u on ucm.user_id = u.id where co.id = %s"""
        cur.execute(query, [cid])
        db_data = [dict((cur.description[i][0], value)
                        for i, value in enumerate(row)) for row in cur.fetchall()]

        username = []
        final_db_data = {}
        if len(db_data) > 0:
            final_db_data = db_data[0]
        for item in db_data:
            username.append(item['user_name'])
        final_db_data['user_name'] = username

        return jsonify(construct_response(200, 'OK', final_db_data))
    except Exception as e:
        return jsonify(construct_response(500, 'Unfortunate Error', str(e)))





@app.route('/conference/register', methods=['POST'])
def register():
    try:
        conn = mysql.connect
        cur = conn.cursor()
        query = """SELECT user_count from conferences where id = %s"""
        request_data = request.json['data']
        cur.execute(query, [request_data['conf_id']])
        db_data = [dict((cur.description[i][0], value)
                        for i, value in enumerate(row)) for row in cur.fetchall()]
        if int(db_data[0]['user_count']) < 5:
            query = """INSERT INTO user_conf_map(user_id, conf_id) VALUE(%s, %s)"""
            cur.execute(query, (request_data['user_id'], request_data['conf_id']))
            conn.commit()
            query = """UPDATE  conferences SET user_count = %s where id = %s"""
            cur.execute(query,(db_data[0]['user_count'] + 1, request_data['conf_id']))
            conn.commit()
            return jsonify(construct_response(200, 'OK', 0))
        else:
            return jsonify(construct_response(400, 'Conference Full', 0)), 400

    except Exception as e:
        code, message  = e.args
        return jsonify(construct_response(code, message, str(e))), 500



@app.route('/conference/user/<user_id>')
def get_conference_list(user_id):
    try:
        conn = mysql.connect
        cur = conn.cursor()
        query = """SELECT co.name as name,co.id as id,  co.venue as venue, co.judge as judge, co.eventdate as eventdate from \
                    users u left join user_conf_map ucm ON u.id = ucm.user_id 
                    join conferences co on co.id= ucm.conf_id where u.id = %s"""
        cur.execute(query, [user_id])
        db_data = [dict((cur.description[i][0], value)
                        for i, value in enumerate(row)) for row in cur.fetchall()]

        return jsonify(construct_response(200, 'OK', db_data))
    except Exception as e:
        return jsonify(construct_response(500, 'Something went wrong', str(e))), 500
