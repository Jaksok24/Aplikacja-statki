import sqlite3
from datetime import date as day
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import hashlib

# Konfiguracja strony
st.set_page_config(page_title="Statki", page_icon=":ship:", layout="wide")

#Style
title_style = "color: White; background-color: #262730; text-align: Center; border-radius: 10px;"
info_style = "color: White; background-color: #85C1C1; text-align: Center; border-radius: 10px; font-weight: bold;"

#Łączenia się z bazą danych
conn = sqlite3.connect('statki_database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS rejs (id INTEGER PRIMARY KEY, customer TEXT, date DATE, hour TIME, ship TEXT, fee BOOLEAN, people INTEGER, nb TEXT, cruise TEXT, fee_cost INTEGER, catering TEXT, note TEXT, dc TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS rejs_new (id INTEGER PRIMARY KEY, customer TEXT, date DATE, hour TIME, ship TEXT, fee BOOLEAN, people INTEGER, nb TEXT, cruise TEXT, fee_cost INTEGER, catering TEXT, note TEXT, dc TEXT)''')

#Klasa danych o statkach
class Ship:
    def __init__(self, id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note):
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
        
    def printData(self):
        data = [f"Imię i nazwisko: {self.customer}", f"Numer telefonu: {self.dc}", f"{self.nb}", f"{self.date}", f"{self.hour}", self.cruise, f"{self.people}", f"Zaliczka: {self.fee}", f"Kwota zaliczki: {self.fee_cost} PLN", f"Katering: {self.catering}", f"Notatki: {self.note}", f"ID: {self.id}"]
        return data

#Klasa rejsów do strony głównej
class Cruise:
    def __init__(self, id, hour, people, cruise, ship, catering):
        self.id = id
        self.hour = hour
        self.people = people
        self.ship = ship
        self.cruise = cruise
        self.catering = catering

    def cruise_id(self):
        a = str(self.cruise) + str(self.hour) + str(self.ship)
        return hashlib.sha256(a.encode()).hexdigest()

#Klasa rejsów do strony głównej na wszystkie dni
class Cruise_all:
    def __init__(self, id, date, hour, people, cruise, ship, catering):
        self.id = id
        self.date = date
        self.hour = hour
        self.people = people
        self.cruise = cruise
        self.ship = ship
        self.catering = catering
        
    def cruise_id_all(self):
        dane_hash2 = str(self.date) + str(self.cruise) + str(self.hour) + str(self.ship)
        return hashlib.md5(dane_hash2.encode()).hexdigest()

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

#Funkcja do dodawania liczby ludzi
def checkCruise(theDay):
    c.execute(f"SELECT id, hour, people, cruise, ship, catering FROM rejs_new WHERE date='{theDay}' ORDER BY hour")
    for elem in c.fetchall():
        object = Cruise(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5])
        for cruise in tablicaDanych:
            if cruise.cruise_id() == object.cruise_id():
                cruise.people += object.people
                break
        else:
            tablicaDanych.append(object)

#Funkcja do dodawania liczby ludzi dla wszystkich rejsów
def checkCruiseForAll():
    c.execute(f"SELECT id, date, hour, people, cruise, ship, catering FROM rejs_new ORDER BY date")
    for elem in c.fetchall():
        cruise_info = Cruise_all(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6])
        for cruise2 in tablicaDanych2:
            if cruise2.cruise_id_all() == cruise_info.cruise_id_all():
                cruise2.people += cruise_info.people
                break
        else:
            tablicaDanych2.append(cruise_info)

#Wyświetl skrócone dane o rejsie na dany dzień
def printData(): 
    ct = st.columns([1,1,1,1,1])
    head_title = ["Godziny", "Osoby", "Rejs", "Statek", "Catering"]
    for i in range(len(head_title)):
        with ct[i]:
            st.header(head_title[i])
    for i, elem in enumerate(tablicaDanych):
        with st.container(border=True):
            ct1 = st.columns([1,1,1,1,1])
            timeCruise(elem)
            time_str2 = new_time.strftime('%H:%M')
            with ct1[0]:
                st.write(f"{elem.hour} - {time_str2}")
            #     edit_button = st.button("Edytuj", key=f"a{i}")
            # if edit_button:
            #     editableInput(elem, i)
            with ct1[1]:
                st.write(str(elem.people))
            with ct1[2]:
                st.write(elem.cruise)
            with ct1[3]:
                st.write(elem.ship)  
            with ct1[4]:
                st.write(elem.catering)
        dlt = st.button(f"Usuń", key=f"b{i}")
        if dlt:
            deleteInfo(elem)

