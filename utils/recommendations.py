
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def recommend_books(book_id, books, number_of_recommendations=4):

    # Create a clean copy of the dataset
    books = books.reset_index(drop=True).copy()

    # Find the selected book
    selected_book = books[books["book_id"] == book_id]

    if selected_book.empty:
        return pd.DataFrame()

    # Fill missing values to avoid errors
    text_columns = [
        "title",
        "author",
        "genre",
        "description",
        "themes"
    ]

    for column in text_columns:
        if column not in books.columns:
            books[column] = ""

        books[column] = books[column].fillna("").astype(str)

    # Combine all book features
    # Repeated fields give them more influence in TF-IDF
    books["content"] = (
        (books["title"] + " ") * 2 +
        books["author"] + " " +
        (books["genre"] + " ") * 2 +
        books["description"] + " " +
        (books["themes"] + " ") * 2
    )

    # Convert book information into numerical TF-IDF vectors
    tfidf = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000
    )

    tfidf_matrix = tfidf.fit_transform(books["content"])

    # Calculate similarity between every pair of books
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Find the selected book's position
    selected_index = selected_book.index[0]

    # Get similarity scores
    similarity_scores = list(
        enumerate(similarity_matrix[selected_index])
    )

    # Sort from highest similarity to lowest
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    # Remove the selected book itself
    similarity_scores = [
        item for item in similarity_scores
        if item[0] != selected_index
    ]

    # Select the top matching books
    top_matches = similarity_scores[:number_of_recommendations]

    # Get recommended book positions
    recommended_indices = [
        item[0] for item in top_matches
    ]

    # Create recommendations dataframe
    recommendations = books.iloc[recommended_indices].copy()

    # Add similarity percentages
    recommendations["similarity_score"] = [
        round(item[1] * 100, 2)
        for item in top_matches
    ]

    return recommendations
