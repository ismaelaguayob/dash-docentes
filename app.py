import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

external_scripts = [
    {'src': 'https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4'},
]

external_stylesheets = [
    'https://cdn.jsdelivr.net/npm/daisyui@5',
    "https://cdn.jsdelivr.net/npm/daisyui@5/themes.css"
]

# Configuración del tema DaisyUI
tema = "garden"

# Incorporate data
df = pd.read_csv('./data/dash_docentes_2023.csv') # Asegúrate que esta ruta sea correcta

# Función para crear el dropdown reutilizable (MODIFICADA)
def crear_dropdown_variable_x(dropdown_id, titulo="Selecciona variable X"):
    opciones_x = [
        {'label': 'Dependencia', 'value': 'dependencia'},
        {'label': 'Nivel', 'value': 'nivel'},
        {'label': 'Género', 'value': 'sexo'},
        {'label': 'Ruralidad', 'value': 'rural'},
        {'label': 'Tramo de Edad', 'value': 'grupo_edad'}
    ]
    
    return html.Div([
        html.H3(
            titulo,
            className='text-lg font-bold mb-3 text-base-content'
        ),
        html.Div([ # Este es '.dropdown-wrapper w-full'
            dcc.Dropdown(
                id=dropdown_id,
                options=opciones_x,
                value='nivel',
                clearable=False,
                className='w-full',
                style={
                    'backgroundColor': 'transparent',
                    'border': 'none',
                    'fontFamily': 'inherit'
                }
            )
        ], className='dropdown-wrapper w-full', style={'position': 'relative', 'z-index': 50}) # <--- AÑADIDO style para z-index local
    ], className='form-control w-full')

# Función para procesar y formatear los datos según la variable seleccionada
def procesar_datos_para_grafico(df, variable_x):
    df_procesado = df.copy()
    if variable_x == 'sexo':
        df_procesado['sexo_label'] = df_procesado['sexo'].map({1: 'Masculino', 2: 'Femenino'})
        return df_procesado, 'sexo_label'
    elif variable_x == 'rural':
        df_procesado['rural_label'] = df_procesado['rural'].map({0: 'Urbano', 1: 'Rural'})
        return df_procesado, 'rural_label'
    else:
        return df_procesado, variable_x

# Initialize the app
app = Dash(__name__, external_scripts=external_scripts, external_stylesheets=external_stylesheets)

server = app.server

