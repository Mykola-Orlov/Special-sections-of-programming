import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc
from dash import html

# Функція для генерації даних
def generate_data():
    x = np.linspace(0, 2*np.pi, 100) #Генеруємо 100 рівномірно розподілених значень від 0 до 2π.
    y1 = np.sin(x) #Генеруєvj значення синуса для кожного значення x
    y2 = np.cos(x)
    return x, y1, y2 #Повертає три масиви даних: x, y1 і y2

# Функція для фільтрації даних
def custom_filter(data, filter_type='none'):
    #Якщо вибраний тип фільтра 'none', функція повертає вхідні дані без будь-якої зміни
    if filter_type == 'none': 
        return data
    elif filter_type == 'low_pass':
        # Реалізуйте ваш фільтр, наприклад, низькочастотний фільтр
        filtered_data = np.convolve(data, np.ones(10)/10, mode='same')
        return filtered_data
    elif filter_type == 'high_pass':
        # Реалізуйте ваш фільтр, наприклад, високочастотний фільтр
        filtered_data = data - np.convolve(data, np.ones(10)/10, mode='same')
        return filtered_data
    else:
        return data

# Дані для візуалізації
x, y1, y2 = generate_data()

# Створення графіку
fig = make_subplots(rows=2, cols=1, subplot_titles=['Графік 1', 'Графік 2'])

trace1 = go.Scatter(x=x, y=y1, mode='lines', name='Графік 1')
fig.add_trace(trace1, row=1, col=1)

trace2 = go.Scatter(x=x, y=y2, mode='lines', name='Графік 2')
fig.add_trace(trace2, row=2, col=1)

# Створення layout для Dash
app = dash.Dash(__name__) #Створюється об'єкт Dash для створення веб-додатку

app.layout = html.Div(children=[                          # Описує структуру сторінки веб-додатку
    html.H1(children='Візуалізація та фільтрація даних'), # Додає заголовок рівня 1 на сторінку

    dcc.Dropdown(              #Створює розкриваючий список для вибору типу фільтра. 
        id='filter-dropdown',
        options=[
            {'label': 'Без фільтра', 'value': 'none'},                     
            {'label': 'Низькочастотний фільтр', 'value': 'low_pass'},
            {'label': 'Високочастотний фільтр', 'value': 'high_pass'}
        ],
        value='none',          #Встановлюємо значення за замовчуванням ('none')
        style={'width': '50%'}
    ),

    dcc.Graph(             #Додає графік, ідентифікований як 'graph', з визначеною фігурою
        id='graph',
        figure=fig,
        style={'height': '100vh', 'width': '100vw'}  # Встановлений розмірами на весь екран
    )
])

# Оновлення графіку при виборі нового фільтра
@app.callback(
    dash.dependencies.Output('graph', 'figure'), #Функція повертатиме новий графік для відображення в елементі з ідентифікатором 'graph
    [dash.dependencies.Input('filter-dropdown', 'value')]  #Функція отримує значення, обране випадаючим списком, яке передається як параметр value
)
# Функція, яка оновлює дані графіків на основі обраного фільтра
def update_graph(selected_filter): 
    # Застосовуємо фільтрацію до y1 та y2 за допомогою вибраного фільтра
    filtered_y1 = custom_filter(y1, selected_filter)
    filtered_y2 = custom_filter(y2, selected_filter)

    # Оновлюємо дані графіків з фільтрованими даними
    fig.data[0].y = filtered_y1
    fig.data[1].y = filtered_y2

    return fig

if __name__ == '__main__':
    app.run_server(debug=True) #запускає сервер Dash у режимі вкладки