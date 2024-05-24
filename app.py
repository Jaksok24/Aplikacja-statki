import sqlite3
from datetime import date as day
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import hashlib
import logging
from logging import getLogger

# Konfiguracja strony
st.set_page_config(page_title="Statki", page_icon=":ship:", layout="wide")

app_logger = getLogger()
app_logger.addHandler(logging.StreamHandler())
app_logger.setLevel(logging.INFO)

#Style
title_style = "color: White; background-color: #262730; text-align: Center; border-radius: 10px;"
info_style = "color: White; background-color: #85C1C1; text-align: Center; border-radius: 10px; font-weight: bold;"
tab_config = '''<style> .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size:2rem; } </style> '''      

#Łączenia się z bazą danych
conn = sqlite3.connect('statki_database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS rejs (id INTEGER PRIMARY KEY, customer TEXT, date DATE, hour TIME, ship TEXT, fee BOOLEAN, people INTEGER, nb TEXT, cruise TEXT, fee_cost INTEGER, catering TEXT, note TEXT, dc TEXT, checked TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS dinners (dID INTEGER PRIMARY KEY, dinner TEXT, data DATE, hour_start TIME, hour_stop TIME, people INEGER, checked TEXT)''')

#Tablice/zmienne wykorzystywane dla całej aplikacji
current_time = datetime.now().strftime("%H:%M")
today = day.today()
albatros = []
biala_mewa = []
kormoran = []
ckt_vip = []
tablicaDanych = []
tablicaDanych2 = []
editData = []

#Klasa szczegółowych danych o statkach
class Details:
    def __init__(self, id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note, check):
        self.id = id
        self.customer = customer
        self.dc = dc
        self.nb = nb
        self.date = date
        self.hour = hour
        self.cruise = cruise
        self.ship = ship
        self.people = people
        self.fee = fee
        self.fee_cost = fee_cost
        self.catering = catering
        self.note = note
        self.check = check
        
    def printData(self):
        data = [f"Imię i nazwisko: {self.customer}", f"Numer telefonu: {self.dc} {self.nb}", f"Data rejsu: {self.date}", f"Godzina: {self.hour}", self.cruise, f"Liczba ludzi: {self.people}", f"Zaliczka: {self.fee}", f"Kwota zaliczki: {self.fee_cost} PLN", f"Katering: {self.catering}", f"Notatki: {self.note}"]
        return data

#Klasa rejsów do strony głównej
class Cruise:
    def __init__(self, id, hour, people, ship, cruise, catering, check, date):
        self.id = id
        self.hour = hour
        self.people = people
        self.ship = ship
        self.cruise = cruise
        self.catering = catering
        self.check = check
        self.date = date

#Klasa do informacji o obiadach
class Dinner:
    def __init__(self, dID, hour_start, hour_stop, group, name, empty1, check, date):
        self.dID = dID
        self.hour_start = hour_start
        self.hour_stop = hour_stop
        self.group = group
        self.name = name
        self.empty1 = empty1
        self.check = check
        self.date = date

def switchPage(page):
    st.session_state.page = page

#Zapisz do DataFrame wszystkie dane z tabeli
def showAllData():
    c.execute("SELECT customer, dc, nb, ship, date, hour, cruise, people, fee, fee_cost, catering, note, id FROM rejs ORDER BY date, hour")
    df = pd.DataFrame([row for row in c.fetchall()], columns=("Imię i nazwisko", "Kierunkowy", "Nr tel", "Statek", "Data", "Godzina", "Rejs", "Ilość ludzi", "Zaliczka", "Kwota zaliczki", "Katering", "Notatki", "ID"))
    return df

