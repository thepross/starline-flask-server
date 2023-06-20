from flask import Flask, request, flash, url_for, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:12345678@34.31.245.198:3306/db_starline'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

# class Generaciones(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     imagen1 = db.Column(db.String)
#     imagen2 = db.Column(db.String(120))
#     imagen3 = db.Column(db.String(120))
#     texto1 = db.Column(db.String(120))
#     texto2 = db.Column(db.String(120))
#     texto3 = db.Column(db.String(120))
#     id_user = db.Column(db.String(120))


@app.route('/gennn')
def show_all():
    from models.Generacion import Generaciones
    st = Generaciones.query.all()
    # return jsonify([generacion.serialize() for generacion in st])
    

if __name__ == '__main__':
   app.app_context().push()
   app.run(debug = True)