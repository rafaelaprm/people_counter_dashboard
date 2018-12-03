from flask import Flask, render_template
import dash
import math
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
import pandas as pd
from datetime import date, time, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Cliente, Local, Camera, Contagem

CLIENTE_ID = 1
DB_CONN_STRING = 'postgres://peoplecounter:peoplecounter@localhost:5432/peoplecounter'

engine = create_engine(DB_CONN_STRING, echo=False)

server = Flask(__name__)
app = dash.Dash(__name__, server=server)
app.config.suppress_callback_exceptions = True


def get_contagem_df(busca_local, busca_camera):

    query = "SELECT cl.nome AS cliente_nome, l.nome AS local_nome, l.cep, l.endereco, l.cidade, l.estado \
        FROM locais l \
        RIGHT JOIN clientes cl ON l.cliente_id = cl.cliente_id \
        WHERE l.cliente_id = {0} AND l.nome LIKE '%%{1}%%'".format(CLIENTE_ID, busca_local.upper())

    local_selecionado = pd.read_sql(query, engine)

    query = "SELECT cl.nome AS cliente_nome, l.nome AS local_nome, cam.nome AS camera_nome \
        FROM cameras cam \
        RIGHT JOIN locais l ON cam.local_id = l.local_id \
        RIGHT JOIN clientes cl ON l.cliente_id = cl.cliente_id \
        WHERE l.cliente_id = {0} AND l.cep = '{1}' AND cam.nome LIKE '%%{2}%%'".format(CLIENTE_ID, local_selecionado.cep[0], busca_camera.upper())
    
    camera_selecionada = pd.read_sql(query, engine)

    query = "SELECT cont.timestamp, cont.qtd_pessoas_in, cont.qtd_pessoas_out \
        FROM contagem cont \
        RIGHT JOIN cameras cam ON cont.camera_id = cam.camera_id\
        RIGHT JOIN locais l ON cam.local_id = l.local_id \
        RIGHT JOIN clientes cl ON l.cliente_id = cl.cliente_id \
        WHERE cl.cliente_id = {0} AND l.cep = '{1}' AND cam.nome = '{2}' \
        ORDER BY cont.contagem_id".format(CLIENTE_ID, local_selecionado.cep[0], camera_selecionada.camera_nome[0])

    contagem = pd.read_sql(query, engine)

    return contagem



# return html Table with dataframe values  
def df_to_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +
        
        # Body
        [
            html.Tr(
                [
                    html.Td(df.iloc[i][col])
                    for col in df.columns
                ]
            )
            for i in range(len(df))
        ]
    )


#returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [
            
            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id = id_value,
                className="indicator_value"
            ),
        ],
        className="four columns indicator",
        
    )


