
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
from base64 import encodebytes
from PIL import Image
import random, io, datetime
from slugify import slugify

from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from config import config
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from base64 import encodebytes
from PIL import Image
import random, io

app = Flask(__name__)
CORS(app)

conexion = MySQL(app)


def not_found(error):
    return "<h1>La pagina no existe!</h1>", 404



if __name__ == '__main__':
    
    from routes.route_generaciones import generacion_bp
    from routes.route_api import api_bp
    
    app.register_blueprint(generacion_bp, url_prefix='/generaciones')
    app.register_blueprint(api_bp, url_prefix='/generar')

    app.config.from_object(config['development'])
    app.register_error_handler(404, not_found)
    app.run('0.0.0.0', 5000)