
import argparse
import json
import cv2
import numpy as np
import os
from tqdm import tqdm


os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from background_retrieval import bk_img_retrieval
from utils.font_utils import PutText2Image

from model.distrib_model import LayoutsDistribModel
from model.layout_model import BBoxesRegModel

from layout_distribution_predict import smooth_region_dectection, get_distrib_mask
from layout_refine import get_batch_text_region, get_bbox_mask, get_refine_bboxes



####################################
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config
from flask_cors import CORS

from base64 import encodebytes
from PIL import Image
import random, io, datetime
from slugify import slugify

app = Flask(__name__)
CORS(app)

conexion = MySQL(app)

# Para almacenar en AWS
# import boto3
# # Let's use Amazon S3
# s3 = boto3.resource("s3")
# for bucket in s3.buckets.all():
#     print(bucket.name)

@app.route('/gem/<texto1>/<texto2>', methods=['GET'])
def gem(texto1, texto2):
    try:
        print(texto1, texto2)
        generaciones = []
        for i in range(1, 5):
            imagen = generador(texto1, texto2)
            generaciones.append(imagen)

        return jsonify({'generaciones': generaciones, 'mensaje': "Generaciones listadas."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})
    
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
    except Exception as ex:
        return jsonify({'mensaje': "Error"})


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



####################################


STD_WIDTH, STD_HEIGHT = 300, 400
MIN_VALUE = -999999
MAX_BBOX_NUM = 32

def draw_figure(mask_list, layers, height, width):
    figure_mask = np.zeros((height, width, 3))
    for mask, layer in zip(mask_list, layers):
        figure_mask[:, :, layer] = mask / mask.max()
    figure_mask = cv2.resize(figure_mask, (width, height))
    return figure_mask * 255


def save_process_to_figure(
    saliency_map, 
    smooth_region_mask, 
    bbox_distrib_map, 
    initial_bbox_mask,
    refined_bbox_mask,
    height, width,
    save_folder):
    
    initial_bbox_mask = cv2.resize(initial_bbox_mask[0], (width, height))
    smooth_region_mask = cv2.resize(smooth_region_mask[0], (width, height))
    bbox_distrib_map = cv2.resize(bbox_distrib_map, (width, height))
    refined_bbox_mask = cv2.resize(refined_bbox_mask[0], (width, height))

    cv2.imwrite(os.path.join(save_folder, "candidate_regions.jpg"), smooth_region_mask * 255)
    cv2.imwrite(os.path.join(save_folder, "layout_distribution.jpg"), bbox_distrib_map * 255)

    smooth_region_figure = draw_figure(
        [saliency_map, smooth_region_mask], 
        [0, 2],
        height, width)
    cv2.imwrite(os.path.join(save_folder, "saliency_map_with-smooth.jpg"), smooth_region_figure)

    layout_distribution_figure = draw_figure(
        [saliency_map, bbox_distrib_map], 
        [0, 2],
        height, width)
    cv2.imwrite(os.path.join(save_folder, "saliency_map_with-layout-distribution.jpg"), layout_distribution_figure)

    initial_layout_figure = draw_figure(
        [initial_bbox_mask, bbox_distrib_map, saliency_map], 
        [2, 1, 0],
        height, width)
    cv2.imwrite(os.path.join(save_folder, "initial_layout.jpg"), initial_layout_figure)

    refined_layout_figure = draw_figure(
        [refined_bbox_mask, bbox_distrib_map, saliency_map], 
        [2, 1, 0],
        height, width)
    cv2.imwrite(os.path.join(save_folder, "refined_layout.jpg"), refined_layout_figure)
    return


