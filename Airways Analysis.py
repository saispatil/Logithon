# -*- coding: utf-8 -*-
"""logithon.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ma-z0iUzbnjXFqQP7amzkADv5prosqQ9
"""

pip install flask

import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Download NLTK resources
nltk.download('vader_lexicon')

# Load the dataset
df = pd.read_excel('cargoairways.xlsx')

# Display basic information about the dataset
print("Dataset shape:", df.shape)
print("Columns:", df.columns)
print("\nSample data:")
print(df.head())

# Drop rows with NaN values in the 'customer_review' column
df = df.dropna(subset=['customer_review'])

# Sentiment analysis
sid = SentimentIntensityAnalyzer()
df['sentiment_score'] = df['customer_review'].apply(lambda x: sid.polarity_scores(x)['compound'])

# Plot sentiment distribution
plt.figure(figsize=(8, 6))
df['sentiment_score'].hist(bins=20, color='skyblue', edgecolor='black', alpha=0.7)
plt.title('Sentiment Distribution of Customer Reviews')
plt.xlabel('Sentiment Score')
plt.ylabel('Frequency')
plt.show()

# Display sample data with sentiment scores
print("\nSample data with sentiment scores:")
print(df[['customer_review', 'sentiment_score']].head())

# Group the dataset by airline and calculate the mean ratings for each service aspect
airline_ratings = df.groupby('airline')[['seat_comfort', 'cabin_service', 'food_bev', 'entertainment', 'ground_service', 'value_for_money']].mean()

# Calculate the overall rating for each airline
airline_ratings['overall_rating'] = airline_ratings.mean(axis=1)

# Rank the airlines based on their overall ratings
ranked_airlines = airline_ratings.sort_values(by='overall_rating', ascending=False)

# Display the ranked airlines
print("Ranking of Airlines based on Overall Ratings:")
print(ranked_airlines[['overall_rating']])

import matplotlib.pyplot as plt

# Group the dataset by airline and calculate the mean value_for_money ratings for each airline
value_for_money_ratings = df.groupby('airline')['value_for_money'].mean()

# Rank the airlines based on their mean value_for_money ratings
ranked_airlines_value_for_money = value_for_money_ratings.sort_values(ascending=False)

# Plot the histogram of value_for_money ratings
plt.figure(figsize=(10, 6))
ranked_airlines_value_for_money.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Ranking of Airlines based on Value for Money')
plt.xlabel('Airline')
plt.ylabel('Mean Value for Money Rating')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Function to suggest airlines based on user preferences
def suggest_airlines(df, preferences):
    # Calculate composite score for each airline based on user preferences
    df['composite_score'] = (df['value_for_money'] * preferences['value_for_money'] +
                             df['recommended'].map({'yes': 1, 'no': 0}) * preferences['recommended'] +
                             df['overall'] / 10 * preferences['overall_rating'])

    # Rank the airlines based on composite scores
    ranked_airlines = df.sort_values(by='composite_score', ascending=False)

    # Get top N recommendations
    top_n = 5
    recommendations = ranked_airlines[['airline', 'composite_score']].head(top_n)

    return recommendations

# Example user preferences
user_preferences = {
    'value_for_money': 0.3,
    'recommended': 0.2,
    'overall_rating': 0.5
}

# Suggest airlines based on user preferences
user_recommendations = suggest_airlines(df, user_preferences)

# Display recommendations
print("Top Airlines Recommendations based on User Preferences:")
print(user_recommendations)

# Function to suggest airlines based on user preferences
def suggest_airlines(df):
    # Prompt user to input preferences
    print("Please rate each parameter from 1 to 5 (5 being the highest):")
    preferences = {}
    for parameter in ['value_for_money', 'recommended', 'overall_rating']:
        rating = float(input(f"Rate {parameter.replace('_', ' ').title()}: "))
        preferences[parameter] = rating / 5  # Normalize rating to range between 0 and 1

    # Calculate composite score for each airline based on user preferences
    df['composite_score'] = (df['value_for_money'] * preferences['value_for_money'] +
                             df['recommended'].map({'yes': 1, 'no': 0}) * preferences['recommended'] +
                             df['overall'] / 10 * preferences['overall_rating'])

    # Rank the airlines based on composite scores
    ranked_airlines = df.sort_values(by='composite_score', ascending=False)

    # Get top N recommendations
    top_n = 5
    recommendations = ranked_airlines[['airline', 'composite_score']].head(top_n)

    return recommendations

# Suggest airlines based on user preferences
user_recommendations = suggest_airlines(df)

# Display recommendations
print("Top Airlines Recommendations based on User Preferences:")
print(user_recommendations)

# Function to compare airlines based on selected parameters
def compare_airlines(df):
    # Prompt user to select parameters
    selected_parameters = []
    print("Select parameters you want to compare (enter 'done' when finished):")
    while True:
        parameter = input("Enter parameter (e.g., value_for_money, recommended, overall_rating): ")
        if parameter.lower() == 'done':
            break
        if parameter in df.columns:
            selected_parameters.append(parameter)
        else:
            print("Invalid parameter! Please enter a valid parameter.")

    if not selected_parameters:
        print("No parameters selected. Exiting.")
        return

    # Calculate composite score for each airline based on selected parameters
    df['composite_score'] = df[selected_parameters].mean(axis=1)

    # Rank the airlines based on composite scores
    ranked_airlines = df.sort_values(by='composite_score', ascending=False)

    return ranked_airlines[['airline', 'composite_score']]

# Compare airlines based on selected parameters
selected_airlines = compare_airlines(df)

# Display comparison results
if selected_airlines is not None and not selected_airlines.empty:
    print("Airlines Ranking based on Selected Parameters:")
    print(selected_airlines)
else:
    print("No comparison results to display.")











import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Download NLTK resources
nltk.download('vader_lexicon')

# Load the dataset
df = pd.read_excel('cargoairways.xlsx')

# Display basic information about the dataset
print("Dataset shape:", df.shape)
print("Columns:", df.columns)
print("\nSample data:")
print(df.head())

# Sentiment analysis
sid = SentimentIntensityAnalyzer()
df['sentiment_score'] = df['customer_review'].apply(lambda x: sid.polarity_scores(x)['compound'])

# Define features and target variable
X = df[['seat_comfort', 'cabin_service', 'food_bev', 'entertainment', 'ground_service', 'value_for_money', 'sentiment_score']]
y = df['recommended'].map({'yes': 1, 'no': 0})

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a random forest classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train, y_train)

# Feature importance
feature_importance = rf_classifier.feature_importances_
features = X.columns

# Plot feature importance
plt.figure(figsize=(10, 6))
plt.barh(features, feature_importance, color='skyblue')
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importance')
plt.show()

# Predictions and evaluation
y_pred = rf_classifier.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))