import redis
from datetime import datetime, timedelta

def new_arrival(r:redis.Redis, number_plate:str, current_time:datetime)-> bool:
    time_limit = timedelta(minutes=5)
    last_time_str = r.get(number_plate)
    # if the vehicle has not come before or time in Redis has expired
    if last_time_str is None:
        # Save the current time in Redis with the number plate as key
        r.set(number_plate, current_time.isoformat())
        return True
    else:
        # Calculate the time difference
        last_time = datetime.fromisoformat(last_time_str.decode('utf-8'))
        delta_time = current_time - last_time
        
        # Check if the delta_time is greater than the time limit
        if delta_time > time_limit:
            # Update the time in Redis
            r.set(number_plate, current_time.isoformat())
            return True
        else:
            return False