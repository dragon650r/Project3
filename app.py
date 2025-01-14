# Import necessary dependencies
from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sqlalchemy import create_engine

# Initialize Flask app
app = Flask(__name__)

# Load the dataset
df = pd.read_csv('resources/netflix_titles.csv')

# Filter out rows where the 'Director' column is null
df_cleaned = df[df['director'].notnull()]

# Ensure 'release_year' is numeric and handle missing values
df_cleaned['release_year'] = pd.to_numeric(df_cleaned['release_year'], errors='coerce')
df_cleaned = df_cleaned.dropna(subset=['release_year'])

# Split the 'cast' column to get individual actors
df_cleaned['cast'] = df_cleaned['cast'].fillna('')
df_cast_split = df_cleaned.assign(cast=df_cleaned['cast'].str.split(', ')).explode('cast')

# Remove entries where actor is null or empty
df_cast_split = df_cast_split[df_cast_split['cast'] != '']

# Calculate the career span for each actor (difference between first and last appearance year)
career_span = df_cast_split.groupby('cast')['release_year'].agg(['min', 'max'])
career_span['trajectory'] = career_span['max'] - career_span['min']

# Get the top 20 actors with the longest career trajectories
top_actors = career_span.nlargest(20, 'trajectory').index

# Filter the data to only include the top 20 actors
df_filtered = df_cast_split[df_cast_split['cast'].isin(top_actors)]

# Create an interactive plot with Plotly
fig = px.scatter(
    df_filtered,
    x='release_year', y='cast', color='cast',  # Color by actor
    title='Actors with Longest Career Trajectories on Netflix (By Year, Top 20 Actors)',
    labels={'release_year': 'Year', 'cast': 'Actor'},
    color_discrete_sequence=px.colors.sequential.Viridis,
    opacity=0.7,
    height=600
)

# Convert the Plotly graph to HTML div
graph_html = pio.to_html(fig, full_html=False)

# Flask route to display the plot
@app.route('/')
def index():
    return render_template('index.html', plot=graph_html)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
