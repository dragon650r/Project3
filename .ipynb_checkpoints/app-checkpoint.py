from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from bokeh.embed import components
import matplotlib.pyplot as plt
import io
import os
import plotly.io as pio
from flask import send_file

app = Flask(__name__)

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Hunter's pie chart
@app.route('/hunter')
def hunter_pie_chart():
    df = pd.read_csv('resources/netflix_titles.csv')
    
    # Filter for each genre and get directors
    genres = ['Documentaries', 'Dramas & International Movies', 'Stand-Up Comedy']
    director_counts = [359, 362, 334]
    directors = ['Vlad Yudin', 'Youssef Chahine', 'Raúl Campos, Jan Suter']

    # Create the pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(director_counts, labels=genres, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title('Genres and Directors')
    plt.axis('equal')

    # Save the pie chart to memory and serve it
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return render_template('plot.html', graph_html=None, hunter_questions=True, img=img)

# Jose's Plotly chart
@app.route('/jose')
def jose_scatter_plot():
    df = pd.read_csv('resources/netflix_titles.csv')
    df_cleaned = df[df['director'].notnull()]
    df_cleaned = df_cleaned.copy()
    df_cleaned['release_year'] = pd.to_numeric(df_cleaned['release_year'], errors='coerce')
    df_cleaned = df_cleaned.dropna(subset=['release_year'])
    df_cleaned['cast'] = df_cleaned['cast'].fillna('')
    df_cast_split = df_cleaned.assign(cast=df_cleaned['cast'].str.split(', ')).explode('cast')
    df_cast_split = df_cast_split[df_cast_split['cast'] != '']
    career_span = df_cast_split.groupby('cast')['release_year'].agg(['min', 'max'])
    career_span['trajectory'] = career_span['max'] - career_span['min']
    top_actors = career_span.nlargest(20, 'trajectory').index
    df_filtered = df_cast_split[df_cast_split['cast'].isin(top_actors)]
    
    fig = px.scatter(df_filtered, x='release_year', y='cast', color='cast',
                     title='Actors with Longest Career Trajectories on Netflix (By Year)',
                     labels={'release_year': 'Year', 'cast': 'Actor'},
                     color_discrete_sequence=px.colors.sequential.Viridis, opacity=0.7)
    
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=df_filtered['release_year'].min(), dtick=1),
                      yaxis=dict(tickmode='array', tickvals=top_actors),
                      hovermode='closest', showlegend=False, title_x=0.5)
    
    graph_html = pio.to_html(fig, full_html=False)
    
    return render_template('plot.html', graph_html=graph_html, hunter_questions=False, jose_questions=True)

# Aidan's Bokeh chart
@app.route('/aidan')
def aidan_scatter_plot():
    df = pd.read_csv('resources/netflix_titles.csv')
    df_cleaned = df[df['director'].notnull()]
    df_cleaned = df_cleaned.copy()
    df_cleaned = df_cleaned.dropna(subset=['cast'])
    df_cast_split = df_cleaned.assign(cast=df_cleaned['cast'].str.split(', ')).explode('cast')
    df_cast_split = df_cast_split[df_cast_split['cast'] != '']
    movie_count = df_cast_split['cast'].value_counts().head(100)
    x_values1 = movie_count.index.tolist()
    y_values1 = movie_count.values.tolist()

    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource, HoverTool, FactorRange
    from bokeh.palettes import Category10
    from bokeh.embed import components

    colors = Category10[10]
    color_dict = {name: colors[i % 10] for i, name in enumerate(x_values1)}
    source = ColumnDataSource(data=dict(
        x=x_values1, y=y_values1, color=[color_dict[name] for name in x_values1], name=x_values1, frequency=y_values1))
    p = figure(title="Top 100 Actors Frequency on Netflix", toolbar_location="above", tools="pan,reset,hover,wheel_zoom",
               height=1000, width=1000, x_range=FactorRange(*x_values1))
    p.scatter(x='x', y='y', source=source, size=8, color='color', alpha=0.7, legend_field="name", fill_alpha=0.6)
    hover = HoverTool()
    hover.tooltips = [("Actor Name", "@name"), ("# of Movies on Netflix", "@frequency")]
    p.add_tools(hover)
    p.legend.title = 'Actor Names'
    p.legend.orientation = 'vertical'
    p.legend.location = 'top_right'
    script, div = components(p)

    return render_template('bokeh-plot.html', script=script, div=div)