# returns pie chart that shows lead source repartition
def lead_source(df):
    qtd_pessoas = df.qtd_pessoas_in.value_counts()

    trace = go.Pie(
        labels=qtd_pessoas.index,
        values=qtd_pessoas,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(margin=dict(l=15, r=10, t=0, b=65), legend=dict(orientation="h"))
    
    return dict(data=[trace], layout=layout)



def converted_leads_in_count(df):
    tempo_inicio = df.timestamp.min()   
    tempo_fim = df.timestamp.max() + timedelta(seconds=1)
    intervalo_tempo = pd.date_range(start=tempo_inicio, end=tempo_fim, freq='3S')
    qtd_pessoas = df.qtd_pessoas_in
    

    trace = go.Scatter(
        x=intervalo_tempo,
        y=qtd_pessoas,
        name="converted leads",
        fill="tozeroy",
        fillcolor="#e6f2ff",
    )

    data = [trace]

    layout = go.Layout(
        xaxis=dict(showgrid=False),
        margin=dict(l=33, r=25, b=37, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


def converted_leads_out_count(df):
    tempo_inicio = df.timestamp.min()   
    tempo_fim = df.timestamp.max() + timedelta(seconds=1)
    intervalo_tempo = pd.date_range(start=tempo_inicio, end=tempo_fim, freq='3S')
    qtd_pessoas = df.qtd_pessoas_out
    

    trace = go.Scatter(
        x=intervalo_tempo,
        y=qtd_pessoas,
        name="converted leads",
        fill="tozeroy",
        fillcolor="#e6f2ff",
    )

    data = [trace]

    layout = go.Layout(
        xaxis=dict(showgrid=False),
        margin=dict(l=33, r=25, b=37, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


app.layout = html.Div(
    [
        # header
        html.Div([

            html.Span("People Counter Dashboard", className='app-title'),
            html.Div(
                html.Img(src='https://upload.wikimedia.org/wikipedia/commons/9/98/SupermercadoDB-Logo.png',height="100%")
                ,style={"float":"right","height":"100%"})
            ],
            className="row header"
            ),

        # tabs
        html.Div([

            dcc.Tabs(
                id="tabs",
                style={"height":"40","verticalAlign":"middle"},
                children=[
                    dcc.Tab(label="Resumo Estatístico {}".format(date.today().strftime("%d/%m/%Y")), value="leads_tab")
                ],
                value="leads_tab",
            ),

            ],
            className="row tabs_div"
        ),
       
                
        # divs that save dataframe for each tab
        html.Div(id="leads_df", style={"display": "none"}), # leads df

        # Tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),
        
        html.Link(href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css", rel="stylesheet")
    ],
    className="row",
    style={"margin": "0%"},
)


layout = [

        # top controls
    html.Div(
        [
    
        html.Div(
                dcc.Dropdown(
                    id="converted_leads_dropdown",
                    options=[
                        {"label": "DB CIDADE NOVA", "value": "cidade"},
                        {"label": "DB PARAIBA", "value": "paraiba"},
                    ],
                    value="cidade",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(
                dcc.Dropdown(
                    id="lead_source_dropdown",
                    options=[
                        {"label": "CAMERA ENTRADA 1", "value": "1"},
                        {"label": "CAMERA ENTRADA 2", "value": "2"},                   
                    ],
                    value="1",
                    clearable=False,
                ),
                className="two columns",
            ),
            ],
        className="row",
        style={"marginBottom": "10"},
    ),

    # indicators row div
    html.Div(
        [
            indicator(
                "#00cc96", "Total de Pessoas", "left_leads_indicator"
            ),
            indicator(
                "#119DFF", "Horário de Pico de Entrada", "middle_leads_indicator_in"
            ),
            indicator(
                "#119DFF", "Horário de Pico de Saída", "middle_leads_indicator_out"
            )

        ],
        className="row",
    ),

    # charts row div
    html.Div(
        [   
            html.Div(
                [
                    html.P("Frequencia (%) de pessoas"),
                    dcc.Graph(
                        id="lead_source",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="four columns chart_div"
            ),
            html.Div(
                [
                    html.P("Pessoas por horário entrando"),                        
                    dcc.Graph(
                        id="converted_leads_in",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="four columns chart_div"
            ),

            html.Div(
                [
                    html.P("Pessoas por horário saindo"),                        
                    dcc.Graph(
                        id="converted_leads_out",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="four columns chart_div"
            ),

            
        ],
        className="row",
        style={"marginTop": "5"},
    ),

    # table div
    html.Div(
        id="leads_table",
        className="row",
        style={
            "maxHeight": "350px",
            "overflowY": "scroll",
            "padding": "8",
            "marginTop": "5",
            "backgroundColor":"white",
            "border": "1px solid #C8D4E3",
            "borderRadius": "3px"
        },
    )

]

# update dataframe
@app.callback(
    Output("leads_df", "children"),
    [Input("converted_leads_dropdown", "value"), Input("lead_source_dropdown", "value")],
)
def df_callback(local, camera):
    return get_contagem_df(local, camera).to_json(orient="split")



# updates left indicator based on df updates
@app.callback(
    Output("left_leads_indicator", "children"), [Input("leads_df", "children")]
)
def left_leads_indicator_callback(df):
    df = pd.read_json(df, orient="split")
    total = df.qtd_pessoas_in.sum()
    return total


# updates middle indicator based on df updates
@app.callback(
    Output("middle_leads_indicator_in", "children"), [Input("leads_df", "children")]
)
def middle_leads_indicator_in_callback(df):
    df = pd.read_json(df, orient="split")
    pico_in = df.timestamp[df.qtd_pessoas_in == df.qtd_pessoas_in.max()].iloc[0].strftime('%H:%M')
    return pico_in


# updates middle indicator based on df updates
@app.callback(
    Output("middle_leads_indicator_out", "children"), [Input("leads_df", "children")]
)
def middle_leads_indicator_out_callback(df):
    df = pd.read_json(df, orient="split")
    pico_out = df.timestamp[df.qtd_pessoas_out == df.qtd_pessoas_out.max()].iloc[0].strftime('%H:%M')
    return pico_out


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("lead_source", "figure"),
    [Input("leads_df", "children")],
)
def lead_source_callback(df):
    df = pd.read_json(df, orient="split")
    return lead_source(df)


# update heat map figure based on dropdown's value and df updates
@app.callback(
    Output("map", "figure"),
    [Input("lead_source_dropdown", "value"), Input("leads_df", "children")],
)
def map_callback(status, df):
    df = pd.read_json(df, orient="split")
    return choropleth_map(status, df)


# update table based on dropdown's value and df updates
@app.callback(
    Output("leads_table", "children"),
    [Input("leads_df", "children")]
)
def leads_table_callback(df):
    df = pd.read_json(df, orient="split")
    
    return df_to_table(df)


# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("converted_leads_in", "figure"),
    [Input("leads_df", "children")],
)
def converted_leads_in_callback(df):
    df = pd.read_json(df, orient="split")
    return converted_leads_in_count(df)

# update pie chart figure based on dropdown's value and df updates
@app.callback(
    Output("converted_leads_out", "figure"),
    [Input("leads_df", "children")],
)
def converted_leads_out_callback(df):
    df = pd.read_json(df, orient="split")
    return converted_leads_out_count(df)



@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "leads_tab":
        return layout



if __name__ == "__main__":
    app.run_server(debug=True)