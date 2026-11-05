from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = 'exercises'

    # Table constraints
    __table_args__ = (
        UniqueConstraint('name', name='uq_exercise_name'),
        CheckConstraint('length(trim(name)) > 0', name='ck_exercise_name_not_blank'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Exercise has many WorkoutExercises (deleting an exercise removes them)
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan'
    )
    # Exercise has many Workouts through WorkoutExercises
    workouts = association_proxy('workout_exercises', 'workout')

    # Model validations
    @validates('name', 'category')
    def validate_text(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{key} must be a non-empty string.')
        return value.strip()

    @validates('equipment_needed')
    def validate_equipment(self, key, value):
        if not isinstance(value, bool):
            raise ValueError('equipment_needed must be true or false.')
        return value

    def __repr__(self):
        return f'<Exercise {self.id} {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    # Table constraints
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Workout has many WorkoutExercises (deleting a workout removes them)
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan'
    )
    # Workout has many Exercises through WorkoutExercises
    exercises = association_proxy('workout_exercises', 'exercise')

    # Model validations
    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError('date must be a valid date.')
        return value

    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError('duration_minutes must be a positive integer.')
        return value

    def __repr__(self):
        return f'<Workout {self.id} {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    # Table constraints
    __table_args__ = (
        UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise_pair'),
        CheckConstraint('reps IS NULL OR reps >= 0', name='ck_we_reps_non_negative'),
        CheckConstraint('sets IS NULL OR sets >= 0', name='ck_we_sets_non_negative'),
        CheckConstraint(
            'duration_seconds IS NULL OR duration_seconds >= 0',
            name='ck_we_duration_non_negative',
        ),
        CheckConstraint(
            'reps IS NOT NULL OR sets IS NOT NULL OR duration_seconds IS NOT NULL',
            name='ck_we_has_measure',
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # A WorkoutExercise belongs to a Workout and to an Exercise
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # Model validations
    @validates('reps', 'sets', 'duration_seconds')
    def validate_measure(self, key, value):
        if value is None:
            return value
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f'{key} must be a non-negative integer.')
        return value

    def __repr__(self):
        return f'<WorkoutExercise {self.id} w={self.workout_id} e={self.exercise_id}>'