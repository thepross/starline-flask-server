from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)
db.init_app(app)

class Generaciones(db.Model):
    __tablename__ = 'generaciones'
    id = db.Column(db.Integer, primary_key=True)
    imagen1 = db.Column(db.String)
    imagen2 = db.Column(db.String(120))
    imagen3 = db.Column(db.String(120))
    texto1 = db.Column(db.String(120))
    texto2 = db.Column(db.String(120))
    texto3 = db.Column(db.String(120))
    id_user = db.Column(db.String(120))
    @property
    def serialize(self):
        return {
            'id': self.id,
            'imagen1': self.imagen1,
            'imagen2': self.imagen2,
            'imagen3': self.imagen3,
            'texto1': self.texto1,
            'texto2': self.texto2,
            'texto3': self.texto3,
            'id_user': self.id_user
        }