def generador(texto1, texto2):
    tm = datetime.datetime.now()
    currentTime = tm.strftime("%H-%M-%S")
    print(currentTime)
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_text_file", type=str, dest = "input_text_file", default="example/input_text_elements_4.json")
    parser.add_argument("--output_folder", type=str, dest = "output_folder", default="example/output_" + str(currentTime))
    parser.add_argument("--background_folder", type=str, dest = "background_folder", default="bk_image_folder")
    parser.add_argument("--save_process", action='store_true', default=True)
    parser.add_argument("--top_n", type=int, dest = "top_n", default=5)
    args = parser.parse_args()
    print(args)

    # The iteration round of layout refine model.
    iteration_rounds = 30 
    font_file = "./font_files/Poppins-Regular.ttf"
    font_file_bold = "./font_files/Poppins-Bold.ttf"
    text_color = (255, 255, 255)
    ft_center = PutText2Image(font_file)
    ft_center2 = PutText2Image(font_file_bold)

    if not os.path.exists(args.output_folder):
            os.mkdir(args.output_folder)

    # load the input text elements.
    f = open(args.input_text_file, "r")
    input_text_elements = json.load(f) # [(text_1, font_size_n),...,(text_n, font_size_n)]
    f.close()
    input_text_elements["sentences"][0][0] = texto1
    input_text_elements["sentences"][1][0] = texto2
    print(input_text_elements)

    sentences = input_text_elements["sentences"]
    sentences = sorted(sentences, reverse = True, key = lambda x: x[1])
    data_len = len(sentences)

    for text_info in sentences:
        print("Text: {}, Font Size:{}".format(text_info[0], text_info[1]))
    
    background_query = input_text_elements["background_query"]
    print("Background retrieval query:", background_query)

    image_path_list = bk_img_retrieval(background_query, args.background_folder)

    for i, img_path in enumerate(tqdm(image_path_list[:args.top_n])):
        print("background image: ", img_path)
        img = cv2.imread(img_path)
        width, height = img.shape[1], img.shape[0]
        img_size = (width, height)
        smooth_region_mask, regions, saliency_map = smooth_region_dectection(img)
        bbox_distrib_map = get_distrib_mask(smooth_region_mask)
        bbox_size_array = np.zeros((len(sentences), 2))

        # Estimate the size of the text box.
        for j, text_info in enumerate(sentences):
            bbox_size_array[j] = ft_center.get_text_bbox_size(text=text_info[0], text_size=text_info[1])

        # initial layout, sampled by the maximum probability above the bbox_distrib_map.
        initial_bboxes = get_batch_text_region(bbox_distrib_map, bbox_size_array, img_size)
        initial_bbox_mask = get_bbox_mask(initial_bboxes, data_len)

        # The data used to refine the layout.
        initial_data = {"len_info": data_len, 
                    "shifted_mask": initial_bbox_mask.copy(),
                    "shifted_bbox": initial_bboxes.copy(),
                    "bbox_distrib_map": bbox_distrib_map.copy(),
                    "smooth_region_mask": smooth_region_mask.copy()}
        
        # The refined layout.
        refined_bboxes, refined_bbox_size, order = get_refine_bboxes(initial_data, iteration_rounds)
        refined_bbox_mask = get_bbox_mask(refined_bboxes[None, :], data_len)

        # scale the layout to the image size.
        refined_bboxes[:, (0, 2)] = refined_bboxes[:, (0, 2)] / STD_WIDTH * width
        refined_bboxes[:, (1, 3)] = refined_bboxes[:, (1, 3)] / STD_HEIGHT * height

        # save the final poster picture.
        bk_img = img.copy()
        bk_img = bk_img / 1.1
        bk_img = bk_img.astype(np.uint8)
        for j in range(len(sentences)):
            text_position = (refined_bboxes[j][0], refined_bboxes[j][1])
            text, text_size = sentences[order[j]][0], sentences[order[j]][1]
            # if (j != 0):
            #     ft_center = PutText2Image(font_file_bold)
            # else:
            #     ft_center = PutText2Image(font_file)

            font_path = "./font_files"
            font = random.choice(os.listdir(font_path))
            font_file = font_path + "/" + font
            ft_center = PutText2Image(font_file)
            bk_img = ft_center.draw_text(bk_img, text_position, text, text_size, text_color)

        save_folder = os.path.join(args.output_folder, str(i))
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
        # tiempo = str(datetime.datetime.now())
        # image_name = f'poster-{slugify(tiempo)}.jpg'
        poster_file = os.path.join(save_folder, "poster.jpg")
        cv2.imwrite(poster_file, bk_img)

        if args.save_process:
            save_process_to_figure(
                saliency_map, 
                smooth_region_mask, 
                bbox_distrib_map, 
                initial_bbox_mask,
                refined_bbox_mask,
                height, width,
                save_folder)
            
    gen = []        

    filename = "example/output_" + str(currentTime) +"/0/poster.jpg"
    with Image.open(filename) as image:
        print(filename)
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='PNG')
        encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
        gen.append(encoded_img)
    return gen[0]


if __name__ == "__main__":
    app.config.from_object(config['development'])
    app.register_error_handler(404, not_found)
    app.run()
