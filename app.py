from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@your_rds_endpoint/dbcestasmart'

# Configuración de la conexión a MySQL (usando la instancia de AWS RDS)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admindb:CestaSmart1512@database-1-instance-1.cxagouikqjlk.us-east-2.rds.amazonaws.com/dbcestasmart'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Usuario
class Usuario(db.Model):
    idUsuario = db.Column(db.Integer, primary_key=True)
    nomUsuario = db.Column(db.String(100), nullable=False)
    rfid_code = db.Column(db.String(100), unique=True, nullable=False)

# Modelo de Registro (puntos)
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'))
    puntos = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), nullable=False)

# Crear las tablas en la base de datos si no existen
#with app.app_context():
#   db.create_all()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')
   
# Ruta para "Nuevo Usuario"
@app.route('/nuevo_usuario', methods=['GET', 'POST'])
def nuevo_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        rfid = request.form['rfid']
        nuevo_usuario = Usuario(nomUsuario=nombre, rfid_code=rfid)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('consultar_puntos'))
    return render_template('nuevo_usuario.html')

# Ruta para "Consultar Puntos"
@app.route('/consultar_puntos')
def consultar_puntos():
    usuarios = Usuario.query.all()
    return render_template('consultar_puntos.html', usuarios=usuarios)


# Ruta para "Redimir Puntos"
@app.route('/redimir_puntos')
def redimir_puntos():
    productos = [
        {'nombre': 'Producto 1', 'puntos': 20, 'imagen': 'producto1.jpg'},
        {'nombre': 'Producto 2', 'puntos': 50, 'imagen': 'producto2.jpg'}
        # Más productos aquí
    ]
    productos = sorted(productos, key=lambda x: x['puntos'])
    return render_template('redimir_puntos.html', productos=productos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Esto crea las tablas en la base de datos
    app.run(debug=True)