# CSS personalizado (sin cambios, ya tienes el z-index alto para Select-menu-outer)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .custom-segmented-radio { display: flex !important; width: 100%; }
            .custom-segmented-radio > label { flex: 1; margin: 0; display: flex !important; align-items: center !important; justify-content: center !important; min-height: 3.5rem; font-weight: 600; transition: all 0.2s ease; position: relative; }
            .custom-segmented-radio > label:hover { transform: scale(1.02); }
            .custom-segmented-radio > label:active { transform: scale(0.98); }
            .custom-segmented-radio input[type="radio"]:checked + label { background: hsl(var(--p)) !important; color: hsl(var(--pc)) !important; border-color: hsl(var(--p)) !important; }
            .dropdown-wrapper .Select-control { background-color: hsl(var(--b1)) !important; border: 2px solid hsl(var(--b3)) !important; border-radius: 0.5rem !important; padding: 0.5rem !important; min-height: 3rem !important; font-size: 1rem !important; transition: all 0.2s ease !important; }
            .dropdown-wrapper .Select-control:hover { border-color: hsl(var(--p)) !important; transform: translateY(-1px) !important; box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important; }
            .dropdown-wrapper .Select-control.is-focused { border-color: hsl(var(--p)) !important; box-shadow: 0 0 0 3px hsl(var(--p) / 0.2) !important; }
            .dropdown-wrapper .Select-placeholder { color: hsl(var(--bc) / 0.6) !important; }
            .dropdown-wrapper .Select-value-label { color: hsl(var(--bc)) !important; font-weight: 500 !important; }
            .dropdown-wrapper .Select-arrow { border-color: hsl(var(--bc)) transparent transparent !important; }
            .dropdown-wrapper .Select-menu-outer { background-color: hsl(var(--b1)) !important; border: 2px solid hsl(var(--b3)) !important; border-radius: 0.5rem !important; box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important; z-index: 1000 !important; }
            .dropdown-wrapper .Select-option { background-color: transparent !important; color: hsl(var(--bc)) !important; padding: 0.75rem !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
            .dropdown-wrapper .Select-option:hover { background-color: hsl(var(--p) / 0.1) !important; color: hsl(var(--p)) !important; }
            .dropdown-wrapper .Select-option.is-selected { background-color: hsl(var(--p)) !important; color: hsl(var(--pc)) !important; }
        </style>
    </head>
    <body> {%app_entry%} <footer> {%config%} {%scripts%} {%renderer%} </footer> </body>
</html>
'''

title = 'Evaluación Docente 2023 - Dashboard'
intro = '''
Una aplicación para visualizar los resultados de la evaluación docente de 2023, tanto el puntaje del portafolio como la prueba de conocimientos (ECEP).
Interactúa con los controles para ver los resultados de la evaluación docente.
'''

# App layout (MODIFICADO)
app.layout = html.Div([
    html.Div([ # Contenedor principal de la página
        html.H1(
            title,
            className='text-4xl font-bold text-center mb-8 text-primary'
        ),
        html.P(
            intro,
            className='text-center mb-8 text-base-content max-w-2xl mx-auto leading-relaxed'
        ),
        
        # Contenedor Flex para controles y gráfico
        html.Div([
            # Columna de Controles (Item 1 del Flex)
            html.Div([
                # Radio buttons para tipo de evaluación
                html.Div([
                    html.H3(
                        'Selecciona el tipo de evaluación:',
                        className='text-xl font-bold text-center mb-6 text-base-content'
                    ),
                    html.Div([
                        dcc.RadioItems(
                            options=[
                                {'label': 'Portafolio', 'value': 'pj_pf'},
                                {'label': 'ECEP', 'value': 'pj_ecep'}
                            ],
                            value='pj_pf',
                            id='controls-and-radio-item',
                            className='custom-segmented-radio',
                            inputClassName='hidden peer',
                            labelClassName='join-item btn btn-outline peer-checked:btn-primary peer-checked:text-primary-content flex-1 h-14 text-base font-semibold transition-all duration-200 hover:scale-105 active:scale-95 flex items-center justify-center'
                        )
                    ], className='join w-full max-w-sm mx-auto shadow-lg')
                ], className='mb-6'), # Mantenemos mb-6 para espaciado interno
                
                # Dropdown para variable X
                html.Div([
                    crear_dropdown_variable_x(
                        dropdown_id='selector-variable-x',
                        titulo='Elige una categoría!:'
                    )
                ], className='w-full max-w-sm mx-auto')
                
            ], 
            className='card bg-gradient-to-br from-base-100 to-base-200 shadow-2xl p-8 border-2 border-base-300 rounded-2xl backdrop-blur-sm w-full md:w-1/3 lg:w-1/4', # Clases para la tarjeta de controles
            style={'position': 'relative', 'z-index': 1050}), # <--- AUMENTADO z-index y asegurado position relative
            
            # Columna del Gráfico (Item 2 del Flex)
            html.Div([
                dcc.Graph(
                    id='gráfico-principal', 
                    figure={}, 
                    style={'height': '100%', 'min-height': '400px'}, # Asegura que el gráfico tenga altura
                    config={'displayModeBar': True} # Asegura que la modebar esté visible para pruebas
                )
            ], className='card bg-base-100 shadow-xl p-6 w-full md:w-2/3 lg:w-3/4 flex-grow') # Clases para la tarjeta del gráfico

        ], className='flex flex-col md:flex-row gap-6'), # <--- CONTENEDOR FLEX para organizar controles y gráfico

    ], className='min-h-screen bg-base-200 p-8')
], **{'data-theme': tema})

# Callback (sin cambios)
@callback(
    Output(component_id='gráfico-principal', component_property='figure'),
    [Input(component_id='controls-and-radio-item', component_property='value'),
     Input(component_id='selector-variable-x', component_property='value')]
)
def update_graph(col_chosen, variable_x):
    df_procesado, x_column = procesar_datos_para_grafico(df, variable_x)
    fig = px.histogram(df_procesado, x=x_column, y=col_chosen, histfunc='avg')
    nombres_variables = {
        'dependencia': 'Dependencia', 'nivel': 'Nivel', 'sexo': 'Género',
        'rural': 'Ruralidad', 'grupo_edad': 'Tramo de Edad'
    }
    tipo_evaluacion = 'Portafolio' if col_chosen == 'pj_pf' else 'ECEP'
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color='#1f2937',
        title=f'Evaluación Docente - {tipo_evaluacion} por {nombres_variables[variable_x]}',
        title_font_size=20, title_x=0.5,
        xaxis_title=nombres_variables[variable_x],
        yaxis_title=f'Promedio {tipo_evaluacion}',
        font_family='inherit'
    )
    fig.update_traces(marker_color='#570df8')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=False)