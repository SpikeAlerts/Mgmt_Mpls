# This is the main python function to call. It iteratively calls MAIN.main() until the designated stop time

# Please set up the database, python environment, & .env files before running this

# change directories to this repository
# Run with a command like "python App/spikealerts.py"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# If on Heroku must add App to path with the following code uncommented to load project modules

# ALSO, will need to change the .env paths in this script, db_conn, all api_functions, ...

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Prep

### Import python libraries

# File Manipulation

import os # For working with Operating System
from dotenv import dotenv_values # Loading .env info
# Add App to system path

import sys

extra_path = os.path.join('App')
if extra_path not in sys.path:
    sys.path.append(extra_path)

# Printing

from pprint import pprint # Pretty Printing

# Time

import datetime as dt # Working with dates/times
import pytz # Timezones
import time # For Sleeping

# Our modules

from modules.db_init import db_need_init # Has the database been initialized?
from modules.MAIN import main # The Main Loop

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Load Configuration (.env)

base_config = {
    **dotenv_values('.env.secret') # Load .env file # environment variables upacked into dicionary
}

 # Remove the database credentials from above
keys_to_drop = [key for key in base_config if 'DB' in key]
for key in keys_to_drop:
    base_config.pop(key)

# Print Config
print('Base Configuration:\n')
pprint(base_config) 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Calculate Global Constants

# timestep = Time in between updates in minutes (integer) 
timestep = int(base_config['TIMESTEP'])

# stoptime = When will we stop the program? (datetime)
days_to_run = int(base_config['DAYS_TO_RUN'])
starttime = dt.datetime.now(pytz.timezone(base_config['TIMEZONE'])) 
stoptime = starttime + dt.timedelta(days=days_to_run)

# next_system_update = The next time for a daily update (new sensors/POIs)    
next_system_update = starttime.replace(hour=8, minute = 0, second = 0) # 8am today

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print(f'''Beginning program

Running until {stoptime}
Updating every {timestep} minutes
Next system update:{next_system_update}
''')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Check database

if db_need_init():
    print('\nERROR:\nNeed to create a database. Please see /Database directory')

else: 

    # Start the loop

    while True:

        # Time
        now = dt.datetime.now(pytz.timezone(base_config['TIMEZONE'])) # Now
        next_regular_update = now + dt.timedelta(minutes=timestep) # The datetime for next regular update

        if stoptime < now: # Check if we've hit stoptime
            break
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Try Main
        
        try:
            print('calling main')
            print('Runtime: ', now)
            next_system_update = main(base_config, now, next_system_update)
            print('made it through main')
            
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # If errors?
        
        except Exception as e:
            print(e)  # Print Error 
            # send_texts([os.environ['LOCAL_PHONE']], ['SpikeAlerts Down']) # Message Manager
            time.sleep(2880*60) # Sleep for two days if errored out
            
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Finally, sleep until next regular update
        
        finally:
            # Calculate how long to sleep 
            # usually close to timestep, but main can take seconds to run 
            now = dt.datetime.now(pytz.timezone(base_config['TIMEZONE'])) # Now
            sleep_seconds = (next_regular_update - now).total_seconds() # Time until next regular update
            print('One iteration Done')
            print('Sleeping for', sleep_seconds, ' seconds')
            
            # Sleep
            time.sleep(sleep_seconds) # Sleep

            #break


# ~~~~~~~~~~~~~~~~~~~~~

# Terminate Program

print("Terminating Program")
# our_twilio.send_texts([os.environ['LOCAL_PHONE']], ['Terminating Program'])
