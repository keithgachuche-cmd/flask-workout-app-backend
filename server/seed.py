#!/usr/bin/env python3
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing tables...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print('Seeding exercises...')
    squat = Exercise(name='Squat', category='Strength', equipment_needed=True)
    pushup = Exercise(name='Push-up', category='Strength', equipment_needed=False)
    plank = Exercise(name='Plank', category='Core', equipment_needed=False)
    run = Exercise(name='Running', category='Cardio', equipment_needed=False)
    db.session.add_all([squat, pushup, plank, run])

    print('Seeding workouts...')
    w1 = Workout(date=date(2026, 10, 26), duration_minutes=45, notes='Leg day')
    w2 = Workout(date=date(2026, 10, 28), duration_minutes=30, notes='Quick core and cardio')
    db.session.add_all([w1, w2])
    db.session.commit()

    print('Seeding workout exercises...')
    db.session.add_all([
        WorkoutExercise(workout=w1, exercise=squat, reps=10, sets=4),
        WorkoutExercise(workout=w1, exercise=pushup, reps=15, sets=3),
        WorkoutExercise(workout=w2, exercise=plank, duration_seconds=60, sets=3),
        WorkoutExercise(workout=w2, exercise=run, duration_seconds=900),
    ])
    db.session.commit()
    print('Done!')