# Plotly route
@app.route('/plotly')
def plotly_plot():
    df = pd.read_csv('resources/netflix_titles.csv')
    df_cleaned = df[df['director'].notnull()]
    df_cleaned = df_cleaned.copy()
    df_cleaned['release_year'] = pd.to_numeric(df_cleaned['release_year'], errors='coerce')
    df_cleaned = df_cleaned.dropna(subset=['release_year'])
    df_cleaned['cast'] = df_cleaned['cast'].fillna('')
    df_cast_split = df_cleaned.assign(cast=df_cleaned['cast'].str.split(', ')).explode('cast')
    df_cast_split = df_cast_split[df_cast_split['cast'] != '']
    career_span = df_cast_split.groupby('cast')['release_year'].agg(['min', 'max'])
    career_span['trajectory'] = career_span['max'] - career_span['min']
    top_actors = career_span.nlargest(20, 'trajectory').index
    df_filtered = df_cast_split[df_cast_split['cast'].isin(top_actors)]
    
    fig = px.scatter(df_filtered, x='release_year', y='cast', color='cast',
                     title='Actors with Longest Career Trajectories on Netflix (By Year)',
                     labels={'release_year': 'Year', 'cast': 'Actor'},
                     color_discrete_sequence=px.colors.sequential.Viridis, opacity=0.7)
    
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=df_filtered['release_year'].min(), dtick=1),
                      yaxis=dict(tickmode='array', tickvals=top_actors),
                      hovermode='closest', showlegend=False, title_x=0.5)
    
    plot_data = {
        "data": fig.to_plotly_json()['data'],
        "layout": fig.to_plotly_json()['layout']
    }
    
    return render_template('plot.html', plot_data=plot_data, hunter_questions=False, jose_questions=True)

# Bokeh route
@app.route('/bokeh')
def bokeh_plot():
    df = pd.read_csv('resources/netflix_titles.csv')
    df_cleaned = df[df['director'].notnull()]
    df_cleaned = df_cleaned.copy()
    df_cleaned = df_cleaned.dropna(subset=['cast'])
    df_cast_split = df_cleaned.assign(cast=df_cleaned['cast'].str.split(', ')).explode('cast')
    df_cast_split = df_cast_split[df_cast_split['cast'] != '']
    movie_count = df_cast_split['cast'].value_counts().head(100)
    x_values1 = movie_count.index.tolist()
    y_values1 = movie_count.values.tolist()

    from bokeh.plotting import figure
    from bokeh.models import ColumnDataSource, HoverTool, FactorRange
    from bokeh.palettes import Category10
    from bokeh.embed import components

    colors = Category10[10]
    color_dict = {name: colors[i % 10] for i, name in enumerate(x_values1)}
    source = ColumnDataSource(data=dict(
        x=x_values1, y=y_values1, color=[color_dict[name] for name in x_values1], name=x_values1, frequency=y_values1))
    p = figure(title="Top 100 Actors Frequency on Netflix", toolbar_location="above", tools="pan,reset,hover,wheel_zoom",
               height=1000, width=1000, x_range=FactorRange(*x_values1))
    p.scatter(x='x', y='y', source=source, size=8, color='color', alpha=0.7, legend_field="name", fill_alpha=0.6)
    hover = HoverTool()
    hover.tooltips = [("Actor Name", "@name"), ("# of Movies on Netflix", "@frequency")]
    p.add_tools(hover)
    p.legend.title = 'Actor Names'
    p.legend.orientation = 'vertical'
    p.legend.location = 'top_right'
    script, div = components(p)
    
    return render_template('bokeh-plot.html', script=script, div=div)

if __name__ == '__main__':
    app.run(debug=True)