#Funkcja dodająca przewidywany czas powrotu
def timeCruise(elem):
    global new_time
    time = datetime.strptime(elem.hour, '%H:%M')
    if elem.cruise == "Po rzekach i jeziorach - 1h":
        new_time = time + timedelta(hours=1)
        return new_time
    elif elem.cruise == "Fotel Papieski - 1h":
        new_time = time + timedelta(hours=1)
        return new_time
    elif elem.cruise == "Kanał Augustowski - 1h":   
        new_time = time + timedelta(hours=1)
        return new_time
    elif elem.cruise == "Dolina Rospudy - 1,5h":
        new_time = time + timedelta(hours=1, minutes=30)
        return new_time
    elif elem.cruise == "Szlakiem Papieskim - 3h":
        new_time = time + timedelta(hours=3)
        return new_time
    elif elem.cruise == "Staw Swoboda - 4h":
        new_time = time + timedelta(hours=4)
        return new_time
    elif elem.cruise == "Gorczyca - „Pełen Szlak Papieski” - 6h":
        new_time = time + timedelta(hours=6)
        return new_time
    else:
        return None

#Wybierz dzień
def choiceTheDay():
    columns = st.columns([1,1,1,1])
    with columns[0]:
        theDay = st.date_input("Wybierz dzień")
    return theDay

#Pobieranie spisu wszystkich aktywności w danym dniu z bazy danych
def getShortData(theDay):
    c.execute(f'''SELECT * FROM
              (SELECT id, hour, SUM(people), ship, cruise, catering, checked, date FROM rejs GROUP BY hour, ship, cruise
              UNION
              SELECT dID, hour_start as hour, hour_stop, people, dinner, ' ', checked, data as date FROM dinners)
              WHERE date='{theDay}' ORDER BY hour''')
    for elem in c.fetchall():
        if elem[6] == 'cruise':
            cruiseInfo = Cruise(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6], elem[7])
            tablicaDanych.append(cruiseInfo)
        else:
            dinnerInfo = Dinner(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6], elem[7])
            tablicaDanych.append(dinnerInfo)
            
#Wyświetl skrócone dane o rejsie na dany dzień
def printData(): 
    st.markdown('''<table style="border: 0; border-collapse: collapse; border: 0; text-align: Center; width: 100%;">
                <tr style="border: 0;">
                <td style="border: 0; width: 20%"><h3>Godzina</h3></td>
                <td style="border: 0; width: 20%"><h3>Rejs</h3></td>
                <td style="border: 0; width: 20%;"><h3>Osoby</h3></td>
                <td style="border: 0; width: 20%;"><h3>Statek</h3></td>
                <td style="border: 0; width: 20%;"><h3>Catering</h3>
                </td></tr></table><br>''', unsafe_allow_html=True)
    for elem in tablicaDanych:  
        if elem.check == 'cruise':
            timeCruise(elem)
            time_str2 = new_time.strftime('%H:%M')
            st.markdown(f'''<table style="border-collapse: collapse; border: 0; border-radius: 12px; text-align: Center; width: 100%; background-color: #7B68EE; color: Black;">
                        <tr style="border: 0;">
                        <td style="width: 20%; border: 0;">{elem.hour} - {time_str2}</td>
                        <td style="width: 20%; border: 0;">{elem.cruise}</td>
                        <td style="width: 20%; border: 0;">{elem.people} osób</td>
                        <td style="width: 20%; border: 0;">{elem.ship}</td>
                        <td style="width: 20%; border: 0;">{elem.catering}</td>
                        </tr></table><br>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''<table style="border-collapse: collapse; border: 0; border-radius: 12px; text-align: Center; width: 100%; background-color: #DAA520; color: Black;">
                        <tr style="border: 0;">
                        <td style="width: 20%; border: 0;">{elem.hour_start} - {elem.hour_stop}</td>
                        <td style="width: 20%; border: 0;"></td>
                        <td style="width: 20%; border: 0;">{elem.group} osób</td>
                        <td style="width: 20%; border: 0;"></td>
                        <td style="width: 20%; border: 0;">{elem.name}</td>
                        </tr></table><br>''', unsafe_allow_html=True)

#Pobieranie z bazy danych skróconych informacji o wszystkich rejsach
def getShortDataForAll():
    c.execute('''SELECT id, hour, SUM(people), ship, cruise, catering, checked, date FROM rejs GROUP BY hour, ship, cruise ORDER BY date, hour''')
    for elem in c.fetchall():
        cruiseInfo = Cruise(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6], elem[7])
        tablicaDanych2.append(cruiseInfo)

