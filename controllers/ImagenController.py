import sys, os, io
from flask import request, jsonify
from app import conexion
from PIL import Image
from base64 import encodebytes

def index():
    try:
        cursor = conexion.connection.cursor()
        # sql = "SELECT * from imagenes LIMIT 5"
        sql = "SELECT * from imagenes"
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
