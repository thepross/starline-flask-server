from flask import Blueprint

from controllers.GeneracionController import index, store, show, update, destroy

generacion_bp = Blueprint('generacion_bp', __name__)
generacion_bp.route('/', methods=['GET'])(index)
generacion_bp.route('/create', methods=['POST'])(store)
generacion_bp.route('/<int:id>', methods=['GET'])(show)
generacion_bp.route('/<int:id>/edit', methods=['POST'])(update)
generacion_bp.route('/<int:id>', methods=['DELETE'])(destroy)