#Funkcja do wyświetlania skróconych danych o rejsach dla wszystkich dni
def printDataForAll():
    st.markdown('''<table style="border: 0; border-collapse: collapse; border: 0; text-align: Center; width: 100%;">
                <tr style="border: 0;">
                <td style="border: 0; width: 16%"><h3>Data</h3></td>
                <td style="border: 0; width: 16%"><h3>Godzina</h3></td>
                <td style="border: 0; width: 16%"><h3>Rejs</h3></td>
                <td style="border: 0; width: 16%;"><h3>Osoby</h3></td>
                <td style="border: 0; width: 16%;"><h3>Statek</h3></td>
                <td style="border: 0; width: 16%;"><h3>Catering</h3>
                </td></tr></table><br>''', unsafe_allow_html=True)
    for elem in tablicaDanych2:
        timeCruise(elem)
        time_str3 = new_time.strftime('%H:%M')
        st.markdown(f'''<table style="border-collapse: collapse; border: 0; border-radius: 12px; text-align: Center; width: 100%; background-color: #7B68EE; color: Black;">
                        <tr style="border: 0;">
                        <td style="width: 16%; border: 0">{elem.date}</td>
                        <td style="width: 16%; border: 0;">{elem.hour} - {time_str3}</td>
                        <td style="width: 16%; border: 0">{elem.cruise}</td>
                        <td style="width: 16%; border: 0">{elem.people} osób</td>
                        <td style="width: 16%; border: 0">{elem.ship}</td>
                        <td style="width: 16%; border: 0">{elem.catering}</td>
                        </tr></table><br>''', unsafe_allow_html=True)

