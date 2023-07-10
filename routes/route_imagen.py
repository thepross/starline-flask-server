from flask import Blueprint

from controllers.ImagenController import index

imagen_bp = Blueprint('imagen_bp', __name__)
imagen_bp.route('/', methods=['GET'])(index)