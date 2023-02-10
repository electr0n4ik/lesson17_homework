# app.py *

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app. config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_ns = api.namespace("/movies")
director_ns = api.namespace("/directors")
genre_ns = api.namespace("/genres")

movie_schema = MovieSchema()
director_schema = DirectorSchema()
genre_schema = GenreSchema()

movies_schema = MovieSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        if request.values.get("genre_id") != None and request.values.get("director_id") != None:
            d_id, g_id = int(request.values.get("director_id")), int(request.values.get("genre_id"))
            query = db.session.query(Movie).filter(Movie.director_id == d_id, Movie.genre_id == g_id).all()
            return movies_schema.dump(query)

        elif request.values.get("director_id") != None:
            director_id_request = int(request.values.get("director_id"))
            query = db.session.query(Movie).filter(Movie.director_id == director_id_request).all()
            return movies_schema.dump(query)

        elif request.values.get("genre_id") != None:
            genre_id_request = int(request.values.get("genre_id"))
            query = db.session.query(Movie).filter(Movie.genre_id == genre_id_request).all()
            return movies_schema.dump(query)

        all_movies = Movie.query.all()
        return movies_schema.dump(all_movies), 200


@movie_ns.route('/<int:m_id>')
class MovieView(Resource):
    def get(self, m_id):
        movie = Movie.query.get(m_id)
        return movie_schema.dump(movie), 200


@director_ns.route('/')
class DirectorsView(Resource):
    def post(self):
        req_ = request.json
        dirs = Director(
            id=req_.get("id"),
            name=req_.get("name")
        )

        with db.session.begin():
            db.session.add(dirs)
        return f"{req_.get('id')} добавлен!", 201
@director_ns.route('/<int:d_id>')
class DirectorView(Resource):
    def get(self, d_id):
        director = Director.query.get(d_id)
        return director_schema.dump(director), 200


    def put(self, d_id):
        req_json = request.json
        director = Director.query.get(d_id)
        director.name = req_json["name"]
        db.session.commit()
        return "", 204


    def delete(self, d_id):
        dir = Director.query.get(d_id)
        if not dir:
            return "", 404
        db.session.delete(dir)
        db.session.commit()
        return "", 204

if __name__ == '__main__':
    app.run(debug=True)