#Zapisywanie danych do poszczególnych tablic
def saveDataToArray():
    c.execute(f"SELECT id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note, checked FROM rejs WHERE date='{theDay2}' ORDER BY hour")
    for row in c.fetchall():
        cruiseInfo = Details(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
        if cruiseInfo.ship == "Albatros":
            albatros.append(cruiseInfo)
        if cruiseInfo.ship == "Biała Mewa":
            biala_mewa.append(cruiseInfo)
        if cruiseInfo.ship == "Kormoran":
            kormoran.append(cruiseInfo)
        if cruiseInfo.ship == "CKT VIP":
            ckt_vip.append(cruiseInfo)
    
#Wyświetlanie szczegółowych informacji o rejsach
def showDetails(shipTable):
    for i, object in enumerate(shipTable):
        timeCruise(object)
        time_str = new_time.strftime('%H:%M')
        st.markdown(f"<p style=\"{info_style}\">{object.hour} - {time_str}<br>{object.cruise}<br>Ilość osób: {object.people}<p>", unsafe_allow_html=True)
        with st.expander("Szczegóły"):
            for info in object.printData():
                st.write(info)
        
#Dodawanie informacji o rejsie
def addCruiseInfo():
    with st.container(border=True):
        columns = st.columns([1,1])
        with columns[0]:
            customer = st.text_input("Podaj imię i nazwisko")
            date = st.date_input("Podaj dzień", value="today", format="DD.MM.YYYY", label_visibility="visible")
            ship = st.selectbox("Wybierz statek", ["Albatros", "Biała Mewa", "Kormoran", "CKT VIP", ""])
            fee = st.selectbox("Zaliczka", ["Nie", "Tak"])
            if ship == "Albatros":
                people = st.number_input("Ilość osób", step=1, max_value=60, min_value=0)
            else:
                people = st.number_input("Ilość osób", step=1, max_value=12, min_value=0)
        with columns[1]:
            phone_column = st.columns([1,3])
            with phone_column[0]:
                dc = st.selectbox("Kierunkowy", ["🇵🇱 +48", "🇷🇺 +7", "🇩🇪 +49", "🇱🇹 +370", "🇱🇻 +371", "🇪🇪 +372", "🇺🇦 +380", "🇨🇿 +420", "🇸🇰 +421"])
            with phone_column[1]:
                nb = st.text_input("Podaj numer telefonu")
            hour = st.time_input("Podaj godzinę")  
            cruise = st.selectbox("Wybierz rejs", ["Po rzekach i jeziorach - 1h", "Fotel Papieski - 1h", "Kanał Augustowski - 1h", "Dolina Rospudy - 1,5h", "Szlakiem Papieskim - 3h", "Staw Swoboda - 4h", "Gorczyca - „Pełen Szlak Papieski” – 6h", "Paniewo", ""])
            fee_cost = st.number_input("Kwota zaliczki")
            catering = st.selectbox("Katering", ["Tak", "Nie"])
        note = st.text_area("Notatki")
        add_button = st.button("Zapisz")
    if add_button:
        if customer != "" and nb != "":
            hour_str = hour.strftime("%H:%M")
            c.execute("INSERT INTO rejs (customer, date, hour, ship, fee, people, nb, cruise, fee_cost, catering, note, dc, checked) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'cruise')",
                    (customer, date, hour_str, ship, fee, people, nb, cruise, fee_cost, catering, note, dc))
            conn.commit()
            st.success("Dane zostały dodane pomyślnie")
        else:
            st.warning("Wprowadź dane", icon="🚨")
            
#Dodawanie informacji o obiadach
def addDinner():
     with st.container(border=True):
         dinner = st.text_area("Podaj obiad", key="dinner_add1")
         group = st.number_input("Podaj liczbę osób", min_value=0, step=1, key="dinner_add2")
         dinCol = st.columns([1,1])
         with dinCol[0]:
            date = st.date_input("Podaj date", key="dinner_add3")
         with dinCol[1]:
            dinCol2 = st.columns([1,1])
            with dinCol2[0]:
                hour_start = st.time_input("Podaj godzinę rozpoczęcia", key="dinner_add4")
            with dinCol2[1]:
                hour_stop = st.time_input("Podaj godzinę zakończenia", key="dinner_add4+1")
         dinBut = st.button("Dodaj obiad")
         if dinBut:
             if dinner != "":
                hour_str = hour_start.strftime("%H:%M")
                hour_str2 = hour_stop.strftime("%H:%M")
                c.execute('''INSERT INTO dinners (dinner, data, hour_start, hour_stop, people, checked) VALUES (?,?,?,?,?, 'dinner')''', (dinner, date, hour_str, hour_str2, group))
                conn.commit()
                st.success("Dodano obiad")
                selected = "Strona główna"

#Edytowanie danych
def editInfo():
    c.execute('''SELECT * FROM
              (SELECT id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note, checked FROM rejs
              UNION
              SELECT dID, hour_start as hour, hour_stop, people, dinner, ' ', ' ', data as date, ' ', ' ', ' ', ' ', ' ', checked FROM dinners)
              ORDER BY hour, date''')
    for row in c.fetchall():
        if row[13] == 'cruise':
            cruiseInfo = Details(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], int(row[8]), row[9], row[10], row[11], row[12], row[13])
            editData.append(cruiseInfo)
        else:
            dinnerInfo = Dinner(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            editData.append(dinnerInfo)
    for i, elem in enumerate(editData):
        if elem.check == 'cruise':
            st.write(f"Rejs nr {elem.id}")
            with st.popover(f"{elem.customer} | {elem.ship} | {elem.cruise} | {elem.date} | {elem.hour}", use_container_width=True):
                editCruiseInfo(i, elem)
        else:
            st.write(f"Obiad nr {elem.dID}")
            with st.popover(f"{elem.name} | {elem.date} | {elem.hour_start} - {elem.hour_stop}", use_container_width=True):
                editDinnerInfo(i, elem)

#Inputy pobierające dane z rekordów tabeli
def editCruiseInfo(i, obj):
    columns = st.columns([1,1])
    with columns[0]:
        customer = st.text_input("Imię i nazwisko", value=obj.customer, key=f"a{i}")
        date = st.date_input("Dzień", value=datetime.strptime(obj.date, "%Y-%m-%d").date(), format="DD.MM.YYYY", min_value=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), key=f"b{i}")
        ship = st.selectbox("Statek", ["Albatros", "Biała Mewa", "Kormoran", "CKT VIP"], index=["Albatros", "Biała Mewa", "Kormoran", "CKT VIP", None].index(obj.ship), key=f"c{i}")
        fee = st.selectbox("Zaliczka", ["Nie", "Tak"], index=["Nie", "Tak"].index(obj.fee), key=f"d{i}")
        people = st.number_input("Ilość osób", step=1, max_value=60, min_value=0, value=obj.people, key=f"e{i}")
    with columns[1]:
        phone_column = st.columns([1,3])
        with phone_column[0]:
            dc = st.selectbox("Kierunkowy", ["🇵🇱 +48", "🇷🇺 +7", "🇩🇪 +49", "🇱🇹 +370", "🇱🇻 +371", "🇪🇪 +372", "🇺🇦 +380", "🇨🇿 +420", "🇸🇰 +421"], index=["🇵🇱 +48", "🇷🇺 +7", "🇩🇪 +49", "🇱🇹 +370", "🇱🇻 +371", "🇪🇪 +372", "🇺🇦 +380", "🇨🇿 +420", "🇸🇰 +421"].index(obj.dc), key=f"f{i}")
        with phone_column[1]:
            nb = st.text_input("Numer telefonu", value=obj.nb, key=f"g{i}")
        hour = st.time_input("Godzina", value=datetime.strptime(obj.hour, '%H:%M').time(), key=f"h{i}")
        cruise = st.selectbox("Rejs", ["Po rzekach i jeziorach - 1h", "Fotel Papieski - 1h", "Kanał Augustowski - 1h", "Dolina Rospudy - 1,5h", "Szlakiem Papieskim - 3h", "Staw Swoboda - 4h", "Gorczyca - „Pełen Szlak Papieski” – 6h", "Paniewo"], index=["Po rzekach i jeziorach - 1h", "Fotel Papieski - 1h", "Kanał Augustowski - 1h", "Dolina Rospudy - 1,5h", "Szlakiem Papieskim - 3h", "Staw Swoboda - 4h", "Gorczyca - „Pełen Szlak Papieski” – 6h", "Paniewo"].index(obj.cruise), key=f"i{i}")
        fee_cost = st.number_input("Kwota zaliczki", value=obj.fee_cost, key=f"j{i}")
        catering = st.selectbox("Katering", ["Tak", "Nie"], index=["Tak", "Nie"].index(obj.catering), key=f"k{i}")
    note = st.text_area("Notatki", value=obj.note, key=f"l{i}")
    cb = st.columns([1,1,1,1,1])
    with cb[0]:
        accept_changes_button = st.button("Zapisz zmiany", key=f"m{i}")
    with cb[4]:
        delete_button = st.button("Usuń", key=f"n{i}")
    if accept_changes_button:
        hour_str = hour.strftime("%H:%M")
        date_str = date.strftime("%Y-%m-%d")
        c.execute("UPDATE rejs SET customer = ?, dc = ?, nb = ?, date = ?, hour = ?, cruise = ?, ship = ?, people = ?, fee = ?, fee_cost = ?, catering = ?, note = ? WHERE id = ?",
            (customer, dc, nb, date_str, hour_str, cruise, ship, people, fee, fee_cost, catering, note, obj.id))
        conn.commit()
        st.success( "Zaktualizowano dane")
    if delete_button:
        c.execute(f"DELETE FROM rejs WHERE id = {object.id}")
        conn.commit()
        st.success(f"Usunięto dane")

