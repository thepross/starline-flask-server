from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config
from flask_cors import CORS

from base64 import encodebytes
from PIL import Image
import random, io

app = Flask(__name__)
CORS(app)

conexion = MySQL(app)

@app.route('/api', methods=['GET'])
def api():
    try:
        generaciones = []
        lista = []
        for j in range(1, 5):
            rnd = random.randint(1, 7)
            lista.append(rnd)
        for i in lista:
            filename = "src/images/{0}.png".format(i)
            with Image.open(filename) as image:
                # width, height = image.size
                print(filename)
                byte_arr = io.BytesIO()
                image.save(byte_arr, format='PNG')
                encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
                generaciones.append(encoded_img)

        print("cantidad: ", len(generaciones))
        return jsonify({'generaciones': generaciones, 'mensaje': "Generaciones listadas."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})


@app.route('/generaciones', methods=['GET'])
def listar_generaciones():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * from generaciones"
        cursor.execute(sql)
        datos = cursor.fetchall()
        generaciones = []
        for f in datos:
            generacion = {'id':f[0], 'imagen1': f[1], 'imagen2': f[2], 'imagen3': f[3], 'texto1': f[4], 'texto2': f[5], 'texto3': f[6], 'id_user': f[7]}
            generaciones.append(generacion)
        return jsonify({'generaciones': generaciones, 'mensaje': "Generaciones listadas."})
        # return jsonify({'generaciones': [], 'mensaje': "Generaciones listadas."})
    except Exception as ex:
        return jsonify({'mensaje': 'Error', 'error': str(ex)})


@app.route('/generaciones/<id>', methods=['GET'])
def leer_generacion(id):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * from generaciones WHERE id = '{0}'".format(id)
        cursor.execute(sql)
        datos = cursor.fetchone()
        if datos != None:
            generacion = {'id':datos[0], 'imagen1': datos[1], 'imagen2': datos[2], 'imagen3': datos[3], 'texto1': datos[4], 'texto2': datos[5], 'texto3': datos[6], 'id_user': datos[7]}
            return jsonify({'generacion': generacion, 'mensaje': "Generacion encontrada."})
        else:
            return jsonify({'mensaje': "Generacion no encontrada."})
            
    except Exception as ex:
        return jsonify({'mensaje': "Error"})


@app.route('/generaciones', methods=['POST'])
def registrar_generacion():
    try:
        #print(request.json)
        cursor = conexion.connection.cursor()
        sql = """INSERT INTO generaciones (id, imagen1, imagen2, imagen3, texto1, texto2, texto3, id_user) 
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')""".format(request.json['id'], request.json['imagen1'], request.json['imagen2'], request.json['imagen3'], request.json['texto1'], request.json['texto2'], request.json['texto3'], request.json['id_user'])
        cursor.execute(sql)
        conexion.connection.commit() #confirmacion
        return jsonify({'mensaje': "Generacion registrado."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})


@app.route('/generaciones/<id>', methods=['PUT'])
def actualizar_generacion(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """UPDATE generaciones SET imagen1 = '{1}', imagen2 = '{2}', imagen3 = '{3}', texto1 = '{4}', texto2 = '{5}', texto3 = '{6}', id_user = {7}
        """.format(id, request.json['imagen1'], request.json['imagen2'], request.json['imagen3'], request.json['texto1'], request.json['texto2'], request.json['texto3'], request.json['id_user'])
        cursor.execute(sql)
        conexion.connection.commit() #confirmacion
        return jsonify({'mensaje': "Generacion actualizado."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})
    


@app.route('/generaciones/<id>', methods=['DELETE'])
def eliminar_generacion(id):
    try:
        cursor = conexion.connection.cursor()
        sql = "DELETE FROM generaciones WHERE id = '{0}'".format(id)
        cursor.execute(sql)
        conexion.connection.commit() #confirmacion
        return jsonify({'mensaje': "Generacion eliminada."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})
    


def not_found(error):
    return "<h1>La pagina no existe!</h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, not_found)
    app.run()