from ping3 import ping
from datetime import datetime
import time
import re
import art
import math # для округления шага
import matplotlib.pyplot as plt # построение графиков и диаграмм
import pandas as pd 
import openpyxl # для работы с xlsx
# import numpy as np

def greeting(): 
    art.tprint("NETWORK\nPING\nANALIZER", font="small")
    print("by Makar Bolovintsev")     
greeting()

# PING SCANNER
def ping_scanner():

    host = input("Введи хост для анализа сети: ").lower()
    res = re.search(r"^(?:https?:\/\/)?([a-z0-9.-]+\.[a-z]{2,})?(\/[a-zA-Z0-9\D\/]+)$", host)

    print(f"Начинаю сканирование хоста {res.group(1)}")
    print("Нажми Ctrl+C для остановки\n")

    # Переменные
    time_list = []
    ping_list = []
    seconds_list = []
    log_list = []
    losses = 0
    all_packages = 0
    bad_packages = 0
    ping_log = {}
    bad_time = {}
    breaking_connection = {}


    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            seconds = datetime.now().timestamp()
            response_time = ping(res.group(1))

            all_packages += 1

            if response_time is None:
                losses += 1
                print(f"{current_time} ❌ Нет соединения с {res.group(1)}: ({losses}/{all_packages})")
                breaking_connection[current_time] = response_time
            else:
                time_list.append(current_time)
                ping_list.append(response_time)
                seconds_list.append(seconds)

                ping_log[current_time] = response_time

                if len(ping_list) >= 5:
                    average_time = sum(ping_list[-5:])/5

                    if response_time > average_time * 2: # сначала САМОЕ строгое условие
                        print(f"{current_time} ❗КРИТИЧЕСКОЕ ПАДЕНИЕ {res.group(1)}: {response_time:.3f} сек")

                        bad_time[current_time] = response_time
                        bad_packages += 1

                    elif response_time > average_time * 1.3:  # затем более слабое и т.д.
                        percent = ((average_time - response_time) / average_time) * 100
                        print(f"{current_time} 📉 Падение скорости {res.group(1)} на {percent:.0f}%: {response_time:.3f} сек")
                    
                    elif response_time < average_time * 0.7:
                        percent = ((average_time - response_time) / average_time) * 100
                        print(f"{current_time} 📈 Скачок скорости {res.group(1)} на {percent:.0f}%: {response_time:.3f} сек")            
                    
                    else: # если никакое условие не было выполнено, то else
                        print(f"{current_time} ✅ Время ответа {res.group(1)}: {response_time:.3f} сек")
                  
                else:
                    print(f"{current_time} ✅ Время ответа {res.group(1)}: {response_time:.3f} сек")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nПингование остановлено пользователем")
        

# STATISTICS
        print("\n" + "="*40)
        print(f"📊 СТАТИСТИКА ПО {res.group(1).upper()}:")
        print("\n" + "="*40)

        print(f"📅 Начало анализа: {''.join(map(str, time_list[:1]))} | Конец анализа: {''.join(map(str, time_list[-1:]))}")
        print("\n" + "-"*40)

        print(f"📦 Пакеты: {all_packages} | ❌ Потери: {losses}")

        # Отсекаю дату из списка, оствляя время (для диаграммы)
        time_list3f = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S') for date in time_list]
        
        if ping_list:
            print(f"🏆 Лучший: {min(ping_list):.3f} сек")
            print(f"💩 Худший: {max(ping_list):.3f} сек")
            print(f"📊 Средний: {sum(ping_list)/len(ping_list):.3f} сек")

            print("\n" + "-"*40)

            if len(bad_time) >= 1:
                print(f"❗({len(bad_time)}) КРИТИЧЕСКИХ ПАДЕНИЙ:")

                for key, value in bad_time.items():
                    print(f"{key} → {value}")
            else:
                print("✅ Критических падений не было")

            print("\n" + "-"*40)

            if len(breaking_connection) >= 1:  
                print(f"❌ ({len(breaking_connection)}) разрывов соединения:")

                for key, value in breaking_connection.items():
                    print(f"{key} → {value}")
            else:
                print("✅ Разрывов соединений не было")

            print("\n" + "="*40)   


# DIAGRAMM
            def chart():
                
                total_points = all_packages
                max_labels = 15

                if total_points <= max_labels:
                    step = 1
                else:
                    step = math.ceil(total_points / max_labels)

                x = time_list3f[::step]  
                y = ping_list[::step] 

                plt.style.use('ggplot') # Популярные стили: 'ggplot', 'seaborn', 'dark_background', 'bmh'

                plt.plot(x, y, color='red', marker='*', markersize=7, alpha=0.8)
                plt.title(f'Статистика {res.group(1)}')
                plt.xlabel('Время соединения', fontsize=5)
                plt.ylabel('Время ответа')
                plt.show()


            def pie_chart():

                value = [all_packages, bad_packages, losses]
                labels = ["Всего пакетов", "Критические падения", "Разрывы соедиения"] 
                colors = ['green', 'yellow', 'red']           

                # plt.style.use('seaborn-darkgrid')
                plt.pie(value, labels=None, autopct='%1.1f%%', colors=colors, startangle=90) # Убираю подписи, чтобы не мешали
                plt.title(f'Статистика {res.group(1)}')

                # Отедбльная легенда
                plt.legend(labels, title="Легенда", loc="right", bbox_to_anchor=(0.5, -0.1, 0.5, 0.1))

                plt.axis('equal') # чтобы круг не растягивался в овал

                plt.show()


# TABLE
            def export_csv():
                statistics = {'Дата замера': time_list, 'Время отклика': ping_list}

                df = pd.DataFrame(statistics)
                df.to_csv('scanner_stat.csv')
                print('Отчет выгружен в директорию со скриптом')
                print("\n" + "-"*40) 


            def export_xlsx():
                statistics = {'Дата замера': time_list, 'Время отклика': ping_list}

                df = pd.DataFrame(statistics)
                df.to_excel('scanner_stat.xlsx')
                print('Отчет выгружен в директорию со скриптом')                
                print("\n" + "-"*40) 


# MENU
            def action_result():
                print("✔️ Действие с результатом \n")
                print("1. Получить график замеров")
                print("2. Получить груговую диаграмму происшествий")
                print("3. Выгрузить отчет в csv")
                print("4. Выгрузить отчет в xlsx")
                print("5. Вернуться к сервисам \n")

            # CHOICE
            while True:
                action_result()
                print("\n" + "-"*40)
                choice = int(input("Действие: "))
                print("\n" + "-"*40)

                if choice == 1:
                    chart()
                elif choice == 2:
                    pie_chart()
                elif choice == 3:
                    export_csv()
                elif choice == 4:
                    export_xlsx()
                elif choice == 5:
                    print("Выход")
                    print("\n" + "-"*40)

                    break
                else:
                    print("Введи введи верное число по номеру сервиса")  

# /PING SCANNER

# NETWORK SPEED
def network_speed():
    print("Этот сервис еще в работе, но очень скоро появится")

# MENU
def service_menu():
    print("Сервисы")
    print("1. Проверка сетевого соединения с узлом")
    print("2. Ассинхронный тест узла")
    print("3. Выход \n")

print("\n" + "-"*40)

# CHOICE
while True:
    service_menu()
    choice = int(input("Выбор сервиса: "))

    if choice == 1:
        ping_scanner()
    elif choice == 2:
        network_speed()
    elif choice == 3:
        print("Выход")
        break
    else:
        print("Введи введи верное число по номеру сервиса")



