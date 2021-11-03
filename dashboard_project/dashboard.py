import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd

dataframe = pd.read_csv('data.csv')
dict = {'age groups': 'age_x', 'political ideology': 'partylr_x', 'subjective social class': 'rank_x'}


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
app.title = "Immigrants and Korean Society"
server = app.server

# Layout section: Bootstrap
# ------------------------------------

app.layout = dbc.Container([

    dbc.Row([
        html.H3("Immigrants and Korean Society",
                className="text-center mt-4 mb-4")
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Div(
                    html.H5("Introduction", className="px-2 py-2"),
                    className="bg-primary text-white rounded mt-2 mb-4"
                ),
                html.P("The immigrant issue has become part of the central concern in Korean society in recent years. "
                       "This visualization project uses data from the Korean General Social Survey "
                       "conducted by the Survey Research Center at Sungkyunkwan University in 2003 (N=1315) and "
                       "2013 (N=1294), and was designed to present the time trend shift of how different social groups"
                       " in Korea see immigrant issues differently.",
                       style={'text-align': 'justify'}),
            ]),
            dbc.Row([
                html.H5("Variables",
                        className="mt-1"),
                dcc.Dropdown(
                    id='dropdown', multi=False, value='age groups',
                    options=[{'label': x, 'value': x}
                             for x in ['age groups', 'political ideology', 'subjective social class']],
                    className="mb-4")
            ]),
            dbc.Row([
                html.Div(
                    html.H5("Did you find...?", className="px-2 py-2"),
                    className="bg-primary text-white rounded mt-2 mb-4"
                ),
                html.Div([
                    html.P("1. Young Korean who suggested increasing the number of immigrants to Korea decreased by "
                           "12.8% from 2003 to 2013.", style={'text-align': 'justify'}),
                    html.P("2. Elder Korean who suggested immigrants take away jobs from Korean dropped by 9% "
                           "from 2003 to 2013.", style={'text-align': 'justify'}),
                    html.P("3. Interestingly, Korean who identified themselves as liberal associated immigrants with"
                           " crimes the most.",
                           style={'text-align': 'justify'}),
                    html.P("4. Korean who identified themselves as liberal tended to have a stricter idea"
                           " about being truly Korean.", style={'text-align': 'justify'}),
                ])
            ]),
            dbc.Row([
                html.Div(
                    html.H5("About the Dashboard", className="px-2 py-2"),
                    className="bg-primary text-white rounded mt-2 mb-4"
                ),
                html.Div([
                    html.P("This data visualization project is created by C.J. If you want to discuss anything about "
                           "this dashboard or the data, you can find me through the button below that links to my "
                           "LinkedIn profile.", style={'text-align': 'justify'}),
                    html.Div([
                        dbc.Button(
                            "Contact the Author",
                            href="https://www.linkedin.com/in/c-j-hsu",
                            external_link=True,
                            outline=False,
                            color="success",
                        ),
                    ], className="mt-4 mb-4")
                ])
            ]),
        ], style={'padding-right': 25, 'padding-left': 25}, xs=12, sm=12, md=3, lg=3, xl=3),

        dbc.Col([
            dbc.Row([
                html.Div(
                    html.H5("1. Do you think the number of immigrants in Korea should be...",
                            className="px-2 py-2"),
                    className="bg-primary text-white rounded mt-2"
                ),
                dcc.Graph(id='pies', figure={}, className="mb-2")
            ]),
            dbc.Row([
                html.Div(
                    html.H5("2. Opinions on immigrants",
                            className="px-2 py-2"),
                    className="bg-primary text-white rounded mt-2 mb-2"
                )
            ]),
            dbc.Row([
                html.Div([
                    dcc.Tabs([
                        dcc.Tab(label='Immigrants and Crimes', children=[
                            html.H5("Do you agree that immigrants increase crime rate?", className="text-center mt-4"),
                            dcc.Graph(id='immcrime', figure={}, className="mb-2")
                        ]),
                        dcc.Tab(label='Immigrants and Jobs', children=[
                            html.H5("Do you agree that immigrants take away jobs from Korean?",
                                    className="text-center mt-4"),
                            dcc.Graph(id='immjobs', figure={}, className="mb-2")
                        ]),
                        dcc.Tab(label='Cultural Diversity', children=[
                            html.H5("Do you agree that immigrants bring in new ideas and cultures?",
                                    className="text-center mt-4"),
                            dcc.Graph(id='immideas', figure={}, className="mb-2")
                        ]),
                    ])
                ])
            ]),
            dbc.Row([
                html.Div(
                    html.H5("3. Which of the following aspect is important for being truly Korean?",
                            className="px-2 py-2"),
                    className="bg-primary text-white rounded mt-2 mb-2"
                ),
            ]),
            dbc.Row([
                html.Div([
                    dcc.Tabs([
                        dcc.Tab(label='2003', children=[
                            dcc.Graph(id='kr2003', figure={}, className="mb-2")
                        ]),
                        dcc.Tab(label='2013', children=[
                            dcc.Graph(id='kr2013', figure={}, className="mb-2")
                        ]),
                    ])
                ])
            ]),
        ], style={'padding-right': 25, 'padding-left': 25}, xs=12, sm=12, md=9, lg=9, xl=9)
    ]),
])