#Funkcja do wyświetlania skróconych danych o rejsach dla wszystkich dni
def printDataForAll():
    ct_all = st.columns([1,1,1,1,1,1])
    head_title_all = ["Data", "Godziny", "Osoby", "Rejs", "Statek", "Catering"]
    for i in range(len(head_title_all)):
        with ct_all[i]:
            st.header(head_title_all[i])
    for i, elem in enumerate(tablicaDanych2):    
        with st.container(border=True):
            ct_all1 = st.columns([1,1,1,1,1,1])
            timeCruise(elem)
            time_str3 = new_time.strftime('%H:%M')
            with ct_all1[0]:  
                st.write(elem.date)
            #     edit_button_all = st.button("Edytuj", key=f"c{i}")
            # if edit_button_all:
            #     st.success("Tu będzie edycja")
            with ct_all1[1]:
                st.write(f"{elem.hour} - {time_str3}")
            with ct_all1[2]:
                st.write(str(elem.people))
            with ct_all1[3]:
                st.write(elem.cruise)
            with ct_all1[4]:
                st.write(elem.ship)
            with ct_all1[5]:
                st.write(elem.catering)
        dlt2 = st.button(f"Usuń", key=f"d{i}")
        if dlt2:
            deleteInfo(elem)

def deleteInfo(object):
    c.execute(f"DELETE FROM rejs_new WHERE id = {object.id}")
    conn.commit()
    c.execute(f"DELETE FROM rejs WHERE id = {object.id}")
    conn.commit()

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
    elif elem.cruise == "":
        new_time = time + timedelta(hours=1)
        return new_time
    else:
        return None

#Wybierz dzień
def choiceTheDay():
    columns = st.columns([1,1,1,1])
    with columns[0]:
        theDay = st.date_input("Wybierz dzień")
    return theDay

#Zapisywanie danych do poszczególnych tablic
def saveDataToArray():
    for row in c.fetchall():
        cruiseInfo = Ship(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])
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
        if st.button("Usuń", key=i):
            deleteInfo(object)

