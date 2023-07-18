
import argparse
import json
import cv2
import numpy as np
import os, uuid
from tqdm import tqdm

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from background_retrieval import bk_img_retrieval
from utils.font_utils import PutText2Image

from model.distrib_model import LayoutsDistribModel
from model.layout_model import BBoxesRegModel

from layout_distribution_predict import smooth_region_dectection, get_distrib_mask
from layout_refine import get_batch_text_region, get_bbox_mask, get_refine_bboxes

####################################
from base64 import encodebytes
from PIL import Image
import random, io, datetime
from slugify import slugify

from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

from base64 import encodebytes
from PIL import Image
import random, io

app = Flask(__name__)

#cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"*": {"origins": "*"}})

conexion = MySQL(app)

@app.route('/ping', methods=['GET'])
def ping():
    print("ping pong")
    response = jsonify({'status': 'estado', 'message': "ping"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    try:
        print(request.json)
        cursor = conexion.connection.cursor()
        username = request.json['user']
        password = request.json['password']
        sql = """SELECT * FROM users WHERE username = '{0}'""".format(username)
        cursor.execute(sql)
        dato = cursor.fetchone()
        if dato != None:
            # existe el usuario, verificar contraseña
            if dato[2] == password:
                # correcto
                token = uuid.uuid4()
                user = {'id': dato[0], 'username': dato[1]}
                return jsonify({'user': user, 'token': token, 'status': 'ok', 'message': 'Correcto.'})
            else:
                return jsonify({'status': 'Error', 'message': "Error contraseña incorrecta."})
        else:
            return jsonify({'status': 'Error', 'message': "Error, el usuario no existe."})
        
    except Exception as ex:
        return jsonify({'status': 'Error', 'message': "Error"})

@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    try:
        print(request.json)
        cursor = conexion.connection.cursor()
        username = request.json['user']
        email = request.json['email']
        password = request.json['password']
        sql = """SELECT * FROM users WHERE username = '{0}'""".format(username)
        cursor.execute(sql)
        dato = cursor.fetchone()
        if dato == None:
            # existe el usuario, verificar contraseña
            sql = """SELECT * FROM users WHERE email = '{0}'""".format(email)
            cursor.execute(sql)
            dato = cursor.fetchone()
            if dato == None:
                # correcto
                cursor = conexion.connection.cursor()
                sql = """INSERT INTO users (username, password, email)
                VALUES ('{0}', '{1}', '{2}')""".format(username, password, email)
                cursor.execute(sql)
                conexion.connection.commit()

                token = uuid.uuid4()
                user = {'id': cursor.lastrowid, 'username': username}
                return jsonify({'user': user, 'token': token, 'status': 'ok', 'message': 'Correcto.'})
            else:
                return jsonify({'status': 'Error', 'message': "Error, correo ya existe."})
        else:
            return jsonify({'status': 'Error', 'message': "Error, el usuario ya existe."})
        
    except Exception as ex:
        return jsonify({'status': 'Error', 'message': str(ex)})



def not_found(error):
    return "<h1>La pagina no existe!</h1>", 404



if __name__ == '__main__':
    
    from routes.route_generaciones import generacion_bp
    from routes.route_api import api_bp
    from routes.route_imagen import imagen_bp
    
    app.register_blueprint(generacion_bp, url_prefix='/generaciones')
    app.register_blueprint(api_bp, url_prefix='/generar')
    app.register_blueprint(imagen_bp, url_prefix='/imagen')

    app.config.from_object(config['development'])
    app.register_error_handler(404, not_found)
    
    #port = int(os.environ.get('PORT', 5000))
    #app.run(debug=True, host='0.0.0.0', port=port)
    
    #app.run(ssl_context=('cert.pem', 'key.pem'))
    app.run()