@app.callback(
    Output(component_id='pies', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')],
    prevent_initial_call=False
)
def update_my_graph(val_chosen):

    ip = dict[val_chosen]

    df = dataframe.copy()
    donuts = df.groupby(['year', ip])['letin1_x'].value_counts().sort_index().reset_index(name='count')

    try:
        donuts['partylr_x'] = pd.Categorical(donuts['partylr_x'], ordered=True,
                                             categories=['conservative', 'middle', 'liberal'])
        abc = donuts.sort_values(by=['partylr_x'])
        (a, b, c) = tuple(abc[ip].unique())
    except:
        (a, b, c) = tuple(donuts[ip].unique())

    donuts1 = donuts.loc[(donuts['year'] == 2003) & (donuts[ip] == a)]
    donuts2 = donuts.loc[(donuts['year'] == 2013) & (donuts[ip] == a)]
    donuts3 = donuts.loc[(donuts['year'] == 2003) & (donuts[ip] == b)]
    donuts4 = donuts.loc[(donuts['year'] == 2013) & (donuts[ip] == b)]
    donuts5 = donuts.loc[(donuts['year'] == 2003) & (donuts[ip] == c)]
    donuts6 = donuts.loc[(donuts['year'] == 2013) & (donuts[ip] == c)]

    labels = ['increased', 'remained', 'reduced']

    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=2, cols=3, specs=[[{'type': 'pie'}, {'type': 'pie'}, {'type': 'pie'}],
                                               [{'type': 'pie'}, {'type': 'pie'},{'type': 'pie'}]],
                        horizontal_spacing=0.085, vertical_spacing=0.085,
                        x_title=val_chosen, #y_title='year',
                        column_titles=[a, b, c], row_titles=['2003', '2013'],
                        )

    fig.layout.template = "plotly_white"
    fig.add_trace(go.Pie(labels=labels, values=donuts1['count'].values, name=a), 1, 1)
    fig.add_trace(go.Pie(labels=labels, values=donuts2['count'].values, name=a), 2, 1)
    fig.add_trace(go.Pie(labels=labels, values=donuts3['count'].values, name=b), 1, 2)
    fig.add_trace(go.Pie(labels=labels, values=donuts4['count'].values, name=b), 2, 2)
    fig.add_trace(go.Pie(labels=labels, values=donuts5['count'].values, name=c), 1, 3)
    fig.add_trace(go.Pie(labels=labels, values=donuts6['count'].values, name=c), 2, 3)

    fig.update_traces(direction='clockwise', sort=False, hole=.3, hoverinfo="label+percent+name", showlegend=True,
                      marker={'colors': ['green', 'grey', 'red']})
    fig.update_layout(legend={'orientation': 'h', 'xanchor': 'center', 'x': 0.5, 'y': -0.4})
    fig.for_each_annotation(lambda x: x.update(y=1.1) if x.text in [a, b, c] else ())
    fig.for_each_annotation(lambda x: x.update(x=-0.1, textangle=-90) if x.text in ['2003', '2013'] else ())
    return fig

