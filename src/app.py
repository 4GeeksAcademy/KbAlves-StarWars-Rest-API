from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)
@app.route('/user', methods=['GET'])
def get_users():
    # obtiene todos los objetos de usuario de la base de datos
    users = User.query.all()
    # crea una lista de diccionarios con la información de cada usuario
    user_list = [
        {
            "id": user.id,
            "email": user.email
            # agrega aquí cualquier otra información que quieras devolver
        }
        for user in users
    ]

    return jsonify(user_list), 200

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return 'User not found', 404
    favorites = [favorite.serialize() for favorite in user.favorites]
    return jsonify(favorites), 200

@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id, user_id):

    body = request.get_json()
    planet_id = body['planet_id']

    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    new_favorite = Favorite(user = user, planet = planet)

    db.session.add(new_favorite)
    db.session.commit()

    response_body = {'msg' : 'Su planeta favorito ha sido agregado correctamente'}
    return jsonify(response_body)

@app.route('/favorite/user/<int:user_id>/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id, user_id):

    body = request.get_json()
    people_id = body['people_id']

    user = User.query.get(user_id)
    people = People.query.get(people_id)
    new_favorite = Favorite(user = user, people = people)

    db.session.add(new_favorite)
    db.session.commit()

    response_body = {'msg' : 'Su persona favorita ha sido agregado correctamente'}
    return jsonify(response_body)

@app.route('/favorite/user/<int:user_id>/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id, user_id):

    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    favorite = Favorite.query.filter_by(user=user, planet=planet).first()

    if favorite is None:
        return jsonify({'msg' : 'No favorite found'}), 404

    db.session.delete(favorite)
    db.session.commit()

    response_body = {'msg' : 'Su planeta favorito ha sido eliminado correctamente'}
    return jsonify(response_body)

@app.route('/favorite/user/<int:user_id>/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id, user_id):

    user = User.query.get(user_id)
    people = People.query.get(people_id)

    favorite = Favorite.query.filter_by(user=user, people=people).first()

    if favorite is None:
        return jsonify({'msg' : 'No favorite found'}), 404

    db.session.delete(favorite)
    db.session.commit()

    response_body = {'msg' : 'Su persona favorita ha sido eliminada correctamente'}
    return jsonify(response_body)

@app.route('/planet', methods=['GET'])
def get_planets():
    allPlanets = Planet.query.all()
	@@ -67,6 +141,7 @@ def get_single_planet(planet_id):
        return 'Planeta no encontrado', 404
    return jsonify(planet1.serialize()), 200


@app.route('/planet', methods=['POST'])
def post_planet():

	@@ -116,6 +191,8 @@ def post_people():

    return jsonify(inserted_person_data), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))