from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio

# Initialize Flask app
app = Flask(__name__)

# Load the Netflix dataset
df = pd.read_csv('resources/netflix_titles.csv')

# Filter out rows where the 'Director' column is null
df_cleaned = df[df['director'].notnull()]

# Ensure 'release_year' is numeric and handle missing values
df_cleaned.loc[:, 'release_year'] = pd.to_numeric(df_cleaned['release_year'], errors='coerce')
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

# Create the career trajectory plot (Scatter Plot)
fig_career_trajectory = px.scatter(
    df_filtered,
    x='release_year', y='cast', color='cast',
    title='Actors with Longest Career Trajectories on Netflix (By Year, Top 20 Actors)',
    labels={'release_year': 'Year', 'cast': 'Actor'},
    color_discrete_sequence=px.colors.sequential.Viridis,
    opacity=0.7,
    height=600
)

# Convert the Plotly career trajectory graph to HTML div
graph_career_html = pio.to_html(fig_career_trajectory, full_html=False)

# Hunter's Pie Chart - Genres and Directors
# Manually input the data for genres and directors
genres = ['Documentaries', 'Dramas & International Movies', 'Stand-Up Comedy']
director_counts = [359, 362, 334]  # Corresponding counts for each genre
directors = ['Vlad Yudin', 'Youssef Chahine', 'Raúl Campos, Jan Suter']  # The most frequent directors for each genre

# Create the Pie Chart for Directors by Genre
fig_pie_chart = px.pie(
    names=genres, values=director_counts,
    title='Directors by Genre on Netflix',
    labels={'names': 'Genre', 'values': 'Movies/TV Shows Produced'},
    color=genres,
    color_discrete_sequence=px.colors.sequential.Inferno
)

# Convert the Plotly pie chart graph to HTML div
graph_pie_html = pio.to_html(fig_pie_chart, full_html=False)

# Home route that shows the home page with the "Career Trajectories" and "Directors by Genre" options
@app.route('/')
def index():
    return render_template('index.html', plot_career=graph_career_html, plot_pie=graph_pie_html)

# Route for the career trajectories chart
@app.route('/career')
def career_chart():
    return render_template('index.html', plot_career=graph_career_html)

# Route for the directors by genre pie chart
@app.route('/pie')
def pie_chart():
    return render_template('index.html', plot_pie=graph_pie_html)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)