from datetime import datetime, timedelta
from prettytable import PrettyTable
import random

def get_workout_for_day(day, last_workout):
    # Assign fixed workouts based on the day
    if day == 'Tuesday':
        return 'Speed'
    elif day == 'Thursday':
        return 'Tempo'
    elif day == 'Saturday':
        return 'Long Runs'

    # If the last workout was Long Runs, only allow Rest Days or Easy Runs on the next day
    if last_workout == 'Long Runs' and day == 'Sunday':
        return random.choice(['Rest Day', 'Easy'])

    # Assign other workouts randomly
    workout_sequence = ['Easy', 'Progressive', 'Fartlek']
    return random.choice(workout_sequence)

def randomize_percentage_distribution():
    # Randomize the percentage distribution for each workout type
    percentage_distribution = {
        'Long Runs': round(random.uniform(20, 30)),
        'Speed': round(random.uniform(8, 12)),
        'Tempo': round(random.uniform(10, 20)),
        'Progressive': round(random.uniform(0, 20)),
        'Fartlek': round(random.uniform(0, 20)),
        'Easy': round(random.uniform(50, 100))
    }

    # Normalize percentages to sum to 100%
    total_percentage = sum(percentage_distribution.values())
    normalized_distribution = {k: v / total_percentage * 100 for k, v in percentage_distribution.items()}

    # Ensure 'Rest Day' is displayed as 0%
    normalized_distribution['Rest Day'] = 0

    return normalized_distribution

def generate_week_schedule_with_workouts(num_weeks):
    # Get the current date and time
    current_date = datetime.now()

    # Calculate the start date of the next week
    start_date = current_date + timedelta(days=(7 - current_date.weekday()))

    # Initialize a PrettyTable for displaying the schedule
    table = PrettyTable()
    header_row = ["Day"] + [f"Week {i}" for i in range(1, num_weeks + 1)]

    table.field_names = header_row

    last_workout = None  # Track the last workout for the Long Run rule

    # Generate and print the schedule for each day
    for day in range(7):
        # Calculate the current date for the day
        current_day = start_date + timedelta(days=day)

        # Initialize a row for the day
        row_data = [f"{current_day.strftime('%A')}"]

        # Add the workouts for each week
        for week in range(1, num_weeks + 1):
            workout = get_workout_for_day(current_day.strftime('%A'), last_workout)
            row_data.append(f"{workout}")

            # Update last_workout after each iteration
            last_workout = workout

        # Add the row to the table
        table.add_row(row_data)

    # Randomize the percentage distribution
    percentages = randomize_percentage_distribution()

    # Add percentage information next to each workout in the table
    for i in range(1, num_weeks + 1):
        for j in range(7):
            workout = table._rows[j][i]
            percentage = f"{round(percentages.get(workout, 0))}%"
            table._rows[j][i] = f"{workout} ({percentage})"

    # Print the modified table
    print(table)

# Example usage:
num_weeks = 3
generate_week_schedule_with_workouts(num_weeks)
