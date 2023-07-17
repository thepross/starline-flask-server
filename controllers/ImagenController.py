import sys, os, io
from flask import request, jsonify
from app import conexion
from PIL import Image
from base64 import encodebytes

def index(id):
    try:
        cursor = conexion.connection.cursor()
        # sql = "SELECT * from imagenes LIMIT 5"
        sql = "SELECT * from imagenes, generaciones WHERE imagenes.id_generacion = generaciones.id AND generaciones.id_user = {0}".format(id)
        cursor.execute(sql)
        datos = cursor.fetchall()
        imagenes = []
        for f in datos:
            with Image.open(f[1]) as image:
                byte_arr = io.BytesIO()
                image.save(byte_arr, format='JPEG')
                encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
            imagen = {'id':f[0], 'ruta': f[1], 'nombre': f[2], 'size': f[3], 'id_generacion': f[4], 'image': 'data:image/jpeg;base64,' + encoded_img}
            imagenes.append(imagen)
        return jsonify({'imagenes': imagenes, 'mensaje': "Imagenes listadas."})
    except Exception as ex:
        return jsonify({'mensaje': 'Error', 'error': str(ex)})

def show(id):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * from imagenes WHERE id = {0}".format(id)
        cursor.execute(sql)
        f = cursor.fetchone()
        imagenes = []
        with Image.open(f[1]) as image:
            byte_arr = io.BytesIO()
            image.save(byte_arr, format='JPEG')
            encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')

        
        sql = "SELECT * from calificaciones WHERE id_imagen = {0} AND id_generacion = {1} order by id desc limit 1".format(id, f[4])
        cursor.execute(sql)
        rt = cursor.fetchone()
        rating = ""
        if rt != None:
            rating = rt[1]
        imagen = {'id':f[0], 'ruta': f[1], 'nombre': f[2], 'size': f[3], 'id_generacion': f[4], 'image': 'data:image/jpeg;base64,' + encoded_img, 'rating': rating}
        imagenes.append(imagen)

        return jsonify({'imagenes': imagenes, 'mensaje': "Imagenes listadas."})
    except Exception as ex:
        return jsonify({'mensaje': 'Error', 'error': str(ex)})

def recursos(id):
    try:
        cursor = conexion.connection.cursor()
        # sql = "SELECT * from imagenes LIMIT 5"
        sql = "SELECT * from generaciones WHERE id_user = {0}".format(id)
        cursor.execute(sql)
        datos = cursor.fetchall()
        imagenes = []
        for d in datos:
            imagen = []
            if d[1] != "":
                with Image.open(d[1]) as image:
                    byte_arr = io.BytesIO()
                    image.save(byte_arr, format='PNG')
                    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
                    imagen.append('data:image/jpeg;base64,' + encoded_img)
            else:
                imagen.append("")
            if d[2] != "":
                with Image.open(d[2]) as image:
                    byte_arr = io.BytesIO()
                    image.save(byte_arr, format='PNG')
                    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
                    imagen.append('data:image/jpeg;base64,' + encoded_img)
            else:
                imagen.append("")
            if d[3] != "":
                with Image.open(d[3]) as image:
                    byte_arr = io.BytesIO()
                    image.save(byte_arr, format='PNG')
                    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
                    imagen.append('data:image/jpeg;base64,' + encoded_img)
            else:
                imagen.append("")
            
            i = {'id': d[0], 'image': imagen}
            imagenes.append(i)
        
        return jsonify({'imagenes': imagenes, 'mensaje': "Imagenes listadas."})
    except Exception as ex:
        return jsonify({'mensaje': 'Error', 'error': str(ex)})
    

def calificacion():
    try:
        cursor = conexion.connection.cursor()
        detalle = request.form['detalle']
        id_generacion = request.form['id_generacion']
        id_imagen = request.form['id_imagen']
        sql = """INSERT INTO calificaciones (detalle, id_generacion, id_imagen) VALUES ('{0}', '{1}', '{2}')""".format(detalle, id_generacion, id_imagen)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'status': 'ok', 'message': 'Correcto.'})
    except Exception as ex:
        return jsonify({'status': 'Error', 'message': ex})