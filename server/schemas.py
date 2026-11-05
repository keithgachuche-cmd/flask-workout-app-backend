from marshmallow import Schema, ValidationError, fields, validate, validates, validates_schema


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='Name must be 1-100 characters.'),
    )
    category = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50, error='Category must be 1-50 characters.'),
    )
    equipment_needed = fields.Bool(required=True)

    # Only shown on GET /exercises/<id> (the associated workouts)
    workout_exercises = fields.Nested(
        'WorkoutExerciseSchema', many=True, dump_only=True, exclude=('exercise',)
    )

    # Schema validation: blank/whitespace-only strings are not allowed
    @validates('name')
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError('Name cannot be blank.')

    @validates('category')
    def validate_category(self, value):
        if not value.strip():
            raise ValidationError('Category cannot be blank.')


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1, max=1440, error='Duration must be between 1 and 1440 minutes.'),
    )
    notes = fields.Str(
        allow_none=True,
        validate=validate.Length(max=500, error='Notes must be 500 characters or fewer.'),
    )

    # Only shown on GET /workouts/<id> (the exercises with reps/sets/duration)
    workout_exercises = fields.Nested(
        'WorkoutExerciseSchema', many=True, dump_only=True, exclude=('workout',)
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(
        allow_none=True, strict=True,
        validate=validate.Range(min=0, max=10000, error='Reps must be between 0 and 10000.'),
    )
    sets = fields.Int(
        allow_none=True, strict=True,
        validate=validate.Range(min=0, max=1000, error='Sets must be between 0 and 1000.'),
    )
    duration_seconds = fields.Int(
        allow_none=True, strict=True,
        validate=validate.Range(min=0, max=86400, error='Duration must be between 0 and 86400 seconds.'),
    )

    exercise = fields.Nested('ExerciseSchema', dump_only=True, exclude=('workout_exercises',))
    workout = fields.Nested('WorkoutSchema', dump_only=True, exclude=('workout_exercises',))

    # Schema validation: an entry needs reps AND sets, or a duration (or both)
    @validates_schema
    def validate_measurement(self, data, **kwargs):
        reps, sets = data.get('reps'), data.get('sets')
        duration = data.get('duration_seconds')
        has_reps_and_sets = reps is not None and sets is not None
        if not has_reps_and_sets and duration is None:
            raise ValidationError(
                'Provide both reps and sets, or duration_seconds (or all three).',
                field_name='_schema',
            )
        if (reps is None) != (sets is None):
            raise ValidationError('reps and sets must be provided together.', field_name='_schema')


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workout_exercises',))
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
workout_exercise_schema = WorkoutExerciseSchema()