import time
import datetime
start = datetime.datetime.now().replace(microsecond=0)
try:
    while True:
        print('running')
        time.sleep(1)
except KeyboardInterrupt:
    end = datetime.datetime.now().replace(microsecond=0)
    print(f"Keyboard Interrupt recieved, dying. ran for {end - start}")
