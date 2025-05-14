from dash import Dash, html, dcc, callback, Output, Input, State, MATCH
import pandas as pd
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_ag_grid import AgGrid
from dash_iconify import DashIconify
import dash

from meli_2025 import mercadolivre
from magalu import magalu
from amz import amazon
from amz import remaining_request
import suporte
from mongo import append_to_mongo

dash._dash_renderer._set_react_version("18.2.0")

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",
        "https://cdn.jsdelivr.net/npm/@mantine/core@latest/dist/mantine.css",
    ],
)

server = app.server

header = dmc.Stack(
    [
        dmc.Title(children="Consulta agregada", order=1),
        dmc.Text(children="Mercado Livre & Amazon & Magalu", size="lg"),
    ]
)

websites = dmc.Paper(
    dbc.Card(
        [
            dbc.CardHeader("Escolha os ECommerces"),
            dbc.CardBody(
                [
                    dcc.Checklist(
                        [
                            {
                                "label": [
                                    html.Img(
                                        src="/assets/images/meli.svg",
                                        width="150px",
                                        style={"padding": 10},
                                    ),
                                ],
                                "value": "Meli",
                            },
                            {
                                "label": [
                                    html.Img(
                                        src="/assets/images/magalu.svg",
                                        width="150px",
                                        style={"padding": 10},
                                    ),
                                ],
                                "value": "Magalu",
                            },
                            {
                                "label": [
                                    html.Img(
                                        src="/assets/images/amazon.svg",
                                        width="150px",
                                        style={"padding": 10},
                                    ),
                                    html.H6("(consultas limitadas)"),
                                ],
                                "disabled": not remaining_request(),
                                "value": "Amz",
                            },
                        ],
                        value=["Meli", "Magalu", "Amz"],
                        labelStyle={"display": "flex", "align-items": "center"},
                        id="Checklist",
                    )
                ]
            )
        ],
        style={"height": "100%"},
    ),
    radius="md",
    shadow="md",
    withBorder=True,
    style={"height": "100%"},
)

search = dmc.Paper(
    dbc.Card(
        [
            dbc.CardHeader("Consulta de Produtos"), 
            dbc.CardBody(
                dmc.Grid(
                    children=[
                        dmc.Stack(
                            pos="relative",
                            p=5,
                            w=500,
                            children=[
                                dmc.TextInput(
                                    label="Termo a ser pesquisado",
                                    placeholder="Busca nos sites",
                                    leftSection=DashIconify(icon="material-symbols:search-rounded"),
                                    required=True,
                                    id="q",
                                ),
                                dmc.NumberInput(
                                    label="Páginas (max 2 páginas)",
                                    value=1,
                                    step=1,
                                    max=2,
                                    required=True,
                                    leftSection=DashIconify(icon="radix-icons:lock-closed"),
                                    id="paginas",
                                ),
                                dmc.Button(
                                    "CONSULTAR",
                                    id="submit-button",
                                    variant="outline",
                                    fullWidth=True,
                                ),
                            ],
                        ),
                    ]
                )

            )
            ]
            ),
    radius="md",
    shadow="md",
    withBorder=True,
)

def filters(df,clicks):

    tags = suporte.filtro_texto(df,'Titulo')
    min = df['Preco'].min()
    max = df['Preco'].max()
    q1 = df['Preco'].quantile(0.25)
    q2 = df['Preco'].quantile(0.5)
    q3 = df['Preco'].quantile(0.75)
    marks = {
        min: 'Min',
        q1: 'Q1',
        q2: 'Q2',
        q3: 'Q3',
        max: 'Max',
    }

    tags_input = dmc.TagsInput(
        label="Filtrar por texto",
        placeholder="Selecione ou digite uma palavra",
        id={
            'type': 'tags-input',
            'index': clicks
        },
        data=[x[0] for x in tags],
        mb=10,
    )

    agregacao = dmc.Select(
        id={
            'type': 'agregacao',
            'index': clicks
        },
        data=[
            {"label": "ECommerce", "value": "ECommerce"},
            {"label": "Marca", "value": "Marca"},
            {"label": "Seller Name", "value": "SellerName"},
        ],
        value="ECommerce",
        placeholder="Agregação",
        label="Selecionar variável para agregação",
    )

    price_slider = dcc.RangeSlider(
        min=min,
        max=max,
        vertical=True,
        verticalHeight=180,
        id={
            'type': 'price-slider',
            'index': clicks
        },
        tooltip={"placement": "left", "always_visible": True},
        marks=marks
    )
    
    return dmc.Paper(
        dbc.Card(
            [
                dbc.CardHeader("Escolha o tipo de agregação"),
                dbc.CardBody(
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                [
                                    tags_input,
                                    agregacao
                                ],span=7
                            ),
                            dmc.GridCol(
                                [
                                    dmc.Text('Selecionar faixa de preços', fw=500, size='sm'),
                                    price_slider
                                ],
                                span=4,offset=1
                            )
                        ]
                    )
                )
            ],
            style={"height": "100%"},
        ),
        radius="md",
        shadow="md",
        withBorder=True,
        style={"height": "100%"},
    )

