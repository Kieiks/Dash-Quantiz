# Import packages
from dash import Dash, html, dcc, callback, Output, Input, State
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dotenv import load_dotenv
import os

from meli import mercadolivre
from magalu import magalu
from amz import amazon
from amz import remaining_request

# Function to create a count chart with the top 5 categories
def count_chart(df, col_chosen):
    df_chart = df[col_chosen].value_counts().nlargest(5).reset_index()
    df_chart.columns = [col_chosen, 'count']
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_chart[col_chosen],
        x=df_chart['count'],
        orientation='h',
        marker_color='#041E41',
        text=df_chart['count'],
        textfont=dict(size=15)
    ))

    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(tickfont=dict(size=15))

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        bargap=0.3,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin = dict(l=10, r=10, t=10, b=10,pad=15),
    )
    return fig

# Function to create a price chart
def price_chart(df, col_chosen):
    top_5 = df[col_chosen].value_counts().nlargest(5).index
    df_top_5 = df[df[col_chosen].isin(top_5)]
    fig = go.Figure()

    fig.add_trace(go.Box(
        x=df_top_5[col_chosen],
        y=df_top_5['Preco'],
        boxpoints='all',
        pointpos=0,
        jitter=0.5,
        whiskerwidth=0.2,
        marker_size=7,
        line_width=1,
        marker_color='#041E41',
        text=[i for i in df_top_5['Titulo']],
        hovertemplate='<b>%{x}</b><br>%{text}<br><b>Preço</b>: %{y:.2f}<br>'
    ))

    for i in top_5:
        value = df_top_5[df_top_5[col_chosen] == i]['Preco'].median()

        fig.add_annotation(
            x=i,
            y=value,
            text=f'{value:.2f}',
            showarrow=False,
            bgcolor='white',
        )
    
    fig.update_yaxes(showticklabels=False)
    fig.update_xaxes(tickfont=dict(size=15))

    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin = dict(l=10, r=10, t=10, b=10),
    )
    return fig


# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

load_dotenv()
token = os.getenv('token')

def create_header():
    return dmc.Grid([
        dmc.Col([
            html.Div(children='Consulta agregada', className='text-right h2'),
            html.Div(children='Mercado Livre & Amazon & Magalu', className='text-right h4')
        ], span=12)
    ])

def create_search_section():       
    search = dmc.Grid(children=[
        dmc.Stack(
            pos="relative",
            p=5,
            w=500,
            children=[
                dmc.TextInput(
                    label="Termo a ser pesquisado",
                    placeholder="Busca nos sites",
                    icon=DashIconify(icon="material-symbols:search-rounded"),
                    required=True,
                    id="q",
                ),
                dmc.NumberInput(
                    label="Páginas (max 2 páginas)",
                    value=1,
                    step=1,
                    max=2,
                    required=True,
                    icon=DashIconify(icon="radix-icons:lock-closed"),
                    id='paginas'
                ),
                dmc.Button(
                    "CONSULTAR", id="submit-button", variant="outline", fullWidth=True
                ),
            ],
        ),
    ])

    return dmc.Paper(dbc.Card([dbc.CardHeader('Consulta de Produtos'),dbc.CardBody([search])]),radius='md',shadow='md',withBorder=True)

def create_websites():
    checklist = dcc.Checklist(
    [
        {
            "label": [
                html.Img(src="/assets/images/meli.svg", width='150px',style={"padding": 10}),
            ],
            "value": "Meli",
        },
        {
            "label": [
                html.Img(src="/assets/images/magalu.svg", width='150px',style={"padding": 10}),
            ],
            "value": "Magalu",
        },
        {
            "label": [
                html.Img(src="/assets/images/amazon.svg", width='150px',style={"padding": 10}),
                html.H6('(consultas limitadas)')
            ],
            'disabled': not remaining_request(),
            "value": "Amz",
        },
    ],
    value=['Meli','Magalu','Amz'],labelStyle={"display": "flex", "align-items": "center"},id='Checklist',
    )

    return dmc.Paper(dbc.Card([dbc.CardHeader('Escolha os ECommerces'),dbc.CardBody([checklist])],style={'height':'100%'}),radius='md',shadow='md',withBorder=True,style={'height':'100%'})


