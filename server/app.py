from flask import Flask, abort, jsonify, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
from schemas import (
    exercise_schema,
    exercises_schema,
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


# ---------- Helpers & error handlers ----------

def error_response(message, status):
    return make_response(jsonify({'error': message}), status)


def get_json_body():
    """Return the JSON body as a dict, or fail with a 400."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError({'_body': ['Request body must be a JSON object.']})
    return data


def get_or_404(model, record_id):
    """Fetch a record by primary key or abort with a descriptive 404."""
    record = db.session.get(model, record_id)
    if record is None:
        abort(404, description=f'{model.__name__} with id {record_id} not found.')
    return record


@app.errorhandler(ValidationError)
def handle_schema_validation_error(err):
    # Marshmallow: request data broke a schema validation
    return make_response(jsonify({'errors': err.messages}), 400)


@app.errorhandler(ValueError)
def handle_model_validation_error(err):
    # SQLAlchemy @validates methods on the models raise ValueError
    db.session.rollback()
    return error_response(str(err), 400)


@app.errorhandler(IntegrityError)
def handle_integrity_error(err):
    # The database rejected the row (table constraint such as UNIQUE / CHECK)
    db.session.rollback()
    return error_response('Database constraint violated (e.g. duplicate name or invalid value).', 409)


@app.errorhandler(404)
def handle_not_found(err):
    return error_response(err.description, 404)


@app.errorhandler(405)
def handle_method_not_allowed(err):
    return error_response('Method not allowed.', 405)


# ---------- Routes ----------

@app.route('/')
def index():
    return make_response(jsonify({'message': 'Workout Tracker API'}), 200)


# --- Workouts ---

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.order_by(Workout.date.desc(), Workout.id.desc()).all()
    return make_response(jsonify(workouts_schema.dump(workouts)), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = get_or_404(Workout, id)
    # Includes each exercise along with its reps / sets / duration_seconds
    return make_response(jsonify(workout_schema.dump(workout)), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = workout_schema.load(get_json_body())
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return make_response(jsonify(workout_schema.dump(workout)), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = get_or_404(Workout, id)
    # Associated WorkoutExercises are removed by the delete cascade
    db.session.delete(workout)
    db.session.commit()
    return make_response('', 204)


# --- Exercises ---

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.name).all()
    return make_response(jsonify(exercises_schema.dump(exercises)), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = get_or_404(Exercise, id)
    # Includes the associated workouts (through WorkoutExercises)
    return make_response(jsonify(exercise_schema.dump(exercise)), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = exercise_schema.load(get_json_body())
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return make_response(jsonify(exercise_schema.dump(exercise)), 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = get_or_404(Exercise, id)
    # Associated WorkoutExercises are removed by the delete cascade
    db.session.delete(exercise)
    db.session.commit()
    return make_response('', 204)


# --- Adding an exercise to a workout ---

@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST'],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = get_or_404(Workout, workout_id)
    exercise = get_or_404(Exercise, exercise_id)

    data = workout_exercise_schema.load(get_json_body())
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return make_response(jsonify(workout_exercise_schema.dump(workout_exercise)), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)