import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import iirfilter, lfilter

class HarmonicNoisePlotter:
    def __init__(self, root):
        # Ініціалізація головного вікна
        self.root = root
        self.root.title("Harmonic Noise Plotter")

        # Змінні, які використовуються для збереження значень параметрів
        self.amplitude_var = tk.DoubleVar(value=1.0)  # Змінна для амплітуди
        self.frequency_var = tk.DoubleVar(value=1.0)  # Змінна для частоти
        self.phase_var = tk.DoubleVar(value=0.0)  # Змінна для фази
        self.noise_amplitude_var = tk.DoubleVar(value=0.2)  # Змінна для амплітуди шуму
        self.noise_covariance_var = tk.DoubleVar(value=0.1)  # Змінна для коваріації шуму
        self.show_noise_var = tk.BooleanVar(value=True)  # Змінна для відображення шуму
        self.filter_cutoff_var = tk.DoubleVar(value=0.2)  # Змінна для частоти фільтра
        self.filter_order_var = tk.IntVar(value=4)  # Змінна для порядку фільтра
        self.use_filter_var = tk.BooleanVar(value=False)  # Змінна для використання фільтра

        # Створення елементів інтерфейсу
        self.create_widgets()
        self.plot()

    def create_widgets(self):
        ttk.Label(self.root, text="Амплітуда").grid(row=0, column=0)  # Повзунок для амплітуди
        ttk.Label(self.root, text="Частота").grid(row=1, column=0)  # Повзунок для частоти
        ttk.Label(self.root, text="Фаза").grid(row=2, column=0)  # Повзунок для фази
        ttk.Label(self.root, text="Амплітуда шуму").grid(row=3, column=0)  # Повзунок для амплітуди шуму
        ttk.Label(self.root, text="Коваріація шуму").grid(row=4, column=0)  # Повзунок для коваріації шуму
        ttk.Label(self.root, text="Показати шум").grid(row=5, column=0)  # Повзунок для відображення шуму


        #from - min знач., to - max знач., variable- Змінна, в яку зберігається вибране значення, orient - Орієнтація шкали (горизонтальна).
        #length - Довжина шкали (200 пікселів), command - Функція, яка викликається при зміні значення шкали 
        # Створення шкали для налаштування амплітуди
        amplitude_scale = ttk.Scale(self.root, from_=0.1, to=2.0, variable=self.amplitude_var, orient=tk.HORIZONTAL,
                            length=200, command=lambda event=None: self.plot())
        # Розміщення шкали на інтерфейсі в графічному вікні (рядок 0, колонка 1)
        amplitude_scale.grid(row=0, column=1)

        frequency_scale = ttk.Scale(self.root, from_=0.1, to=5.0, variable=self.frequency_var, orient=tk.HORIZONTAL,
                                    length=200, command=lambda event=None: self.plot())
        frequency_scale.grid(row=1, column=1)

        phase_scale = ttk.Scale(self.root, from_=-np.pi, to=np.pi, variable=self.phase_var, orient=tk.HORIZONTAL,
                                length=200, command=lambda event=None: self.plot())
        phase_scale.grid(row=2, column=1)

        noise_amplitude_scale = ttk.Scale(self.root, from_=0.0, to=1.0, variable=self.noise_amplitude_var,
                                          orient=tk.HORIZONTAL, length=200, command=lambda event=None: self.plot())
        noise_amplitude_scale.grid(row=3, column=1)

        noise_covariance_scale = ttk.Scale(self.root, from_=0.0, to=1.0, variable=self.noise_covariance_var,
                                           orient=tk.HORIZONTAL, length=200, command=lambda event=None: self.plot())
        noise_covariance_scale.grid(row=4, column=1)

        ttk.Checkbutton(self.root, variable=self.show_noise_var,
                        command=self.plot, onvalue=True, offvalue=False).grid(row=5, column=1)

        # Створення фігури та вісей для графіку
        self.figure, self.ax = plt.subplots()
        # Створення віджета для відображення графіку в Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        # Отримання віджета Tkinter для розміщення на інтерфейсі
        self.canvas_widget = self.canvas.get_tk_widget()
        # Розміщення віджета на інтерфейсі в графічному вікні (рядок 0, колонка 2, rowspan=6 - займає 6 рядків)
        self.canvas_widget.grid(row=0, column=2, rowspan=6)

        # Створення мітки для введення частоти фільтра
        ttk.Label(self.root, text="Частота фільтра").grid(row=6, column=0)
        # Створення шкали для вибору частоти фільтра
        ttk.Scale(self.root, from_=0.1, to=10.0, variable=self.filter_cutoff_var, orient=tk.HORIZONTAL,
                  length=200, command=lambda event=None: self.plot()).grid(row=6, column=1)

        ttk.Label(self.root, text="Порядок фільтра").grid(row=7, column=0)
        ttk.Scale(self.root, from_=1, to=10, variable=self.filter_order_var, orient=tk.HORIZONTAL,
                  length=200, command=lambda event=None: self.plot()).grid(row=7, column=1)

        ttk.Checkbutton(self.root, text="Використовувати фільтр", variable=self.use_filter_var,
                        command=self.plot).grid(row=8, column=0, columnspan=2)

       # Створення кнопки для закриття графіку
        ttk.Button(self.root, text="Закрити графік", command=self.close_plot).grid(row=8, column=2) #При натисканні викликає метод self.close_plot()

         # Створення кнопки для скидання параметрів
        reset_button = ttk.Button(self.root, text="Reset", command=self.reset)
        reset_button.grid(row=8, column=1, columnspan=2)
        
        #Розміри вікна
        self.root.geometry("1000x600")
        

    def plot(self):
        # Генерація часового вектора
        t = np.linspace(0, 10, 1000)
        # Створення гармонійного сигналу без шуму
        signal_without_noise = self.amplitude_var.get() * np.sin(
            2 * np.pi * self.frequency_var.get() * t + self.phase_var.get())
        
        # Додавання шуму до сигналу в залежності від параметрів
        if self.show_noise_var.get():
            # Генерація випадкового шуму з нормальним розподілом
            noise = np.random.normal(0, np.sqrt(self.noise_covariance_var.get()), len(t))
            # Додавання шуму до сигналу без шуму
            signal_with_noise = signal_without_noise + self.noise_amplitude_var.get() * noise
        else:
            # Якщо опція не включена, сигнал з шумом буде ідентичним сигналу без шуму
            signal_with_noise = signal_without_noise
        
        # Використання фільтрації, якщо опція включена
        if self.use_filter_var.get():
            # Отримання параметрів фільтрації
            filter_order = self.filter_order_var.get()
            filter_cutoff = min(self.filter_cutoff_var.get(), 0.5 * self.frequency_var.get())
            # Встановлення частоти дискретизації для фільтрації
            fs = 10 * self.frequency_var.get()  # Використовуємо множник для забезпечення широкого діапазону частот
            # Застосування IIR-фільтра
            b, a = iirfilter(filter_order, filter_cutoff, fs=fs, btype='low', analog=False, ftype='butter')
            filtered_signal = lfilter(b, a, signal_with_noise)
            
            # Очищення візуалізації та відображення графіків
            self.ax.clear()
            self.ax.plot(t, signal_with_noise, label="Signal with Noise")
            self.ax.plot(t, signal_without_noise, label="Original Signal", linestyle='--')
            self.ax.plot(t, filtered_signal, label="Filtered Signal", linestyle='-.')
            self.ax.legend()
            self.ax.set_title("Harmonic Signal with Noise and Filtered Signal")
            self.canvas.draw()
        else:
            # Очищення візуалізації та відображення графіків без фільтрації
            self.ax.clear()
            self.ax.plot(t, signal_with_noise, label="Signal with Noise")
            self.ax.plot(t, signal_without_noise, label="Original Signal", linestyle='--')
            self.ax.legend()
            self.ax.set_title("Harmonic Signal with Noise")
            self.canvas.draw()

    def reset(self):
        # Скидання значень змінних на їхні дефолтні значення
        self.amplitude_var.set(1.0)
        self.frequency_var.set(1.0)
        self.phase_var.set(0.0)
        self.noise_amplitude_var.set(0.2)
        self.noise_covariance_var.set(0.1)
        self.show_noise_var.set(True)
        self.use_filter_var.set(False)
        # Оновлення графіку з новими параметрами
        self.plot()

    def close_plot(self):
        # Завершення роботи програми та закриття графіку
        self.root.quit()
        plt.close()

if __name__ == "__main__":
    # Створення головного вікна програми та запуск коду
    root = tk.Tk()
    app = HarmonicNoisePlotter(root)
    root.mainloop()