#Całe ustawienia do panelu dodawania informacji
def addCruiseInfo():
    with st.container(border=True):
        columns = st.columns([1,1])
        with columns[0]:
            customer = st.text_input("Podaj imię i nazwisko")
            date = st.date_input("Podaj dzień", value="today", format="DD.MM.YYYY", label_visibility="visible")
            ship = st.selectbox("Wybierz statek", ["Albatros", "Biała Mewa", "Kormoran", "CKT VIP"])
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
            cruise = st.selectbox("Wybierz rejs", ["Po rzekach i jeziorach - 1h", "Fotel Papieski - 1h", "Kanał Augustowski - 1h", "Dolina Rospudy - 1,5h", "Szlakiem Papieskim - 3h", "Staw Swoboda - 4h", "Gorczyca - „Pełen Szlak Papieski” – 6h", "Paniewo"])
            fee_cost = st.number_input("Kwota zaliczki")
            catering = st.selectbox("Catering", ["Tak", "Nie"])
        note = st.text_area("Notatki")
        add_button = st.button("Zapisz")
    if add_button:
        if customer != "" and nb != "":
            hour_str = hour.strftime("%H:%M")
            c.execute("INSERT INTO rejs (customer, date, hour, ship, fee, people, nb, cruise, fee_cost, catering, note, dc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (customer, date, hour_str, ship, fee, people, nb, cruise, fee_cost, catering, note, dc))
            c.execute("INSERT INTO rejs_new (customer, date, hour, ship, fee, people, nb, cruise, fee_cost, catering, note, dc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (customer, date, hour_str, ship, fee, people, nb, cruise, fee_cost, catering, note, dc))
            conn.commit()
            st.success("Dane zostały dodane pomyślnie")
        else:
            st.warning("Wprowadź dane", icon="🚨")   

#Zapisz do DataFrame wszystkie dane z tabeli
def showAllData():
    c.execute("SELECT customer, dc, nb, ship, date, hour, cruise, people, fee, fee_cost, catering, note, id FROM rejs ORDER BY date, hour")
    df = pd.DataFrame([row for row in c.fetchall()], columns=("Imię i nazwisko", "Kierunkowy", "Nr tel", "Statek", "Data", "Godzina", "Rejs", "Ilość ludzi", "Zaliczka", "Kwota zaliczki", "Katering", "Notatki", "ID"))
    return df

#Inputy pobierające dane z rekordów tabeli
def editableInput(obj, i):
    columns = st.columns([1,1])
    with columns[0]:
        customer = st.text_input("Imię i nazwisko", value=obj.customer, key=f"a{i}")
        date = st.date_input("Dzień", value=datetime.strptime(obj.date, "%Y-%m-%d").date(), format="DD.MM.YYYY", min_value=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), key=f"b{i}")
        ship = st.selectbox("Statek", ["Albatros", "Biała Mewa", "Kormoran", "CKT VIP"], index=["Albatros", "Biała Mewa", "Kormoran", "CKT VIP"].index(obj.ship), key=f"c{i}")
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
        catering = st.selectbox("Catering", ["Tak", "Nie"], index=["Tak", "Nie"].index(obj.catering), key=f"k{i}")
    note = st.text_area("Notatki", value=obj.note, key=f"l{i}")
    accept_changes_button = st.button("Zapisz zmiany", key=f"m{i}")
    if accept_changes_button:
        hour_str = hour.strftime("%H:%M")
        date_str = date.strftime("%Y-%m-%d")
        c.execute("UPDATE rejs SET customer = ?, dc = ?, nb = ?, date = ?, hour = ?, cruise = ?, ship = ?, people = ?, fee = ?, fee_cost = ?, catering = ?, note = ? WHERE id = ?",
            (customer, dc, nb, date_str, hour_str, cruise, ship, people, fee, fee_cost, catering, note, obj.id))
        c.execute("UPDATE rejs_new SET customer = ?, dc = ?, nb = ?, date = ?, hour = ?, cruise = ?, ship = ?, people = ?, fee = ?, fee_cost = ?, catering = ?, note = ? WHERE id = ?",
            (customer, dc, nb, date_str, hour_str, cruise, ship, people, fee, fee_cost, catering, note, obj.id))
        conn.commit()
        st.success( "Zaktualizowano dane")

#Edytowanie danych
def editInfo():
    c.execute("SELECT id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note FROM rejs")
    for elem in c.fetchall():
        obj = Ship(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6], elem[7], elem[8], elem[9], elem[10], elem[11], elem[12])
        editData.append(obj)
    for i, elem in enumerate(editData):
        st.write(f"Rejs nr {elem.id}")
        with st.popover(f"{elem.customer} | {elem.ship} | {elem.cruise} | {elem.date} | {elem.hour}", use_container_width=True):
            editableInput(elem, i)

#Ustawienia SideBar (DODAĆ DO LOGOWANIA IKONE "box-arrow-in-right")
with st.sidebar:
    selected = option_menu(
        menu_title = "Port Katamaranów",
        options = ["Strona główna", "Szczegóły", "Panel zarządzania", "Historia"],
        icons = ["house", "book", "pencil-square", "clock-history"],
        menu_icon="tsunami",
        default_index = 0,
    )

#Strona główna
if (selected == "Strona główna"):
    tab_1, tab_2 = st.tabs(["Wybrany dzień", "Wszystko"])
    with tab_1:
        theDay = choiceTheDay()
        checkCruise(theDay)
        printData()
    with tab_2:
        checkCruiseForAll()
        printDataForAll()

#Szczegóły rejsów
if (selected == "Szczegóły"):
    st.title("Szczegóły rejsów :ship:")
    
    #Wybierz dzień
    theDay2 = choiceTheDay()

    #Zapis wybranych danych
    c.execute(f"SELECT id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note FROM rejs WHERE date='{theDay2}' ORDER BY hour")
    saveDataToArray()
    
    #Wyświetl dane
    scr = st.columns([1,1,1,1])
    albatros_tab, biala_mewa_tab, kormoran_tab, ckt_vip_tab = st.tabs(["Albatros", "Biała Mewa", "Kormoran", "CKT VIP"])
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
    tab1, tab2 = st.tabs(["Dodaj rejs", "Edytuj"])
    with tab1:
        st.header("Dodaj rejs :anchor:")
        addCruiseInfo()
        
    with tab2:
        st.header("Edytuj dane")
        editInfo()

if (selected == "Historia"):
    st.markdown("<h1 style=\"background-color: #85C1C1; color: #FFFFFF; border-radius: 10px; font-weight: bold; padding-left: 1rem;\">Historia rejsów<h1>", unsafe_allow_html=True)
    history = showAllData()
    st.dataframe(history)

conn.close()
