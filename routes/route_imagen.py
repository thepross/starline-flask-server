from flask import Blueprint

from controllers.ImagenController import index, show, recursos, calificacion

imagen_bp = Blueprint('imagen_bp', __name__)
imagen_bp.route('/<int:id>/<int:page>', methods=['GET'])(index)
imagen_bp.route('/show/<int:id>', methods=['GET'])(show)
imagen_bp.route('/recursos/<int:id>/<int:page>', methods=['GET'])(recursos)
imagen_bp.route('/calificacion', methods=['POST'])(calificacion)