from flask import Blueprint

from controllers.ApiController import index, generar

api_bp = Blueprint('api_bp', __name__)
api_bp.route('/', methods=['POST'])(generar)