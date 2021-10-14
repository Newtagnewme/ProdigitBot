from os import read
from bot import Prodigit
import json 
import sys
 
def Start(): 
    Buldings = {1: 'CU028', 2: 'RM025', 3 : "Exit"}

    print(' \n Welcome to Prodigit Bot Please Choose one of the following! \n ')

    for key, value in Buldings.items(): 
        print(f'{key} : {value}')

    Choice = input('Please choose one, type either 1 or 2 or 3: ')


    while True:
        try: 
            if int(Choice) == 1: 
                Chosen_Building =  Buldings[1]
                return Chosen_Building
            elif int(Choice) == 2: 
                Chosen_Building =  Buldings[2]
                return Chosen_Building
            elif int(Choice) == 3: 
                break 
            else: 
                print('Input Give Not Valid Try Again...') 
                continue 
        except TypeError: 
            print('Value given not an Int, try agian! ')
            continue

        except Exception as e: 
            print(f'Exception {e}')
            continue 
    
    print(f'Closing Script.. GoodBye')
    sys.exit()


if __name__ == "__main__": 
    with open('settings.json', 'r') as file: 
        j = json.load(file)

        Username = j['Usernumber']
        Password = j['Password']
        MaxRetries = j['MaxRetries']
    
    Building = Start()

    Bot = Prodigit(Username, Password, MaxRetries, Building)
    if Bot.login(): 
        Bot.BookSeat()
        Bot.BookSeat1()
        Bot.BookSeat2()
        Bot.BookSeat3()
        Bot.BookSeat4()
        Bot.BookSeat5()