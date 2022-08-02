from dash import Dash, html, dcc
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd

#load CPS data from local csv
def getCpsData():
    df = pd.read_csv ('Econ8320_Project_Vaibhav_Varade.csv')
    return df

#filtes data from USA and Mexico
def filterUSAMexico(local_df, filter_countries):
    if filter_countries is not None:
        if 'United States' not in filter_countries:
            local_df = local_df.drop(local_df[local_df.NATIVE_MOTHER_COUNTRY_CODE == 57].index) # usa
        if 'Mexico' not in filter_countries:
            local_df = local_df.drop(local_df[local_df.NATIVE_MOTHER_COUNTRY_CODE == 303].index) # maxico
    return local_df;
    
dash_app = Dash(__name__)
app = dash_app.server

#load CPS data
df = getCpsData()

#get unique list for dropdowns - countries and city
country_list = df['COUNTRY'].unique()
city_list = df['CITY'].unique()

#for check box
filter_country_list = ['United States', 'Mexico']

# default figures
fig_bar = px.bar(df, x="CITY", hover_name="CITY", animation_frame = 'YEAR', y="POPULATION")
fig = px.scatter_geo(df, lat='LAT', lon='LON', color='COUNTRY', hover_name="CITY",
            animation_frame = 'YEAR', size="POPULATION", scope="usa")
    
dash_app.layout = html.Div(id = 'parent', children = [
    html.H1(id = 'H1', children = 'Demographic Changes in USA (2007 - 2021)', style = {'textAlign':'center',
                                            'marginTop':40,'marginBottom':5}),
    html.Div([
         html.Div([
            html.H3("Select Demographics Country(ies):"),
            dcc.Dropdown(id = 'dropdown_country',
                    options = country_list, multi=True, placeholder="Select a country(ies)")
         ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.H3("Select a Metro Area:"),
            dcc.Dropdown(id = 'dropdown_city', options = city_list, 
                         value = 'Omaha-Council Bluffs NE-IA', placeholder="Select a Metro City")
        ], style={'width': '50%', 'display': 'inline-block'})
    ], style={'width': '100%'}),
    
    html.Div([dcc.Checklist(id = 'filter_country',options = filter_country_list,
                            value = filter_country_list, inline=True)]),
    
    html.Div([
        html.Div([
            dcc.Graph(id='geo_plot', figure=fig)], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='bar_plot', figure=fig_bar)], style={'width': '50%', 'display': 'inline-block'})
    ], style={'width': '100%','marginTop':20}),
     
    html.Div([html.Cite('Source for CPS data - https://www.census.gov/data/developers/data-sets/census-microdata-api/cps/basic.html')]),
    html.Div([html.Cite('Source for GPS coordinates for Metro Cities - https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2021_Gazetteer/')])
])
#Call back to refresh scatter geo  from country selection  
@dash_app.callback(Output(component_id='geo_plot', component_property= 'figure'),
              [Input(component_id='dropdown_country', component_property= 'value')],
              [Input(component_id='filter_country', component_property= 'value')])
def graph_update(country, filter_country):
    
    #get global dataframe
    global df
    
    #assign it to local dataframe
    local_df = df
    
    #filter USA or Mexico population if check box unselected
    local_df = filterUSAMexico(local_df, filter_country)
    
    #filter dataframe from dropdown countries
    if country is not None and len(country) != 0:
        country_list = list(country)
        local_df = local_df[local_df['COUNTRY'].isin(country_list)].reset_index()
        
    #print(local_df)    
    fig = px.scatter_geo(local_df, lat='LAT', lon='LON', color="COUNTRY", hover_name="CITY",
                animation_frame = 'YEAR', size="POPULATION", scope="usa", size_max=30,
                hover_data={'CITY':True,'COUNTRY':True,'POPULATION':True,'LAT':False,'LON':False})
    title = 'Changing demographics in US cities'
    fig.update_layout(title = title,  margin={"r":0,"t":25,"l":10,"b":0})
    return fig  

#Call back to refresh bar chart from country and city selection
@dash_app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown_city', component_property= 'value')],
              [Input(component_id='dropdown_country', component_property= 'value')],
              [Input(component_id='filter_country', component_property= 'value')])
def bar_update(city, country, filter_country):

    #get global dataframe
    global df
    
    #assign it to local dataframe
    local_df = df
    
    #filter USA or Mexico population if check box unselected
    local_df = filterUSAMexico(local_df, filter_country)
    
    #filter df as per two dropdown selections - countries and city
    if (country is not None and len(country) != 0 and city is not None and len(city) != 0):
        country_list = list(country)
        local_df = local_df[local_df['COUNTRY'].isin(country_list)].reset_index()
        local_df = local_df[local_df['CITY'] == city].reset_index()
    elif (country is not None and len(country) != 0):
        country_list = list(country)
        local_df = local_df[local_df['COUNTRY'].isin(country_list)].reset_index()
    elif (city is not None and len(city) != 0):
        local_df = local_df[local_df['CITY'] == city].reset_index()
        
    local_df = local_df.sort_values(by=['YEAR','COUNTRY']).reset_index(drop=True)
    
    fig = px.bar(local_df, x = 'YEAR', color="COUNTRY", y="POPULATION") 
    
    fig.update_layout(title = 'Changing demographics for Metro Area: '+city,  margin={"r":0,"t":25,"l":10,"b":0}, 
                     xaxis_title="Census Year", yaxis_title="Population",)
    
    return fig 

if __name__ =='__main__':
    dash_app.run_server(debug=True,host='0.0.0.0', port='80')