#dID, hour, group, name, empty1, empty2, check, date
def editDinnerInfo(i, obj):
    dinner = st.text_area("Podaj obiad", value=obj.name, key=f"dinner_a{i}")
    group = st.number_input("Podaj liczbę osób", min_value=0, step=1, value=obj.group, key=f"dinner_b{i}")
    dinCol = st.columns([1,1])
    with dinCol[0]:
        date = st.date_input("Podaj date", value=datetime.strptime(obj.date, "%Y-%m-%d").date(), format="DD.MM.YYYY", min_value=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), key=f"dinner_c{i}")
    with dinCol[1]:
        dinCol2 = st.columns([1,1])
        with dinCol2[0]:
            hour_start = st.time_input("Podaj godzinę rozpoczęcia", value=datetime.strptime(obj.hour_start, '%H:%M').time(), key=f"dinner_d{i}")
        with dinCol2[1]:
            hour_stop = st.time_input("Podaj godzinę zakończenia", value=datetime.strptime(obj.hour_stop, '%H:%M').time(), key=f"dinner_2d{i}")
    cb = st.columns([1,1,1,1,1])
    with cb[0]:
        accept_changes_button_dinner = st.button("Zapisz zmiany", key=f"m{i}")
    with cb[4]:
        delete_button_dinner = st.button("Usuń", key=f"n{i}")
    if accept_changes_button_dinner:
        hour_str = hour_start.strftime("%H:%M")
        hour_str2 = hour_stop.strftime("%H:%M")
        date_str = date.strftime("%Y-%m-%d")
        c.execute("UPDATE dinners SET dinner = ?, data = ?, hour_start = ?, hour_stop = ?, people = ? WHERE dID = ?", (dinner, date_str, hour_str, hour_str2, group, obj.dID))
        conn.commit()
        st.success( "Zaktualizowano dane")
    if delete_button_dinner:
            c.execute(f"DELETE FROM dinners WHERE dID = {obj.dID}")
            conn.commit()
            st.success("Usunięto dane")
 
