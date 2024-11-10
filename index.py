from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd


## Author -Utkarsh Pratap Singh

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Inititalization of Flask App
app = Flask(__name__)

# Loading data and Models using error handling
try:
    popular_df = pickle.load(open('models/popular.pkl', 'rb'))
    pt = pickle.load(open('models/pt.pkl', 'rb'))
    similarity_score = pickle.load(open('models/similarity_score.pkl', 'rb'))
    books = pickle.load(open('models/books.pkl', 'rb'))
except FileNotFoundError as e:
    print(f"Error loading model files: {e}")
    popular_df, pt, similarity_score, books = None, None, None, None



# Home Route
# this page will show top 50 books of all time
@app.route('/home')
def index():
    # Check if popular_df is loaded successfully
    if popular_df is not None:
        return render_template('index.html',
                               book_name=list(popular_df['Book-Title'].values),
                               author=list(popular_df['Book-Author'].values),
                               votes=list(popular_df['noOfRatings'].values),
                               avg_rating=list(popular_df['AverageRating'].values),
                               images=list(popular_df['Image-URL-M'].values))
    else:
        return "Error: Could not load popular books data.", 500

# Recommend Route
# for the recommendation purpose
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            recommendations = get_recommendations(user_input)
            return render_template('recommend.html', data=recommendations)
        else:
            return render_template('recommend.html', data=[["Book title is required."]])
    return render_template('recommend.html')

# Helper function to get recommendations
def get_recommendations(book_title):
    if pt is None or similarity_score is None or books is None:
        return [["Error: Model files are not loaded."]]

    try:
        # Check if the book title exists in the dataset
        if book_title in pt.index:
            idx = np.where(pt.index == book_title)[0][0]
            similar_books = sorted(list(enumerate(similarity_score[idx])), key=lambda x: x[1], reverse=True)[1:6]

            recommendations = []
            for i in similar_books:
                book_data = []
                temp_df = books[books['Book-Title'] == pt.index[i[0]]]
                if not temp_df.empty:
                    book_data.extend([
                        temp_df.iloc[0]['Book-Title'],
                        temp_df.iloc[0]['Book-Author'],
                        temp_df.iloc[0]['Image-URL-M'],
                        temp_df.iloc[0]['Publisher']
                    ])
                    recommendations.append(book_data)
            return recommendations
        else:
            return [["Book not found. Please try another title."]]
    except Exception as e:
        print(f"Error in recommendation processing: {e}")
        return [["Error processing the recommendation."]]

# API route for AJAX requests (if needed)
@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    user_input = request.json.get('user_input')
    if user_input:
        recommendations = get_recommendations(user_input)
        return jsonify(recommendations=recommendations)
    return jsonify(error="Book title is required."), 400

# Run app
if __name__ == '__main__':
    app.run(debug=True)
