from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import time
import json


db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)

@app.route('/users', methods = ['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')
@app.route('/messages', methods = ['GET'])
def get_messages():
    session = db.getSession(engine)
    dbResponse = session.query(entities.Message)
    data = []
    for message in dbResponse:
        data.append(message)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')

@app.route('/messages/<id>', methods = ['GET'])
def get_message(id):
    db_session = db.getSession(engine)
    Messages = db_session.query(entities.Message).filter(entities.Message.id == id)
    for message in Messages:
        js = json.dumps(message, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    mensaje = { 'status': 404, 'message': 'Not Found'}
    return Response(mensaje, status=404, mimetype='application/json')


@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'
@app.route('/messages', methods = ['POST'])
def create_message():
    c =json.loads(request.form['values'])
    message = entities.Message(
        content=c['content'],
        user_from_id=c['user_from']['username']['id'],
        user_to_id=c['user_to']['username']['id']
    )
    session = db.getSession(engine)
    session.add(message)
    session.commit()
    return 'Created Message'
@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'
@app.route('/messages', methods = ['PUT'])
def update_message():
    session = db.getSession(engine)
    id = request.form['key']
    message = session.query(entities.Message).filter(entities.Message.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(message, key, c[key])
    session.add(message)
    session.commit()
    return 'Updated Message'
@app.route('/current', methods = ["GET"])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(
        entities.User.id == session['logged_user']
        ).first()
    return Response(json.dumps(
            user,
            cls=connector.AlchemyEncoder),
            mimetype='application/json'
        )

@app.route('/users', methods = ['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        session.delete(user)
    session.commit()
    return "Deleted User"
@app.route('/logout', methods = ["GET"])
def logout():
    session.clear()
    return render_template('index.html')

@app.route('/messages', methods = ['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(entities.Message.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted Message"

@app.route('/authenticate', methods = ["POST"])
def authenticate():
    time.sleep(3)
    message = json.loads(request.data)
    username = message['username']
    password = message['password']
    #2. look in database
    db_session = db.getSession(engine)
    try:
        user = db_session.query(entities.User
            ).filter(entities.User.username == username
            ).filter(entities.User.password == password
            ).one()
        session['logged_user'] = user.id
        message = {'message': 'Authorized'}
        return Response(message, status=200, mimetype='application/json')
    except Exception:
        message = {'message': 'Unauthorized'}
        return Response(message, status=401, mimetype='application/json')
@app.route('/messages/<user_from_id>/<user_to_id>', methods = ['GET'])
def get_messagefrom(user_from_id, user_to_id ):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == user_from_id).filter(
        entities.Message.user_to_id == user_to_id
    )
    message2 = db_session.query(entities.Message).filter(
        entities.Message.user_to_id == user_from_id).filter(
        entities.Message.user_from_id == user_to_id
    )
    data = []
    for message in messages:
        data.append(message)
    for message in message2:
        data.append(message)
    n = len(data)
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            if data[j].id > data[j + 1].id:
                data[j], data[j + 1] = data[j + 1], data[j]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/gabriel/messages', methods=["POST"])
def create_messageto():
    data = json.loads(request.data)
    user_to_id = data['user_to_id']
    user_from_id = data['user_from_id']
    content = data['content']

    message = entities.Message(
        user_to_id=user_to_id,
        user_from_id=user_from_id,
        content=content)

# 2. Save in database
    db_session = db.getSession(engine)
    db_session.add(message)
    db_session.commit()

    response = {'message': 'created'}
    return Response(json.dumps(response, cls=connector.AlchemyEncoder), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.secret_key = ".."
    app.run(debug=True,port=5000, threaded=True, host=('127.0.0.21'))
