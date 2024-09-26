from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)

# Configuración de la conexión a MySQL (usando la instancia de AWS RDS)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admindb:CestaSmart1512@database-1-instance-1.cxagouikqjlk.us-east-2.rds.amazonaws.com/dbcestasmart'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la tabla 'usuario'
class Usuario(db.Model):
    __tablename__ = 'usuario'
    idUsuario = db.Column(db.Integer, primary_key=True)
    nomUsuario = db.Column(db.String(100), nullable=False)
    rfid_code = db.Column(db.String(100), unique=True, nullable=False)

# Modelo de la tabla 'registro'
class Registro(db.Model):
    __tablename__ = 'registro'
    idRegistro = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)
    puntos = db.Column(db.Integer, default=0, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    estado = db.Column(db.String(50))

# Crear las tablas en la base de datos si no existen
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint para registrar un nuevo usuario
@app.route('/api/usuarios', methods=['POST'])
def registrar_usuario():
    data = request.json
    nomUsuario = data.get('nomUsuario')
    rfid_code = data.get('rfid_code')

    if not nomUsuario or not rfid_code:
        return jsonify({'error': 'Nombre de usuario y código RFID son obligatorios'}), 400

    nuevo_usuario = Usuario(nomUsuario=nomUsuario, rfid_code=rfid_code)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado con éxito'}), 201

# Endpoint para registrar el uso de la cesta y sumar puntos
@app.route('/api/rfid', methods=['POST'])
def registrar_uso_cesta():
    data = request.json
    rfid_code = data.get('rfid_code')

    usuario = Usuario.query.filter_by(rfid_code=rfid_code).first()

    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    nuevo_registro = Registro(idUsuario=usuario.idUsuario, puntos=5, estado="disponible")
    db.session.add(nuevo_registro)
    db.session.commit()

    return jsonify({
        'message': f'El usuario {usuario.nomUsuario} ha ganado 5 puntos.',
        'puntos_totales': Registro.query.filter_by(idUsuario=usuario.idUsuario).count() * 5
    }), 200

# Endpoint para listar usuarios y sus puntos
@app.route('/api/usuarios/puntos', methods=['GET'])
def listar_puntos():
    usuarios = Usuario.query.all()
    resultado = []

    for usuario in usuarios:
        puntos_totales = db.session.query(db.func.sum(Registro.puntos)).filter_by(idUsuario=usuario.idUsuario).scalar() or 0
        resultado.append({
            'idUsuario': usuario.idUsuario,
            'nomUsuario': usuario.nomUsuario,
            'puntos': puntos_totales
        })

    return jsonify(resultado), 200

if __name__ == '__main__':
    app.run(debug=True)
