#import plotly.graph_objects as go # or 
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd


app = Dash()
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=5*1000, # refresh every 5 seconds (adjust as needed)
        n_intervals=0),

    html.H3(id='rate_text'),
    dcc.Graph(id='rate_update'),
    dcc.Graph(id='rear_path_update'),
    dcc.Graph(id='rise_update'),
    dcc.Graph(id='squat_update'),


])

@app.callback(
            [Output('rate_update', 'figure'),
            Output('rear_path_update', 'figure'),
            Output('rise_update', 'figure'),
            Output('squat_update', 'figure'),
            Output('rate_text', 'children')],
            [Input('interval-component', 'n_intervals')])
def update_excel_data(n):
    # Re-read the excel file every time the interval fires
    rate = pd.read_csv('stroke_travel.csv')

    ratio_list = []
    stroke_list = []
    travels = rate['travel']
    strokes = rate['stroke']
    for i, (travel, stroke) in enumerate(zip(travels, strokes)):
        if i == 0:
            continue
        travel_change = travels[i] - travels[i-1]
        ins_stroke = strokes[i] - strokes[i-1]
        ratio_list.append(travel_change/ins_stroke)
        stroke_list.append(stroke)
    rate_df = pd.DataFrame({'travel':rate['travel'][1:], 'stroke':stroke_list, 'leverage_ratio':ratio_list})

    rate_fig = px.scatter(rate_df, x='stroke', y='leverage_ratio', custom_data=['travel'], labels={'x':'Stroke', 'y':'Leverage Ratio'})
    #rate_fig = px.scatter(rate, x='travel', y='leverage_ratio', custom_data=['stroke'])
    rate_fig.update_traces(
    hovertemplate="<br>".join([
        "stroke: %{x}",
        "ratio: %{y}",
        "travel: %{customdata[0]}",
    ]) + "<extra></extra>" # Use <extra></extra> to remove the default trace name label
    )
    
    #rate_fig.update_yaxes(range=[1, 5])
    rear_path_fig = px.scatter(rate, x='stroke', y='wheel_path')
    rise_fig = px.scatter(rate, x='stroke', y='antirise')
    squat_fig = px.scatter(rate, x='stroke', y='antisquat')
    sag_point = stroke_list[-1]*.25
    rate_fig.add_vline(x=sag_point, line_width=3, line_dash="dash", line_color="green")
    rear_path_fig.add_vline(x=sag_point, line_width=3, line_dash="dash", line_color="green")
    rise_fig.add_vline(x=sag_point, line_width=3, line_dash="dash", line_color="green")
    squat_fig.add_vline(x=sag_point, line_width=3, line_dash="dash", line_color="green")


    average_ratio = ratio_list[0]/ratio_list[-1]
    header_text = f'Total travel:{rate['travel'].tolist()[-1]}, Average leverage ratio:{average_ratio}'

    return rate_fig, rear_path_fig, rise_fig, squat_fig, header_text

if __name__ == '__main__':
    app.run(debug=True)