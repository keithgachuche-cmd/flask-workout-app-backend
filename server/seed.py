#!/usr/bin/env python3

from datetime import date

from app import app
from models import *

with app.app_context():
    print('Clearing existing data...')
    # Delete children first so foreign keys are never orphaned
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Seeding exercises...')
    exercises = [
        Exercise(name='Push-ups', category='Strength', equipment_needed=False),
        Exercise(name='Squats', category='Strength', equipment_needed=False),
        Exercise(name='Bench Press', category='Strength', equipment_needed=True),
        Exercise(name='Deadlift', category='Strength', equipment_needed=True),
        Exercise(name='Running', category='Cardio', equipment_needed=False),
        Exercise(name='Jump Rope', category='Cardio', equipment_needed=True),
        Exercise(name='Plank', category='Core', equipment_needed=False),
        Exercise(name='Yoga Flow', category='Flexibility', equipment_needed=True),
    ]
    db.session.add_all(exercises)
    db.session.commit()

    pushups, squats, bench, deadlift, running, rope, plank, yoga = exercises

    print('Seeding workouts...')
    workouts = [
        Workout(date=date(2025, 1, 6), duration_minutes=60,
                notes='Upper body strength day'),
        Workout(date=date(2025, 1, 8), duration_minutes=45,
                notes='Cardio and core'),
        Workout(date=date(2025, 1, 10), duration_minutes=30,
                notes='Quick full-body session'),
        Workout(date=date(2025, 1, 12), duration_minutes=50,
                notes='Recovery and mobility'),
    ]
    db.session.add_all(workouts)
    db.session.commit()

    upper, cardio, full_body, recovery = workouts

    print('Linking exercises to workouts...')
    workout_exercises = [
        WorkoutExercise(workout=upper, exercise=bench, reps=8, sets=4),
        WorkoutExercise(workout=upper, exercise=pushups, reps=15, sets=3),
        WorkoutExercise(workout=upper, exercise=plank, duration_seconds=90),
        WorkoutExercise(workout=cardio, exercise=running, duration_seconds=1200),
        WorkoutExercise(workout=cardio, exercise=rope, duration_seconds=300),
        WorkoutExercise(workout=cardio, exercise=plank, duration_seconds=60),
        WorkoutExercise(workout=full_body, exercise=squats, reps=12, sets=3),
        WorkoutExercise(workout=full_body, exercise=pushups, reps=10, sets=3),
        WorkoutExercise(workout=full_body, exercise=deadlift, reps=5, sets=5),
        WorkoutExercise(workout=recovery, exercise=yoga, duration_seconds=1800),
        WorkoutExercise(workout=recovery, exercise=plank, duration_seconds=45),
    ]
    db.session.add_all(workout_exercises)
    db.session.commit()

    print(f'Done! {Exercise.query.count()} exercises, {Workout.query.count()} workouts, '
          f'{WorkoutExercise.query.count()} workout exercises.')