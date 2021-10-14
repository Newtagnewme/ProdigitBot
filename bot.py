import time 
from requests.sessions import session
from log import Log
import requests 
from bs4 import BeautifulSoup 
import json 

class Prodigit: 
    def __init__(self, username: str, password: str, maxretries : int, building: str):
        self.session = requests.session()

        self.username = username
        self.password = password 
        
        self.maxretries = maxretries
        self.retries = 0

        self.building = building
        with open('schedule.json', 'r') as file: 
            self.j = json.load(file)

            
    def login(self): 
        Log('Logging in')
        
        while True: 
            data = {
                #'%%ModDate': '00002CFF00007F5C',
                'Username': self.username,
                'Password': self.password,
                'RedirectTo': 'https://prodigit.uniroma1.it/home.nsf/home',
                '$PublicAccess': '1',
                'ReasonType': '0',
                '$$HTMLTagAttributes': 'lang="en"'
            }

            self.session.headers.update = {
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Upgrade-Insecure-Requests': '1',
                'Origin': 'https://prodigit.uniroma1.it',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Referer': 'https://prodigit.uniroma1.it/',
                'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
            }

            try:
                response = self.session.post('https://prodigit.uniroma1.it/names.nsf?Login', data=data)

                if response.status_code == 200: 
                    
                
                    if response.url == 'https://prodigit.uniroma1.it/home.nsf/home': 
                        soup = BeautifulSoup(response.text, 'html.parser')
                        div = soup.find('form',{'name': '_home'}).find('div',{'align': 'center'}).find('table').find_all('tr')[2].find('div',{'align': 'center'}).find('font').text
                        if len(div) == 78 and 'prenotazione aule' in div: 
                            Log(f'Successfully Logged in user number: {self.username}')

                            return True

                    elif response.url == 'https://prodigit.uniroma1.it/names.nsf?Login':
                        soup = BeautifulSoup(response.text, 'html.parser')
                        errordiv = soup.find('table',{'id': 'LoginUserFormTable1'}).find_all('tr')[1].find('div',{'align': 'center'}).find('font').text.replace('Inserire i dati richiesti:','').strip()
                        if 'Autenticazione non effettuata' in errordiv: 
                            Log(f'Cannot Log in Message [{errordiv}]')
                            self.retries += 1
                            if self.retries == self.maxretries: 
                                Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                                return False 

                            continue
                    
                    else: 
                        self.retries += 1
                        Log(f'Unparsed Error, Recived Uknown Url [{response.url}]')
                        if self.retries == self.maxretries: 
                            Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                            return False 
                    
                    continue

                else: 
                    self.retries += 1
                    Log(f'Bad Response Recived While Logging In - Status Code [{response.status_code}]')
                    if self.retries == self.maxretries: 
                        Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                        return False 
                
                    continue

                
            except TimeoutError: 
                Log('Site Timed Out')
                continue
            except Exception as e:
                self.retries += 1
                Log(f'Exception Occurred {e}')
                if self.retries == self.maxretries: 
                    Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                    return False 
            
                continue
                    
    def BookSeat(self): 
        Log('Checking User... ')
        while True: 
            try:
                self.session.headers.update = {
                    'Connection': 'keep-alive',
                    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': 'https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula?OpenForm&Seq=1',
                    'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
                    'If-Modified-Since': 'Sun, 03 Oct 2021 13:00:20 GMT',
                }

                response = self.session.get('https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula')

                if response.status_code == 200: 
                    soup = BeautifulSoup(response.text, 'html.parser')

                    self.iddoc = soup.find('input', {'name': 'iddoc'})['value']
                    self.fiscalcode = soup.find('input', {'name': 'codicefiscale'})['value']
                    self.name = soup.find('input', {'name': 'nome'})['value']
                    self.lastname = soup.find('input', {'name': 'cognome'})['value']
                    self.email = soup.find('input', {'name': 'email'})['value']
                    self.week = soup.find('input', {'name': 'controllomatr'})['value']
                    self.checknumber = soup.find('input', {'name': 'controllomatricole'})['value']
                    Log(f'Logged into: {self.name} {self.lastname}')
        
                    return 

                else: 
                    self.retries += 1
                    Log(f'Bad Response Recived While Logging In - Status Code [{response.status_code}]')
                    if self.retries == self.maxretries: 
                        Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                        return False 
                
                    continue
            
            except TimeoutError: 
                Log('Site Timed Out')
                continue
            except Exception as e:
                self.retries += 1
                Log(f'Exception Occurred {e}')
                if self.retries == self.maxretries: 
                    Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                    return False 
            
                continue

    def BookSeat1(self): 
        Log(f'Retiving Avaliable Classes for the building: {self.building}')
        
        while True:
            try:
                self.session.headers.update = {
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1',
                    'Origin': 'https://prodigit.uniroma1.it',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': 'https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula',
                    'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
                }

                params = (
                    ('OpenForm', ''),
                    ('Seq', '1'),
                )

                data = {
                    '__Click': '$Refresh',
                    '%%Surrogate_codiceedificio': '1',
                    'codiceedificio': self.building,
                    'database': 'prenotazioni/prenotaaule.nsf',
                    'ruolodomino': '$$WebClient',
                    'utente': self.username,
                    'form': 'prenotaposto-in-aula',
                    'ruolo': 'studente',
                    'iddoc': self.iddoc,
                    'cancella': '',
                    'recorddeleted': '',
                    'SaveOptions': '0',
                    'matricola': self.username,
                    'codicefiscale': self.fiscalcode,
                    'numerobadge': '',
                    'corsodistudio': '',
                    'cognome': self.lastname,
                    'nome': self.name,
                    'codicecorso': '',
                    'email': self.email,
                    'facolta': '',
                    'nuovo_documento': '0',
                    'fila': '',
                    'posto': '',
                    'seriale': '',
                    'codicesiram': '',
                    'webdb': '/prenotazioni/prenotaaule.nsf/',
                    'Message': '',
                    'cancellato': 'NO',
                    'flag': '0',
                    'controllomatricole': self.checknumber,
                    'numerosettimane': '',
                    'appo': '',
                    'directoryaule': 'prenotazioni/prenotaaule.nsf',
                    'directory': 'prenotazioni',
                    'servername': 'prodigit.uniroma1.it',
                    'appo22': '',
                    'systemreaders': '[admin]',
                    'userreaders': 'uid=1996149/ou=students/ou=users/dc=uniroma1/dc=it',
                    'prenotaappo': 'SI',
                    'controllomatr': '04/10/2021#',
                    'indirizzo': '',
                    'ubicazione': '',
                    'aula': '--- Seleziona l\'aula ---',
                    'selezsettimana': '--- Seleziona la settimana ---',
                    'data1': '',
                    'dalleore1': '',
                    'alleore1': '',
                    'data2': '',
                    'dalleore2': '',
                    'alleore2': '',
                    'data3': '',
                    'dalleore3': '',
                    'alleore3': '',
                    'data4': '',
                    'dalleore4': '',
                    'alleore4': '',
                    'data5': '',
                    'dalleore5': '',
                    'alleore5': '',
                    'data6': '',
                    'dalleore6': '',
                    'alleore6': '',
                    'dichiarazione': '',
                    '$$HTMLFrontMatter': '<!DOCTYPE html>',
                    '$$HTMLTagAttributes': 'lang="it"',
                    'httpcookie': '1'
                }

                response = self.session.post('https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula', params=params, data=data)
                
                if response.status_code == 200: 
                    soup = BeautifulSoup(response.text, 'html.parser')

                    classes = soup.find_all('table',{'class':'table-striped'})[2].find('select',{'name':'aula'}).text
                    print(classes)
                    #print('\n' + classes)

                    userinput = input('\nPlease copy a class code and paste it in here: ').strip()

                    self.classroom = userinput
                    self.iddoc1 = soup.find('input', {'name': 'iddoc'})['value']
                    self.address = soup.find('input', {'name': 'indirizzo'})['value']
                    self.location = soup.find('input', {'name': 'ubicazione'})['value']

                    Log(f'Class Code Chosen: {self.classroom}')
            

                    return 
                else: 
                    self.retries += 1
                    Log(f'Bad Response Recived Retriving Classes - Status Code [{response.status_code}]')
                    if self.retries == self.maxretries: 
                        Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                        return False 
                
                    continue

            except TimeoutError: 
                Log('Site Timed Out')
                continue

            except Exception as e:
                self.retries += 1
                Log(f'Exception Occurred [1] {e}')
                if self.retries == self.maxretries: 
                    Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                    return False 
            
                continue

    def BookSeat2(self):
        while True:
            try:
                self.session.headers.update = {
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1',
                    'Origin': 'https://prodigit.uniroma1.it',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': 'https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula?OpenForm&Seq=1',
                    'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
                }

                params = (
                    ('OpenForm', ''),
                    ('Seq', '2'),
                )

                data = {
                    '__Click': '$Refresh',
                    '%%Surrogate_codiceedificio': '1',
                    'codiceedificio': self.building,
                    '%%Surrogate_aula': '1',
                    'aula': self.classroom,
                    'database': 'prenotazioni/prenotaaule.nsf',
                    'ruolodomino': '$$WebClient',
                    'utente': self.username,
                    'form': 'prenotaposto-in-aula',
                    'ruolo': 'studente',
                    'iddoc': self.iddoc1,
                    'cancella': '',
                    'recorddeleted': '',
                    'SaveOptions': '0',
                    'matricola': self.username,
                    'codicefiscale': self.fiscalcode,
                    'numerobadge': '',
                    'corsodistudio': '',
                    'cognome': self.lastname,
                    'nome': self.name,
                    'codicecorso': '',
                    'email': self.email,
                    'facolta': '',
                    'nuovo_documento': '0',
                    'fila': '',
                    'posto': '',
                    'seriale': '',
                    'codicesiram': '',
                    'webdb': '/prenotazioni/prenotaaule.nsf/',
                    'Message': '',
                    'cancellato': 'NO',
                    'flag': '0',
                    'controllomatricole': self.checknumber,
                    'numerosettimane': '',
                    'appo': '',
                    'directoryaule': 'prenotazioni/prenotaaule.nsf',
                    'directory': 'prenotazioni',
                    'servername': 'prodigit.uniroma1.it',
                    'appo22': '',
                    'systemreaders': '[admin]',
                    'userreaders': f'uid={self.username}/ou=students/ou=users/dc=uniroma1/dc=it',
                    'prenotaappo': 'SI',
                    'controllomatr': self.week,
                    'indirizzo': self.address,
                    'ubicazione': self.location,
                    'selezsettimana': '--- Seleziona la settimana ---',
                    'data1': '',
                    'dalleore1': '',
                    'alleore1': '',
                    'data2': '',
                    'dalleore2': '',
                    'alleore2': '',
                    'data3': '',
                    'dalleore3': '',
                    'alleore3': '',
                    'data4': '',
                    'dalleore4': '',
                    'alleore4': '',
                    'data5': '',
                    'dalleore5': '',
                    'alleore5': '',
                    'data6': '',
                    'dalleore6': '',
                    'alleore6': '',
                    'dichiarazione': '',
                    '$$HTMLFrontMatter': '<!DOCTYPE html>',
                    '$$HTMLTagAttributes': 'lang="it"',
                    'httpcookie': '1'
                }

                response = self.session.post('https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula', params=params, data=data)


                if response.status_code == 200: 
                    soup = BeautifulSoup(response.text, 'html.parser')


                    self.iddoc2 = soup.find('input', {'name': 'iddoc'})['value']
                    Log(f'Successfully Sent Payload [2]')

                    return
                else:   
                    self.retries += 1
                    Log(f'Bad Response Recived Retriving Classes - Status Code [{response.status_code}]')
                    if self.retries == self.maxretries: 
                        Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                        return False 
                
                    continue
                
            except TimeoutError: 
                Log('Site Timed Out')
                continue

            except Exception as e:
                self.retries += 1
                Log(f'Exception Occurred [2] {e}')
                if self.retries == self.maxretries: 
                    Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                    return False 
            
                continue


    def BookSeat3(self): 

        while True:
            try:
                    
                self.session.headers.update = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Host': 'prodigit.uniroma1.it',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'Upgrade-Insecure-Requests': '1',
                    'Origin': 'https://prodigit.uniroma1.it',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': 'https://prodigit.uniroma1.it/',
                    'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                }

                params = (
                    ('OpenForm', ''),
                    ('Seq', '3'),
                )

                data = {
                    '__Click': '$Refresh',
                    '%%Surrogate_codiceedificio': '1',
                    'codiceedificio': self.building,
                    '%%Surrogate_aula': '1',
                    'aula': self.classroom,
                    '%%Surrogate_selezsettimana': '1',
                    'selezsettimana': self.week.replace('#', ''),
                    'database': 'prenotazioni/prenotaaule.nsf',
                    'ruolodomino': '$$WebClient',
                    'utente': self.username,
                    'form': 'prenotaposto-in-aula',
                    'ruolo': 'studente',
                    'iddoc': self.iddoc2,
                    'cancella': '',
                    'recorddeleted': '',
                    'SaveOptions': '0',
                    'matricola': self.username,
                    'codicefiscale': self.fiscalcode,
                    'numerobadge': '',
                    'corsodistudio': '',
                    'cognome': self.lastname,
                    'nome': self.name,
                    'codicecorso': '',
                    'email': self.email,
                    'facolta': '',
                    'nuovo_documento': '0',
                    'fila': '',
                    'posto': '',
                    'seriale': '',
                    'codicesiram': self.classroom,
                    'webdb': '/prenotazioni/prenotaaule.nsf/',
                    'Message': '',
                    'cancellato': 'NO',
                    'flag': '0',
                    'controllomatricole': self.checknumber,
                    'numerosettimane': '',
                    'appo': self.week,
                    'directoryaule': 'prenotazioni/prenotaaule.nsf',
                    'directory': 'prenotazioni',
                    'servername': 'prodigit.uniroma1.it',
                    'appo22': '',
                    'systemreaders': '[admin]',
                    'userreaders': f'uid={self.username}/ou=students/ou=users/dc=uniroma1/dc=it',
                    'prenotaappo': 'SI',
                    'controllomatr': self.week,
                    'indirizzo': self.address,
                    'ubicazione': self.location,
                    'data1': '',
                    'dalleore1': '',
                    'alleore1': '',
                    'data2': '',
                    'dalleore2': '',
                    'alleore2': '',
                    'data3': '',
                    'dalleore3': '',
                    'alleore3': '',
                    'data4': '',
                    'dalleore4': '',
                    'alleore4': '',
                    'data5': '',
                    'dalleore5': '',
                    'alleore5': '',
                    'data6': '',
                    'dalleore6': '',
                    'alleore6': '',
                    'dichiarazione': '',
                    '$$HTMLFrontMatter': '<!DOCTYPE html>',
                    '$$HTMLTagAttributes': 'lang="it"',
                    'httpcookie': '1'
                }

                response = self.session.post('https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula', params=params, data=data)

                if response.status_code == 200: 
                        soup = BeautifulSoup(response.text, 'html.parser')

                        self.iddoc3 = soup.find('input', {'name': 'iddoc'})['value']
                        self.data1 = soup.find('input', {'name': 'data1'})['value']
                        self.data2 = soup.find('input', {'name': 'data2'})['value']
                        self.data3 = soup.find('input', {'name': 'data3'})['value']
                        self.data4 = soup.find('input', {'name': 'data4'})['value']
                        self.data5 = soup.find('input', {'name': 'data5'})['value']
                        self.data6 = soup.find('input', {'name': 'data6'})['value']
                        Log(f'Successfully Scraped Week Days ')

                        return

                elif response.status_code in [501, 502, 503, 504]: 
                    Log(f'Request Error Response status code {response.status_code}, Retrying')
                    continue

                else:   
                    self.retries += 1
                    Log(f'Bad Response Recived Retriving Classes - Status Code [{response.status_code}]')
                    if self.retries == self.maxretries: 
                        Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                        return False 
                
                    continue

           
            except TimeoutError: 
                Log('Site Timed Out')
                continue

            except Exception as e:
                self.retries += 1
                Log(f'Exception Occurred [3] {e}')
                if self.retries == self.maxretries: 
                    Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                    return False 
            
                continue

    
    def BookSeat4(self):

        while True: 
            try:
                self.session.headers.update = {
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1',
                    'Origin': 'https://prodigit.uniroma1.it',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': 'https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula?OpenForm&Seq=4',
                    'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
                }

                params = (
                    ('OpenForm', ''),
                    ('Seq', '4'),
                )

                
                data = {
                    '__Click': '$Refresh',
                    '%%Surrogate_codiceedificio': '1',
                    'codiceedificio': self.building,
                    '%%Surrogate_aula': '1',
                    'aula': self.classroom,
                    '%%Surrogate_selezsettimana': '1',
                    'selezsettimana': self.week.replace('#', ''),
                    '%%Surrogate_dalleore1': '1',
                    'dalleore1': '--:--',
                    '%%Surrogate_alleore1': '1',
                    'alleore1': '--:--',
                    '%%Surrogate_dalleore2': '1',
                    'dalleore2': '--:--',
                    '%%Surrogate_alleore2': '1',
                    'alleore2': '--:--',
                    '%%Surrogate_dalleore3': '1',
                    'dalleore3': '--:--',
                    '%%Surrogate_alleore3': '1',
                    'alleore3': '--:--',
                    '%%Surrogate_dalleore4': '1',
                    'dalleore4': '--:--',
                    '%%Surrogate_alleore4': '1',
                    'alleore4': '--:--',
                    '%%Surrogate_dalleore5': '1',
                    'dalleore5': '--:--',
                    '%%Surrogate_alleore5': '1',
                    'alleore5': '--:--',
                    '%%Surrogate_dalleore6': '1',
                    'dalleore6': '--:--',
                    '%%Surrogate_alleore6': '1',
                    'alleore6': '--:--',
                    '%%Surrogate_dichiarazione': '1',
                    'dichiarazione': ':',
                    'database': 'prenotazioni/prenotaaule.nsf',
                    'ruolodomino': '$$WebClient',
                    'utente': self.username,
                    'form': 'prenotaposto-in-aula',
                    'ruolo': 'studente',
                    'iddoc': self.iddoc3,
                    'cancella': '',
                    'recorddeleted': '',
                    'SaveOptions': '0',
                    'matricola': self.username,
                    'codicefiscale': self.fiscalcode,
                    'numerobadge': '',
                    'corsodistudio': '',
                    'cognome': self.lastname,
                    'nome': self.name,
                    'codicecorso': '',
                    'email': self.email,
                    'facolta': '',
                    'nuovo_documento': '0',
                    'fila': '',
                    'posto': '',
                    'seriale': '',
                    'codicesiram': self.classroom,
                    'webdb': '/prenotazioni/prenotaaule.nsf/',
                    'Message': '',
                    'cancellato': 'NO',
                    'flag': '0',
                    'controllomatricole': self.checknumber,
                    'numerosettimane': '',
                    'appo': self.week,
                    'directoryaule': 'prenotazioni/prenotaaule.nsf',
                    'directory': 'prenotazioni',
                    'servername': 'prodigit.uniroma1.it',
                    'appo22': '',
                    'systemreaders': '[admin]',
                    'userreaders': f'uid={self.username}/ou=students/ou=users/dc=uniroma1/dc=it',
                    'prenotaappo': 'SI',
                    'controllomatr': self.week,
                    'indirizzo': self.address,
                    'ubicazione': self.location,
                    'data1': self.data1,
                    'data2': self.data2,
                    'data3': self.data3,
                    'data4': self.data4,
                    'data5': self.data5,
                    'data6': self.data6,
                    '$$HTMLFrontMatter': '<!DOCTYPE html>',
                    '$$HTMLTagAttributes': 'lang="it"',
                    'httpcookie': '1'
                }

                
                response = self.session.post('https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula', params=params, data=data)
                
                if response.status_code == 200: 
                    soup = BeautifulSoup(response.text, 'html.parser')

                    self.onclick = soup.find('a',{'id':'imghref'})['onclick'].replace('return _doClick','').replace('(','').replace(')','').split(',')[0].replace("'","")
                    self.iddoc4 = soup.find('input', {'name': 'iddoc'})['value']
                    Log(f'Successfully Sent Payload [4]')
                    
                    return

                elif response.status_code in [501, 502, 503, 504]: 
                    Log(f'Request Error Response status code {response.status_code}, Retrying')
                    continue

                else:   
                    self.retries += 1
                    Log(f'Bad Response Recived Retriving Classes - Status Code [{response.status_code}]')
                    if self.retries == self.maxretries: 
                        Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                        return False 
                
                    continue

            except Exception as e:
                self.retries += 1
                Log(f'Exception Occurred [4] {e}')
                if self.retries == self.maxretries: 
                    Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                    return False 
            
                continue

    def BookSeat5(self): 

        while True:
            try:
                self.session.headers.update = {
                    'Connection': 'keep-alive',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1',
                    'Origin': 'https://prodigit.uniroma1.it',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': 'https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula?OpenForm&Seq=4',
                    'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
                }

                params = (
                    ('OpenForm', ''),
                    ('Seq', '5'),
                )

                if self.building.upper() == 'CU028':
                    response = self.session.post('https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula', params=params, data={
                    '__Click': self.onclick,
                    '%%Surrogate_codiceedificio': '1',
                    'codiceedificio': self.building,
                    '%%Surrogate_aula': '1',
                    'aula': self.classroom,
                    '%%Surrogate_selezsettimana': '1',
                    'selezsettimana': self.week.replace('#',''),
                    '%%Surrogate_dalleore1': '1',
                    'dalleore1': self.j[self.building]['Monday']['Start'],
                    '%%Surrogate_alleore1': '1',
                    'alleore1': self.j[self.building]['Monday']['EndTime'],
                    '%%Surrogate_dalleore2': '1',
                    'dalleore2':  self.j[self.building]['Tuesday']['Start'],
                    '%%Surrogate_alleore2': '1',
                    'alleore2': self.j[self.building]['Tuesday']['EndTime'],
                    '%%Surrogate_dalleore3': '1',
                    'dalleore3': self.j[self.building]['Wednesday']['Start'],
                    '%%Surrogate_alleore3': '1',
                    'alleore3': self.j[self.building]['Wednesday']['EndTime'],
                    '%%Surrogate_dalleore4': '1',
                    'dalleore4': '--:--',
                    '%%Surrogate_alleore4': '1',
                    'alleore4': '--:--',
                    '%%Surrogate_dalleore5': '1',
                    'dalleore5': self.j[self.building]['Friday']['Start'],
                    '%%Surrogate_alleore5': '1',
                    'alleore5': self.j[self.building]['Friday']['EndTime'],
                    '%%Surrogate_dalleore6': '1',
                    'dalleore6': '--:--',
                    '%%Surrogate_alleore6': '1',
                    'alleore6': '--:--',
                    '%%Surrogate_dichiarazione': '1',
                    'dichiarazione': ':',
                    'database': 'prenotazioni/prenotaaule.nsf',
                    'ruolodomino': '$$WebClient',
                    'utente': self.username,
                    'form': 'prenotaposto-in-aula',
                    'ruolo': 'studente',
                    'iddoc': self.iddoc4,
                    'cancella': '',
                    'recorddeleted': '',
                    'SaveOptions': '0',
                    'matricola': self.username,
                    'codicefiscale': self.fiscalcode,
                    'numerobadge': '',
                    'corsodistudio': '',
                    'cognome': self.lastname,
                    'nome': self.name,
                    'codicecorso': '',
                    'email': self.email,
                    'facolta': '',
                    'nuovo_documento': '0',
                    'fila': '',
                    'posto': '',
                    'seriale': '',
                    'codicesiram': self.classroom,
                    'webdb': '/prenotazioni/prenotaaule.nsf/',
                    'Message': '',
                    'cancellato': 'NO',
                    'flag': '0',
                    'controllomatricole': self.checknumber,
                    'numerosettimane': '',
                    'appo': self.week,
                    'directoryaule': 'prenotazioni/prenotaaule.nsf',
                    'directory': 'prenotazioni',
                    'servername': 'prodigit.uniroma1.it',
                    'appo22': '',
                    'systemreaders': '[admin]',
                    'userreaders': f'uid={self.username}/ou=students/ou=users/dc=uniroma1/dc=it',
                    'prenotaappo': 'SI',
                    'controllomatr': self.week,
                    'indirizzo': self.address,
                    'ubicazione': self.week,
                    'data1': self.data1,
                    'data2': self.data2,
                    'data3': self.data3,
                    'data4': self.data4,
                    'data5': self.data5,
                    'data6': self.data6,
                    '$$HTMLFrontMatter': '<!DOCTYPE html>',
                    '$$HTMLTagAttributes': 'lang="it"',
                    'httpcookie': '1'
                    })
                
                elif self.building.upper() == 'RM025':
                    response = self.session.post('https://prodigit.uniroma1.it/prenotazioni/prenotaaule.nsf/prenotaposto-in-aula', params=params, data = {
                    '__Click': self.onclick,
                    '%%Surrogate_codiceedificio': '1',
                    'codiceedificio': self.building,
                    '%%Surrogate_aula': '1',
                    'aula': self.classroom,
                    '%%Surrogate_selezsettimana': '1',
                    'selezsettimana': self.week.replace('#',''),
                    '%%Surrogate_dalleore1': '1',
                    'dalleore1': '--:--',
                    '%%Surrogate_alleore1': '1',
                    'alleore1': '--:--',
                    '%%Surrogate_dalleore2': '1',
                    'dalleore2':  '--:--',
                    '%%Surrogate_alleore2': '1',
                    'alleore2': '--:--',
                    '%%Surrogate_dalleore3': '1',
                    'dalleore3': self.j[self.building]['Wednesday']['Start'],
                    '%%Surrogate_alleore3': '1',
                    'alleore3': self.j[self.building]['Wednesday']['EndTime'],
                    '%%Surrogate_dalleore4': '1',
                    'dalleore4': '--:--',
                    '%%Surrogate_alleore4': '1',
                    'alleore4': '--:--',
                    '%%Surrogate_dalleore5': '1',
                    'dalleore5': self.j[self.building]['Friday']['Start'],
                    '%%Surrogate_alleore5': '1',
                    'alleore5': self.j[self.building]['Friday']['EndTime'],
                    '%%Surrogate_dalleore6': '1',
                    'dalleore6': '--:--',
                    '%%Surrogate_alleore6': '1',
                    'alleore6': '--:--',
                    '%%Surrogate_dichiarazione': '1',
                    'dichiarazione': ':',
                    'database': 'prenotazioni/prenotaaule.nsf',
                    'ruolodomino': '$$WebClient',
                    'utente': self.username,
                    'form': 'prenotaposto-in-aula',
                    'ruolo': 'studente',
                    'iddoc': self.iddoc4,
                    'cancella': '',
                    'recorddeleted': '',
                    'SaveOptions': '0',
                    'matricola': self.username,
                    'codicefiscale': self.fiscalcode,
                    'numerobadge': '',
                    'corsodistudio': '',
                    'cognome': self.lastname,
                    'nome': self.name,
                    'codicecorso': '',
                    'email': self.email,
                    'facolta': '',
                    'nuovo_documento': '0',
                    'fila': '',
                    'posto': '',
                    'seriale': '',
                    'codicesiram': self.classroom,
                    'webdb': '/prenotazioni/prenotaaule.nsf/',
                    'Message': '',
                    'cancellato': 'NO',
                    'flag': '0',
                    'controllomatricole': self.checknumber,
                    'numerosettimane': '',
                    'appo': self.week,
                    'directoryaule': 'prenotazioni/prenotaaule.nsf',
                    'directory': 'prenotazioni',
                    'servername': 'prodigit.uniroma1.it',
                    'appo22': '',
                    'systemreaders': '[admin]',
                    'userreaders': f'uid={self.username}/ou=students/ou=users/dc=uniroma1/dc=it',
                    'prenotaappo': 'SI',
                    'controllomatr': self.week,
                    'indirizzo': self.address,
                    'ubicazione': self.week,
                    'data1': self.data1,
                    'data2': self.data2,
                    'data3': self.data3,
                    'data4': self.data4,
                    'data5': self.data5,
                    'data6': self.data6,
                    '$$HTMLFrontMatter': '<!DOCTYPE html>',
                    '$$HTMLTagAttributes': 'lang="it"',
                    'httpcookie': '1'
                    })

                else: 
                    pass
                
                
                if response.status_code == 200: 

                    if 'PRENOTAZIONI EFFETTUATE' in response.text: 
                        Log('Successfully Booked Classess, Login and Check')
                        break 

                elif response.status_code in [501, 502, 503, 504]: 
                    Log(f'Request Error Response status code {response.status_code}, Retrying')
                    continue

                else:   
                    self.retries += 1
                    Log(f'Bad Response Recived Retriving Classes - Status Code [{response.status_code}]')
                    if self.retries == self.maxretries: 
                        Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                        return False 
                    
                        continue

            except Exception as e:
                self.retries += 1
                Log(f'Exception Occurred [4] {e}')
                if self.retries == self.maxretries: 
                    Log(f'Max Retries Exceeded limit Set to {self.maxretries}, Stopping Task')
                    return False 
            
                continue
