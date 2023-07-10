import sys
from flask import request, jsonify
from app import conexion
from werkzeug.utils import secure_filename

import numpy as np

def index():
    return "hola"

def generar2(texto1, texto2):
    if request.method == 'POST':
        texto1 = request.form['texto1']
        texto2 = request.form['texto2']
        try:
            print(texto1, texto2)
            generaciones = []
            for i in range(1, 5):
                imagen = generate(texto1, texto2)
                generaciones.append(imagen)

            return jsonify({'generaciones': generaciones, 'mensaje': "Generaciones listadas."})
        except Exception as ex:
            return jsonify({'mensaje': "Error"})

def generar():
    print(request.form)
    if request.method == 'POST':
        id_generacion = request.form['id_generacion']
        try:
            cursor = conexion.connection.cursor()
            sql = "SELECT * from generaciones WHERE id = '{0}'".format(id_generacion)
            cursor.execute(sql)
            generacion = cursor.fetchone()
            imagen1 = Image.open(generacion[1])
            imagen1_path = generacion[1]
            texto1 = generacion[4]
            texto2 = generacion[5]
            texto3 = generacion[6]

            print(texto1, texto2)
            generaciones = []
            for i in range(1, 2):
                nombre_archivo, imagen = generate(texto1, texto2, imagen1, imagen1_path)

                cursor = conexion.connection.cursor()
                sql = """INSERT INTO imagenes (ruta, nombre, size, id_generacion)
                VALUES ('{0}', '{1}', '{2}', '{3}')""".format(nombre_archivo, "poster", "982673", id_generacion)
                cursor.execute(sql)
                conexion.connection.commit()
                generaciones.append(imagen)

            return jsonify({'generaciones': generaciones, 'mensaje': "Imagen Creada."})
        except Exception as ex:
            return jsonify({'mensaje': ex})



    
def generador(texto1, texto2, texto3, imagen1, imagen2, imagen3, id):
    try:
        print(texto1, texto2)
        generaciones = []
        for i in range(1, 5):
            imagen = generate(texto1, texto2)
            generaciones.append(imagen)

        return jsonify({'generaciones': generaciones, 'mensaje': "Generaciones listadas."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})
    





import cv2
import os
import random, io, datetime
import argparse
import json
from tqdm import tqdm
from base64 import encodebytes
from PIL import Image

from utils.font_utils import PutText2Image
from background_retrieval import bk_img_retrieval
from layout_distribution_predict import smooth_region_dectection, get_distrib_mask
from layout_refine import get_batch_text_region, get_bbox_mask, get_refine_bboxes


####################################



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


def scale(image, scale_width):
    (image_height, image_width) = image.shape[:2]
    new_height = int(scale_width / image_width * image_height)
    return cv2.resize(image, (scale_width, new_height))

def set_logo(imagen1, img_path, img, width, height, h, w):
    # colocar logos u otras imagenes
    # fl, file_extension = os.path.splitext(img_path)
    # print(file_extension)
    file_extension = ".jpg"
    logo = cv2.imread(img_path)
    filas, columnas, canales = logo.shape
    if (filas > 500):
        logo = scale(cv2.imread(img_path), 500)
        filas, columnas, canales = logo.shape
    
    print(filas, columnas)
    print(width, height)
        
    # interactuar entre imagenes iguales
    rnd = random.randint(1, 4)
    roi = img[0:filas, 0:columnas]
    if rnd == 1:
        roi = img[10:filas + 10, 10:columnas + 10] # arriba izquierda
    elif rnd == 2:
        roi = img[w-filas - 10:w - 10, 10:columnas + 10] # abajo izquierda
    elif rnd == 3:
        roi = img[10:filas + 10, h-columnas - 10:h - 10] # arriba derecha
    else: 
        roi = img[w - filas - 10:w - 10, h - columnas - 10:h - 10] # abajo derecha

    if (file_extension != '.png'):
        #binarizar el logo
        logo_gris = cv2.cvtColor(logo, cv2.COLOR_RGB2GRAY)
        ret, mascara = cv2.threshold(logo_gris, 240, 255, cv2.THRESH_BINARY)
        mascara_invertida = cv2.bitwise_not(mascara)

        #operaciones
        img_fondo = cv2.bitwise_and(roi, roi, mask=mascara)
        logo_frente = cv2.bitwise_and(logo, logo, mask=mascara_invertida)
        #combinar
        res = cv2.add(img_fondo, logo_frente)
    else:
        res = logo
        # logo = cv2.imread('images/logo.png', cv2.IMREAD_UNCHANGED)
        # bgr = logo[:,:,:3] # Channels 0..2
        # gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        # bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        # alpha = logo[:,:,3] # Channel 3
        # result = np.dstack([bgr, alpha])
        # res = result

    #añadir logo
    if rnd == 1:
        img[10:filas + 10, 10:columnas + 10] = res # arriba izquierda
    elif rnd == 2:
        img[w-filas - 10:w - 10, 10:columnas + 10] = res # abajo izquierda
    elif rnd == 3:
        img[10:filas + 10, h-columnas - 10:h - 10] = res # arriba derecha
    else: 
        img[w - filas - 10:w - 10, h - columnas - 10:h - 10] = res # abajo derecha
    return img


def generate(texto1, texto2, imagen1, logo_path):

    STD_WIDTH, STD_HEIGHT = 300, 400
    MIN_VALUE = -999999
    MAX_BBOX_NUM = 32

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

    # cargando los textos
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

    # imagenes de fondo obtenidas de bk_img_retrieval
    image_path_list = bk_img_retrieval(background_query, args.background_folder)

    for i, img_path in enumerate(tqdm(image_path_list[:args.top_n])):
        print("background image: ", img_path)
        img = cv2.imread(img_path)
        width, height = img.shape[1], img.shape[0]
        h, w = img.shape[1], img.shape[0]

        img = set_logo(imagen1, logo_path, img, width, height, h, w)

        img_size = (width, height)
        smooth_region_mask, regions, saliency_map = smooth_region_dectection(img)
        bbox_distrib_map = get_distrib_mask(smooth_region_mask)
        bbox_size_array = np.zeros((len(sentences), 2))

        # Estimar el tamaño de las cajas de texto.
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

    return filename, gen[0]