#Ustawienia SideBar
with st.sidebar:
    selected = option_menu(
        menu_title = "Port Katamaranów",
        options = ["Strona główna", "Panel zarządzania", "Szczegóły", "Historia"],
        icons = ["house", "pencil-square", "book", "clock-history"],
        menu_icon="tsunami",
        default_index = 0,
    )

#Strona główna
if (selected == "Strona główna"):
    tab_1, tab_2 = st.tabs(["WYBRANY DZIEŃ :sunrise:", "WSZYSTKO :scroll:"])
    with tab_1:
        theDay = choiceTheDay()
        getShortData(theDay)
        printData()
    with tab_2:
        getShortDataForAll()
        printDataForAll()
   
#Szczegóły rejsów
if (selected == "Szczegóły"):
    st.title("Szczegóły rejsów :ship:")

    theDay2 = choiceTheDay()
    saveDataToArray()

    #Wyświetl dane
    scr = st.columns([1,1,1,1])
    albatros_tab, biala_mewa_tab, kormoran_tab, ckt_vip_tab = st.tabs(["Albatros", "Biała mewa", "Kormoran", "CKT VIP"])
    with albatros_tab: 
        st.markdown(f"<h3 style=\"{title_style}\">Albatros<p>Limit osób: 60</p></h3>", unsafe_allow_html=True)
        st.divider()
        showDetails(albatros)
    with biala_mewa_tab:
        st.markdown(f"<h3 style=\"{title_style}\">Biała Mewa<p>Limit osób: 12</p></h3>", unsafe_allow_html=True)
        st.divider()
        showDetails(biala_mewa)
    with kormoran_tab:
        st.markdown(f"<h3 style=\"{title_style}\">Kormoran<p>Limit osób: 12</p></h3>", unsafe_allow_html=True)
        st.divider()
        showDetails(kormoran)
    with ckt_vip_tab:
        st.markdown(f"<h3 style=\"{title_style}\">CKT VIP<p>Limit osób: 12</p></h3>", unsafe_allow_html=True)
        st.divider()
        showDetails(ckt_vip)

#Panel zarządzania danymi
if selected == "Panel zarządzania":
    tab1, tab2, tab3 = st.tabs(["DODAJ REJS :anchor:", "DODAJ OBIAD :knife_fork_plate:", "EDYTUJ DANE :pencil:"])
    with tab1:
        addCruiseInfo()
    with tab2:
        addDinner()
    with tab3:
        editInfo()

#Historia
if (selected == "Historia"):
    st.markdown("<h1 style=\"background-color: #85C1C1; color: #FFFFFF; border-radius: 10px; font-weight: bold; padding-left: 1rem;\">Historia rejsów<h1>", unsafe_allow_html=True)
    history = showAllData()
    st.dataframe(history)

conn.close()