def create_dropdown():

    dropdown = dmc.Stack([
        dmc.Grid(children='',id='message'),
        dmc.Grid(
            dmc.Select(
                id='marca-dropdown',
                data=[
                    {'label': 'ECommerce', 'value': 'ECommerce'},
                    {'label': 'Marca', 'value': 'Marca'},
                    {'label': 'Seller Name', 'value': 'SellerName'}
                ],
                placeholder="Agregação",
                label='Selecionar variável para agregação'
            )
        )
    ],align='stretch',justify='space-between')

    return dmc.Paper(dbc.Card([dbc.CardHeader('Escolha o tipo de agregação'),dbc.CardBody([dropdown])],style={'height':'100%'}),radius='md',shadow='md',withBorder=True,style={'height':'100%'})

def create_charts():
    return dmc.Group([
        dmc.Paper(dbc.Card([dbc.CardHeader('Top 5 | Contagem de Produtos'),dbc.CardBody([dcc.Graph(figure={}, id='count-chart')])]),radius='md',shadow='md',withBorder=True),
        dmc.Paper(dbc.Card([dbc.CardHeader('Distribuição de Preços'),dbc.CardBody([dcc.Graph(figure={}, id='price-chart')])]),radius='md',shadow='md',withBorder=True),
    ],grow=True)

# Assemble the layout using the component functions

app.layout = dmc.Container(
        [
        create_header(),
        html.Hr(),
        dmc.Grid([
            dmc.Col(create_websites(),span=4),
            dmc.Col(create_search_section(), span=4),
            dmc.Col(create_dropdown(), span=4),
        ]),
        html.Hr(),
        dcc.Store(id='stored-data'),
        create_charts(),
        html.Hr(),
        dmc.Grid(id='aggrid',children=''),
    ], fluid=True)



# Callback to fetch and store data
@callback(
    [Output('stored-data', 'data'),
     Output('message', 'children'),
     Output('marca-dropdown', 'value'),
     Output('aggrid', 'children')],
    Input('submit-button', 'n_clicks'),
    State('q', 'value'),
    State('paginas', 'value'),
    State('Checklist', 'value'),
    prevent_initial_call=True,
)
def fetch_data(n_clicks, q, paginas, Checklist):
    # Retrieve data
    if 'Meli' in Checklist:
        df_meli = mercadolivre(q, paginas)
    else:
        df_meli = pd.DataFrame()

    if 'Magalu' in Checklist:
        df_magalu = magalu(q, paginas)
    else:
        df_magalu = pd.DataFrame()
    
    if 'Amz' in Checklist:
        df_amz = amazon(q, paginas)
    else:
        df_amz = pd.DataFrame()


    df = pd.concat([df_meli,df_amz,df_magalu])


    df.fillna(0,inplace=True)
    
    df['Link_Icon'] = '🔗'

    retorno = dmc.Alert(
        children = f'Retorno para a consulta {q} com {paginas} páginas.',
        title = 'Coleta bem sucedida!',
        icon = DashIconify(icon="codicon:flame"),
        color='green',
        style={'height':'100%'},
    )

    grid = AgGrid(
            id='datatable',
            rowData=df.to_dict('records'),
            columnDefs=[
                {'headerName': 'Link', 'field': 'Link_Icon', 'cellRenderer': 'Link'},
                {'headerName': 'ECommerce', 'field': 'ECommerce', 'sortable': True, 'filter': True},
                {'headerName': 'Titulo', 'field': 'Titulo', 'sortable': True, 'filter': True},
                {'headerName': 'Marca', 'field': 'Marca', 'sortable': True, 'filter': True},
                {'headerName': 'SellerName', 'field': 'SellerName', 'sortable': True, 'filter': True},
                {'headerName': 'Preco', 'field': 'Preco', 'sortable': True, 'filter': True},
                # {'headerName': 'Quantidade', 'field': 'Quantidade', 'sortable': True, 'filter': True}
            ],
            columnSize="autoSize",
            dashGridOptions={'pagination': True},
        ),

    return df.to_dict('records'), retorno, 'ECommerce', grid

# Callback to generate the count chart and price chart
@callback(
    [Output('count-chart', 'figure'),
     Output('price-chart', 'figure')],
    Input('marca-dropdown', 'value'),
    State('stored-data', 'data'),
    prevent_initial_call=True,
)
def update_chart(marca, data):
    # Convert stored data back to DataFrame
    df = pd.DataFrame(data)
    # Create and return the count chart and price chart
    return count_chart(df, marca), price_chart(df, marca)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
