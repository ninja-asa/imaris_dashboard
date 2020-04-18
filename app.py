# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import plotly.express as px
import pandas as pd


def IdentifyPkls(path=os.getcwd()):
    if not os.path.isdir(path):
        return []
    list_files =  [filename for filename in os.listdir(path) if '.pkl' in filename]
    option_dropdown  =[]
    
    for file_pkl in list_files:
        option_dropdown.append({'label': file_pkl, 'value':file_pkl})
    return option_dropdown

def LoadDataframe(filename_pkl):
    df = pd.read_pickle(filename_pkl)
    return df



pkls = IdentifyPkls(os.getcwd())

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='Imaris data viewer', style={'textAlign':'center'}),
dcc.Input(id='input_dir', value=os.getcwd(), type='text',placeholder="Directory of pkls",style={'width': '100%'}),
    html.Label('Select Pickle'),
    dcc.Dropdown(
        options=pkls,
        value="",
        id='SelectPkl'
    ),
    html.Label('Select Feature'),
    dcc.Dropdown(
        value="",
        options=[],
        id='SelectFeature'
    ),
    dcc.Graph(id='graph-with-data'),
    html.Div(id='df_hidden', style={'display': 'none'}),
    html.Div(id='directory', style={'display': 'none'},children=os.getcwd()
    )
])

@app.callback(
    [Output(component_id='SelectPkl', component_property='options'),
    Output(component_id='directory', component_property='children'),
    Output(component_id='SelectPkl', component_property='value')],
    [Input(component_id='input_dir', component_property='value')]
)
def update_pkl_list(input_value):
    return IdentifyPkls(input_value), input_value,''

@app.callback(
    [Output(component_id='SelectFeature', component_property='options'),
    Output(component_id='SelectFeature', component_property='value'),
    Output(component_id='df_hidden',component_property='children')],
    [Input(component_id='SelectPkl', component_property='value'),
    Input(component_id='directory', component_property='children')]
)
def get_cols(input_value, directory):
    if input_value=="":
        return [],'', pd.DataFrame().to_json(date_format='iso', orient='split')
    df = LoadDataframe(os.path.join(directory,input_value))
    options_dropdown=[]
    for col in df.columns.values:
        options_dropdown.append({'label': col, 'value':col})
    return options_dropdown,df.columns.values[0], df.to_json(date_format='iso', orient='split')

@app.callback(
    Output('graph-with-data', 'figure'), 
    [Input('df_hidden', 'children'),
    Input('SelectFeature','value')])
def update_graph(json_data, feature):

    # more generally, this line would be
    # json.loads(jsonified_cleaned_data)
    df = pd.read_json(json_data, orient='split')
    if (df.empty):
        return {'data':[]};
    figure = px.box(df,x='Sample',y=feature, points='outliers')
    figure.update_layout(
            autosize=False,
            height=700
        )
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)