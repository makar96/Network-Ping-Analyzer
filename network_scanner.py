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


class PingAnalyzer:
    def __init__(self):

        # Атрибуты основного хоста
        self.time_list = []
        self.ping_list = []
        self.seconds_list = []
        self.ping_log = {}
        self.bad_time = {}
        self.log_list = []
        self.losses = 0
        self.all_packages = 0
        self.bad_packages = 0
        self.breaking_connection = {}
        self.host = None

        # Атрибуты для контрольного хоста
        self.control_host = "8.8.8.8"  # Google DNS
        self.control_breaking_connection = {}
        self.control_ping_list = []


    # ANALYSE CONTROL HOST

    # def monitor_network(self):

    #     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     seconds = datetime.now().timestamp()
    #     response_time = ping(self.res.group(1))

    #     try:
    #         while True:
    #             response_control = ping(self.control_host)

    #         if response_control is None:
    #             self.breaking_connection[current_time] = response_time    
        

    # def greeting(self): 
    #     art.tprint("NETWORK\nPING\nANALIZER", font="small")
    #     print("by Makar Bolovintsev")       


    # PING SCANNER
    def ping_scanner(self):

        self.host = input("Введи хост для анализа сети: ").lower()
        self.res = re.search(r"^(?:https?:\/\/)?([a-z0-9.-]+\.[a-z]{2,})?(\/[a-zA-Z0-9\D\/]+)$", self.host)

        if not self.res:
            print("\nОшибка: неверный формат хоста")
            return  
        
        print(f"Начинаю сканирование хоста {self.res.group(1)}")
        print("Нажми Ctrl+C для остановки\n")

        try:
            while True:

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                seconds = datetime.now().timestamp()
                response_time = ping(self.res.group(1))

                self.all_packages += 1

                if response_time is None:
                    self.losses += 1
                    print(f"{current_time} ❌ Нет соединения с {self.res.group(1)}: ({self.losses}/{self.all_packages})")
                    self.breaking_connection[current_time] = response_time
                else:
                    self.time_list.append(current_time)
                    self.ping_list.append(response_time)
                    self.seconds_list.append(seconds)

                    self.ping_log[current_time] = response_time

                    if len(self.ping_list) >= 10:
                        average_time = sum(self.ping_list[-10:])/10

                        if response_time > average_time * 2: # сначала САМОЕ строгое условие
                            print(f"{current_time} ❗КРИТИЧЕСКОЕ ПАДЕНИЕ {self.res.group(1)}: {response_time:.4f} сек")

                            self.bad_time[current_time] = response_time
                            self.bad_packages += 1

                        elif response_time > average_time * 1.3:  # затем более слабое и т.д.
                            percent = ((average_time - response_time) / average_time) * 100
                            print(f"{current_time} 📉 Падение скорости {self.res.group(1)} на {percent:.0f}%: {response_time:.4f} сек")
                        
                        elif response_time < average_time * 0.7:
                            percent = ((average_time - response_time) / average_time) * 100
                            print(f"{current_time} 📈 Скачок скорости {self.res.group(1)} на {percent:.0f}%: {response_time:.4f} сек")            
                        
                        else: # если никакое условие не было выполнено, то else
                            print(f"{current_time} ✅ Время ответа {self.res.group(1)}: {response_time:.4f} сек")
                    
                    else:
                        print(f"{current_time} ✅ Время ответа {self.res.group(1)}: {response_time:.4f} сек")

                time.sleep(2)

        except KeyboardInterrupt:
            print("\n\nПингование остановлено пользователем")


    # STATISTICS
            print("\n" + "="*40)
            print(f"📊 СТАТИСТИКА ПО {self.res.group(1).upper()}:")
            print("\n" + "="*40)

            print(f"📅 Начало анализа: {''.join(map(str, self.time_list[:1]))} | Конец анализа: {''.join(map(str, self.time_list[-1:]))}")
            print("\n" + "-"*40)

            print(f"📦 Пакеты: {self.all_packages} | ❌ Потери: {self.losses}")

            
            if self.ping_list:
                print(f"🏆 Лучший: {min(self.ping_list):.3f} сек")
                print(f"💩 Худший: {max(self.ping_list):.3f} сек")
                print(f"📊 Средний: {sum(self.ping_list)/len(self.ping_list):.3f} сек")

                print("\n" + "-"*40)

                if len(self.bad_time) >= 1:
                    print(f"❗({len(self.bad_time)}) КРИТИЧЕСКИХ ПАДЕНИЙ:")

                    for key, value in self.bad_time.items():
                        print(f"{key} → {value}")
                else:
                    print("✅ Критических падений не было")

                print("\n" + "-"*40)

                if len(self.breaking_connection) >= 1:  
                    print(f"❌ ({len(self.breaking_connection)}) разрывов соединения:")

                    for key, value in self.breaking_connection.items():
                        print(f"{key} → {value}")
                else:
                    print("✅ Разрывов соединений не было")

                print("\n" + "="*40)  


                # MENU
                def action_result():
                    print("✔️ Действие с результатом \n")
                    print("1. Получить график замеров")
                    print("2. Получить груговую диаграмму происшествий")
                    print("3. Выгрузить отчет в csv")
                    print("4. Выгрузить отчет в xlsx")
                    print("5. Вернуться к сервисам \n")

                while True:
                    action_result()
                    print("\n" + "-"*40)

                    try:
                        choice = int(input("Действие: "))
                    except ValueError:
                        print("Введи корректное число")
                        continue
                    
                    print("\n" + "-"*40)

                    if choice == 1:
                        self.chart()
                    elif choice == 2:
                        self.pie_chart()
                    elif choice == 3:
                        self.export_csv()
                    elif choice == 4:
                        self.export_xlsx()
                    elif choice == 5:
                        print("Выход")
                        print("\n" + "-"*40)

                        break
                    else:
                        print("Введи введи верное число по номеру сервиса")            

     # /PING SCANNER  
    
    # DIAGRAMM
    def chart(self):

        if not self.ping_list:
            print("Нет данных для построения графика")
            return
        
        total_points = self.all_packages
        max_labels = 15

        if total_points <= max_labels:
            step = 1
        else:
            step = math.ceil(total_points / max_labels)
        
        # Отсекаю дату из списка, оствляя время (для диаграммы)
        time_list3f = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S') for date in self.time_list]

        x = time_list3f[::step]  
        y = self.ping_list[::step] 

        plt.style.use('ggplot') # Популярные стили: 'ggplot', 'seaborn', 'dark_background', 'bmh'

        plt.plot(x, y, color='red', marker='*', markersize=7, alpha=0.8)
        plt.title(f'Статистика {self.res.group(1)}')
        plt.xlabel('Время соединения', fontsize=5)
        plt.ylabel('Время ответа')
        plt.show()


    def pie_chart(self):

        value = [self.all_packages, self.bad_packages, self.losses]
        labels = ["Всего пакетов", "Критические падения", "Разрывы соединения"] 
        colors = ['green', 'yellow', 'red']           

        # plt.style.use('seaborn-darkgrid')
        plt.pie(value, labels=None, autopct='%1.1f%%', colors=colors, startangle=90) # Убираю подписи, чтобы не мешали
        plt.title(f'Статистика {self.res.group(1)}')

        # Отедбльная легенда
        plt.legend(labels, title="Легенда", loc="right", bbox_to_anchor=(0.5, -0.1, 0.5, 0.1))

        plt.axis('equal') # чтобы круг не растягивался в овал

        plt.show()


    # TABLE
    def export_csv(self):
        statistics = {'Дата замера': self.time_list, 'Время отклика': self.ping_list}

        df = pd.DataFrame(statistics)
        df.to_csv('scanner_stat.csv')
        print('Отчет выгружен в директорию со скриптом')
        print("\n" + "-"*40) 


    def export_xlsx(self):
        statistics = {'Дата замера': self.time_list, 'Время отклика': self.ping_list}

        df = pd.DataFrame(statistics)
        df.to_excel('scanner_stat.xlsx')
        print('Отчет выгружен в директорию со скриптом')                
        print("\n" + "-"*40) 


    # NETWORK SPEED
    def network_speed(self):
        print("Этот сервис еще в работе, но очень скоро появится")

    # MENU
    def service_menu(self):
        print("Сервисы")
        print("1. Проверка сетевого соединения с узлом")
        print("2. Ассинхронный тест узла")
        print("3. Выход \n")

    # MENU
    def run(self):
        self.greeting()        

        while True:
            print("\n" + "-"*40)
            self.service_menu()
            try:
                choice = int(input("Выбор сервиса: "))
            except ValueError:
                print("Введи корректное число")
                continue

            if choice == 1:
                self.ping_scanner()
            elif choice == 2:
                self.network_speed()
            elif choice == 3:
                print("Выход")
                break
            else:
                print("Введи введи верное число по номеру сервиса")


if __name__ == "__main__":
    analyzer = PingAnalyzer()
    analyzer.run()