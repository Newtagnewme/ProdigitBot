import datetime 


def Log(message):
    time = str(datetime.datetime.now())
    print(f'[{str(time)}] - {message}')