def count_chart_card(df,clicks):
    return dmc.Paper(
        dbc.Card(
            [
                dbc.CardHeader("Top 5 | Contagem de Produtos"),
                dbc.CardBody(
                    dcc.Graph(
                        figure=suporte.count_chart(df, 'ECommerce'),
                        id={
                            'type': 'count-chart',
                            'index': clicks
                        },
                    )
                ),
            ]
        ),
        radius="md",
        shadow="md",
        withBorder=True,
    )

def price_chart_card(df,clicks):
    return dmc.Paper(
        dbc.Card(
            [
                dbc.CardHeader("Distribuição de Preços"),
                dbc.CardBody(
                    dcc.Graph(
                        figure=suporte.price_chart(df, 'ECommerce'),
                        id={
                            'type': 'price-chart',
                            'index': clicks
                        },
                    )
                ),
            ]
        ),
        radius="md",
        shadow="md",
        withBorder=True,
    )

def table_card(data,clicks):
    return AgGrid(
        id={
            'type': 'table',
            'index': clicks
        },
        rowData=data,
        columnDefs=[
            {"headerName": "Link", "field": "Link_Icon", "cellRenderer": "Link"},
            {
                "headerName": "ECommerce",
                "field": "ECommerce",
                "sortable": True,
                "filter": True,
            },
            {
                "headerName": "Titulo",
                "field": "Titulo",
                "sortable": True,
                "filter": True,
            },
            {
                "headerName": "Marca",
                "field": "Marca",
                "sortable": True,
                "filter": True,
            },
            {
                "headerName": "SellerName",
                "field": "SellerName",
                "sortable": True,
                "filter": True,
            },
            {
                "headerName": "Preco",
                "field": "Preco",
                "sortable": True,
                "filter": True,
            },
        ],
        columnSize="autoSize",
        dashGridOptions={"pagination": True},
    )

app.layout = dmc.MantineProvider(dmc.Container(
    [
        header,
        html.Hr(),
        dmc.Grid(
            [
                dmc.GridCol(websites, span=4),
                dmc.GridCol(search, span=4),
                dmc.GridCol(html.Div(id='filters'), span=4)
            ]
        ),
        html.Hr(),
        dcc.Store(id="stored-data"),
        dmc.Grid(
            [
                dmc.GridCol(html.Div(id='count-chart-card'),span=6),
                dmc.GridCol(html.Div(id='price-chart-card'),span=6),
            ]
        ),
        html.Hr(),
        html.Div(id='table-card')
    ],
    fluid=True,
))

@callback(
    Output("stored-data", "data"),
    Input("submit-button", "n_clicks"),
    State("q", "value"),
    State("paginas", "value"),
    State("Checklist", "value"),
    prevent_initial_call=True,
)
def fetch_data(n_clicks, q, paginas, Checklist):
    # Retrieve data

    if "Meli" in Checklist:
        df_meli = mercadolivre(q, paginas)
    else:
        df_meli = pd.DataFrame()
    if "Magalu" in Checklist:
        df_magalu = magalu(q, paginas)
    else:
        df_magalu = pd.DataFrame()
    if "Amz" in Checklist:
        df_amz = amazon(q, paginas)
    else:
        df_amz = pd.DataFrame()

    df = pd.concat([df_meli, df_amz, df_magalu])

    df['Preco'] = pd.to_numeric(df['Preco'], errors='coerce')
    
    # Optionally, drop rows where 'Preco' is NaN
    df = df.dropna(subset=['Preco'])

    df.fillna(0, inplace=True)
    df["Timestamp"] = pd.Timestamp.now()

    append_to_mongo(df)

    df["Link_Icon"] = "🔗"

    return df.to_dict("records")

@callback(
    [
        Output('filters', 'children'),
        Output('count-chart-card', 'children'),
        Output('price-chart-card', 'children'),
        Output('table-card', 'children'),
    ],
    Input('stored-data','data'),
    State('submit-button', 'n_clicks'),
    prevent_initial_call=True,
)
def initial_loading(data,clicks):
    df = pd.DataFrame(data)
   
    return (
        filters(df,clicks),
        count_chart_card(df,clicks),
        price_chart_card(df,clicks),
        table_card(data,clicks)
    )

@callback(
    [
        Output({'type':'count-chart', 'index': MATCH}, 'figure'),
        Output({'type':'price-chart', 'index': MATCH}, 'figure'),
        Output({'type':'table', 'index': MATCH}, 'rowData'),
    ],
    [
        Input({'type':'price-slider', 'index': MATCH}, 'value'),
        Input({'type':'tags-input','index': MATCH}, 'value'),
        Input({'type':'agregacao', 'index': MATCH}, 'value'),
        State('stored-data','data'),
    ],
    prevent_initial_call=True,
)
def updates(values,tags,agregacao,data):
    df = pd.DataFrame(data)
    dff = df.copy()
    if values:
        dff = df[(df['Preco'] >= values[0]) & (df['Preco'] <= values[1])]

    if tags:
        for tag in tags:
            dff = dff[dff['Titulo'].str.contains(tag, case=False, na=False)]

    return (
        suporte.count_chart(dff, agregacao),
        suporte.price_chart(dff, agregacao),
        dff.to_dict("records")
    )

if __name__ == "__main__":
    app.run_server(debug=True)