@app.callback(
    Output(component_id='immcrime', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')],
    prevent_initial_call=False
)
def update_my_graph(val_chosen):
    ip = dict[val_chosen]

    df = dataframe.copy()
    barh = df.groupby(['year', ip])['immcrime_x'].value_counts(normalize=True).sort_index().unstack().reset_index()
    barh.iloc[:, 2:] = barh.iloc[:, 2:].applymap(lambda x: round(x, 3))

    try:
        barh['partylr_x'] = pd.Categorical(barh['partylr_x'], ordered=True,
                                             categories=['conservative', 'middle', 'liberal'])
        abc = barh.sort_values(by=['partylr_x'])
        (a, b, c) = tuple(abc[ip].unique())
    except:
        (a, b, c) = tuple(barh[ip].unique())

    barh1 = barh.loc[barh[ip] == a]
    barh2 = barh.loc[barh[ip] == b]
    barh3 = barh.loc[barh[ip] == c]

    fig = make_subplots(rows=3, cols=1, specs=[[{"type": "bar"}], [{"type": "bar"}], [{"type": "bar"}]],
                        subplot_titles=[a, b, c],
                        vertical_spacing=0.2)

    fig.layout.template = "plotly_white"
    for data, row, ld in zip([barh1, barh2, barh3], [1, 2, 3], [True, False, False]):
        fig.add_trace(go.Bar(
            x=-data['neutral'],
            y=['2003', '2013'],
            name='neutral',
            orientation='h',
            customdata=data['neutral'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group1",
            showlegend=ld,
            legendrank=3,
            marker_color='grey'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=-data['disagree'],
            y=['2003', '2013'],
            name='disagree',
            orientation='h',
            customdata=data['disagree'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group2",
            showlegend=ld,
            legendrank=2,
            marker_color='orangered'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=-data['strongly disagree'],
            y=['2003', '2013'],
            name='strongly disagree',
            orientation='h',
            customdata=data['strongly disagree'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group3",
            showlegend=ld,
            legendrank=1,
            marker_color='red'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=data['agree'],
            y=['2003', '2013'],
            name='agree',
            orientation='h',
            hovertemplate="%{y}: %{x}",
            legendgroup="group4",
            showlegend=ld,
            legendrank=4,
            marker_color='forestgreen'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=data['strongly agree'],
            y=['2003', '2013'],
            name='strongly agree',
            orientation='h',
            hovertemplate="%{y}: %{x}",
            legendgroup="group5",
            showlegend=ld,
            legendrank=5,
            marker_color='darkgreen'
        ), row, 1)

    fig.update_layout(margin={'t': 40})
    fig.update_layout(barmode='relative', legend_traceorder="normal")
    fig.update_layout(legend={'orientation': 'h', 'xanchor': 'center', 'x': 0.5, 'y': -0.3})
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[-0.9, 0.6], tickformat=".0%")
    return fig

@app.callback(
    Output(component_id='immjobs', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')],
    prevent_initial_call=False
)
def update_my_graph(val_chosen):
    ip = dict[val_chosen]

    df = dataframe.copy()
    barh = df.groupby(['year', ip])['immjobs_x'].value_counts(normalize=True).sort_index().unstack().reset_index()
    barh.iloc[:, 2:] = barh.iloc[:, 2:].applymap(lambda x: round(x, 3))

    try:
        barh['partylr_x'] = pd.Categorical(barh['partylr_x'], ordered=True,
                                             categories=['conservative', 'middle', 'liberal'])
        abc = barh.sort_values(by=['partylr_x'])
        (a, b, c) = tuple(abc[ip].unique())
    except:
        (a, b, c) = tuple(barh[ip].unique())

    barh1 = barh.loc[barh[ip] == a]
    barh2 = barh.loc[barh[ip] == b]
    barh3 = barh.loc[barh[ip] == c]

    fig = make_subplots(rows=3, cols=1, specs=[[{"type": "bar"}], [{"type": "bar"}], [{"type": "bar"}]],
                        subplot_titles=[a, b, c],
                        vertical_spacing=0.2)

    fig.layout.template = "plotly_white"
    for data, row, ld in zip([barh1, barh2, barh3], [1, 2, 3], [True, False, False]):
        fig.add_trace(go.Bar(
            x=-data['neutral'],
            y=['2003', '2013'],
            name='neutral',
            orientation='h',
            customdata=data['neutral'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group1",
            showlegend=ld,
            legendrank=3,
            marker_color='grey'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=-data['disagree'],
            y=['2003', '2013'],
            name='disagree',
            orientation='h',
            customdata=data['disagree'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group2",
            showlegend=ld,
            legendrank=2,
            marker_color='orangered'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=-data['strongly disagree'],
            y=['2003', '2013'],
            name='strongly disagree',
            orientation='h',
            customdata=data['strongly disagree'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group3",
            showlegend=ld,
            legendrank=1,
            marker_color='red'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=data['agree'],
            y=['2003', '2013'],
            name='agree',
            orientation='h',
            hovertemplate="%{y}: %{x}",
            legendgroup="group4",
            showlegend=ld,
            legendrank=4,
            marker_color='forestgreen'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=data['strongly agree'],
            y=['2003', '2013'],
            name='strongly agree',
            orientation='h',
            hovertemplate="%{y}: %{x}",
            legendgroup="group5",
            showlegend=ld,
            legendrank=5,
            marker_color='darkgreen'
        ), row, 1)

    fig.update_layout(margin={'t': 40})
    fig.update_layout(barmode='relative', legend_traceorder="normal")
    fig.update_layout(legend={'orientation': 'h', 'xanchor': 'center', 'x': 0.5, 'y': -0.3})
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[-0.9, 0.6], tickformat=".0%")
    return fig

@app.callback(
    Output(component_id='immideas', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')],
    prevent_initial_call=False
)
def update_my_graph(val_chosen):
    ip = dict[val_chosen]

    df = dataframe.copy()
    barh = df.groupby(['year', ip])['immideas_x'].value_counts(normalize=True).sort_index().unstack().reset_index()
    barh.iloc[:, 2:] = barh.iloc[:, 2:].applymap(lambda x: round(x, 3))

    try:
        barh['partylr_x'] = pd.Categorical(barh['partylr_x'], ordered=True,
                                             categories=['conservative', 'middle', 'liberal'])
        abc = barh.sort_values(by=['partylr_x'])
        (a, b, c) = tuple(abc[ip].unique())
    except:
        (a, b, c) = tuple(barh[ip].unique())

    barh1 = barh.loc[barh[ip] == a]
    barh2 = barh.loc[barh[ip] == b]
    barh3 = barh.loc[barh[ip] == c]

    fig = make_subplots(rows=3, cols=1, specs=[[{"type": "bar"}], [{"type": "bar"}], [{"type": "bar"}]],
                        subplot_titles=[a, b, c],
                        vertical_spacing=0.2)

    fig.layout.template = "plotly_white"
    for data, row, ld in zip([barh1, barh2, barh3], [1, 2, 3], [True, False, False]):
        fig.add_trace(go.Bar(
            x=-data['neutral'],
            y=['2003', '2013'],
            name='neutral',
            orientation='h',
            customdata=data['neutral'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group1",
            showlegend=ld,
            legendrank=3,
            marker_color='grey'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=-data['disagree'],
            y=['2003', '2013'],
            name='disagree',
            orientation='h',
            customdata=data['disagree'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group2",
            showlegend=ld,
            legendrank=2,
            marker_color='orangered'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=-data['strongly disagree'],
            y=['2003', '2013'],
            name='strongly disagree',
            orientation='h',
            customdata=data['strongly disagree'] * 100,
            hovertemplate="%{y}: %{customdata}%",
            legendgroup="group3",
            showlegend=ld,
            legendrank=1,
            marker_color='red'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=data['agree'],
            y=['2003', '2013'],
            name='agree',
            orientation='h',
            hovertemplate="%{y}: %{x}",
            legendgroup="group4",
            showlegend=ld,
            legendrank=4,
            marker_color='forestgreen'
        ), row, 1)

        fig.add_trace(go.Bar(
            x=data['strongly agree'],
            y=['2003', '2013'],
            name='strongly agree',
            orientation='h',
            hovertemplate="%{y}: %{x}",
            legendgroup="group5",
            showlegend=ld,
            legendrank=5,
            marker_color='darkgreen'
        ), row, 1)

    fig.update_layout(margin={'t': 40})
    fig.update_layout(barmode='relative', legend_traceorder="normal")
    fig.update_layout(legend={'orientation': 'h', 'xanchor': 'center', 'x': 0.5, 'y': -0.3})
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[-0.9, 0.6], tickformat=".0%")
    return fig

@app.callback(
    Output(component_id='kr2003', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')],
    prevent_initial_call=False
)
def update_my_graph(val_chosen):
    ip = dict[val_chosen]

    df = dataframe.copy()
    hand = df.groupby(['year', ip])[['krbornin_x', 'krcit_x', 'krlived_x', 'krkorean_x', 'krconfuc_x', 'krfeel_x',
                                     'krancstr_x']].mean().sort_index().reset_index()
    hand2 = hand.loc[hand['year'] == 2003]

    x_labels = ['born in Korea', 'poccessing Korean<br>citizenship', 'living in Korea', 'speaking Korean',
                'practicing Confucianism', 'identifying oneself as<br>a Korean', 'Having Korean ancestry']

    try:
        hand2['partylr_x'] = pd.Categorical(hand2['partylr_x'], ordered=True,
                                             categories=['conservative', 'middle', 'liberal'])
        abc = hand2.sort_values(by=['partylr_x'])
        (a, b, c) = tuple(abc[ip].unique())
    except:
        (a, b, c) = tuple(hand2[ip].unique())

    aa = hand2.loc[hand2[ip] == a, ['krbornin_x', 'krcit_x', 'krlived_x', 'krkorean_x', 'krconfuc_x', 'krfeel_x',
                                    'krancstr_x']].values[0]
    bb = hand2.loc[hand2[ip] == b, ['krbornin_x', 'krcit_x', 'krlived_x', 'krkorean_x', 'krconfuc_x', 'krfeel_x',
                                    'krancstr_x']].values[0]
    cc = hand2.loc[hand2[ip] == c, ['krbornin_x', 'krcit_x', 'krlived_x', 'krkorean_x', 'krconfuc_x', 'krfeel_x',
                                    'krancstr_x']].values[0]

    fig = go.Figure(data=[
        go.Bar(name=a, x=x_labels, y=aa, marker_color='lightblue'),
        go.Bar(name=b, x=x_labels, y=bb, marker_color='steelblue'),
        go.Bar(name=c, x=x_labels, y=cc, marker_color='darkslateblue'),
    ])

    fig.layout.template = "plotly_white"
    fig.update_yaxes(range=[0, 1.05], tickformat=".0%")
    fig.update_xaxes(tickangle=60)
    fig.update_layout(barmode='group', title_text='by different '+val_chosen, title_x=0.5)
    return fig

@app.callback(
    Output(component_id='kr2013', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')],
    prevent_initial_call=False
)
def update_my_graph(val_chosen):
    ip = dict[val_chosen]

    df = dataframe.copy()
    hand = df.groupby(['year', ip])[['krbornin_x', 'krcit_x', 'krlived_x', 'krkorean_x', 'krconfuc_x', 'krfeel_x',
                                     'krancstr_x']].mean().sort_index().reset_index()
    hand2 = hand.loc[hand['year'] == 2013]

    x_labels = ['born in Korea', 'poccessing Korean<br>citizenship', 'living in Korea', 'speaking Korean',
                'practicing Confucianism', 'identifying oneself as<br>a Korean', 'Having Korean ancestry']

    try:
        hand2['partylr_x'] = pd.Categorical(hand2['partylr_x'], ordered=True,
                                             categories=['conservative', 'middle', 'liberal'])
        abc = hand2.sort_values(by=['partylr_x'])
        (a, b, c) = tuple(abc[ip].unique())
    except:
        (a, b, c) = tuple(hand2[ip].unique())

    aa = hand2.loc[hand2[ip] == a, ['krbornin_x', 'krcit_x', 'krlived_x', 'krkorean_x', 'krconfuc_x', 'krfeel_x',
                                    'krancstr_x']].values[0]
    bb = hand2.loc[hand2[ip] == b, ['krbornin_x', 'krcit_x', 'krlived_x', 'krkorean_x', 'krconfuc_x', 'krfeel_x',
                                    'krancstr_x']].values[0]
    cc = hand2.loc[hand2[ip] == c, ['krbornin_x', 'krcit_x', 'krlived_x', 'krkorean_x', 'krconfuc_x', 'krfeel_x',
                                    'krancstr_x']].values[0]

    fig = go.Figure(data=[
        go.Bar(name=a, x=x_labels, y=aa, marker_color='lightblue'),
        go.Bar(name=b, x=x_labels, y=bb, marker_color='steelblue'),
        go.Bar(name=c, x=x_labels, y=cc, marker_color='darkslateblue'),
    ])

    fig.layout.template = "plotly_white"
    fig.update_yaxes(range=[0, 1.05], tickformat=".0%")
    fig.update_xaxes(tickangle=60)
    fig.update_layout(barmode='group', title_text='by different '+val_chosen, title_x=0.5)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=3000)