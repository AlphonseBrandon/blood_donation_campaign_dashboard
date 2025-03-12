# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from wordcloud import WordCloud
import nltk
import re
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer


cwd = os.path.dirname(os.path.abspath(__file__))  
print('cwd is >> ', cwd)

# Configuration
CONFIG = {
    'data_path': os.path.join(cwd , 'challenge.xlsx (Converted - 2025-03-11 08_28).xlsx'),
    'output_dir': os.path.join(cwd , 'output'),
    'plot_format': 'png',
    'date_column': 'Date',  # Update with actual date column name that u want to process
    'text_column':'Si_autres_raison_préciser_',
    'random_state': 42,
    'test_size': 0.2
}

os.makedirs(CONFIG['output_dir'], exist_ok=True)

# Initialize NLTK 
nltk.download('stopwords')
stop_words = set(nltk.corpus.stopwords.words('french'))

def load_data(path: str) -> dict:
    """Load all sheets from Excel file into a dictionary of DataFrames."""
    return pd.read_excel(path, sheet_name=None)

def preprocess_text(text: str) -> str:
    """Clean and preprocess text data."""
    if pd.isna(text):
        return ''
    text = re.sub(r'[^a-zA-Zéèêëàâôùç\s]', '', str(text))
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text

def analyze_sentiment(text: str) -> str:
    """Perform sentiment analysis """
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.2:
        return 'Positive'
    elif analysis.sentiment.polarity < -0.2:
        return 'Negative'
    return 'Neutral'

def generate_word_cloud(texts: pd.Series, filename: str) -> None:
    """Generate and save a word cloud visualization."""
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(texts))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(os.path.join(CONFIG['output_dir'], filename), format=CONFIG['plot_format'])
    plt.close()

def plot_sentiment_distribution(data: pd.Series, filename: str) -> None:
    """Generate and save sentiment distribution plot."""
    plt.figure(figsize=(8, 5))
    sns.countplot(x=data, palette='viridis')
    plt.title('Distribution des Sentiments des Retours')
    plt.xlabel('Sentiment')
    plt.ylabel('Nombre')
    plt.savefig(os.path.join(CONFIG['output_dir'], filename), format=CONFIG['plot_format'])
    print ( f'saved at {os.path.join(CONFIG["output_dir"], filename)}')
    plt.close()

def main():
    # Loading
    data = load_data(CONFIG['data_path'])
    df_volontaire = data['Volontaire']
    # Preproscessing
    df_volontaire['cleaned_feedback'] = df_volontaire[CONFIG['text_column']].apply(preprocess_text)
    df_volontaire['sentiment'] = df_volontaire['cleaned_feedback'].apply(analyze_sentiment)
    # visualizations
    generate_word_cloud(df_volontaire['cleaned_feedback'], 'word_cloud.png')
    plot_sentiment_distribution(df_volontaire['sentiment'], 'sentiment_distribution.png')
    print('done analises')
    # Temporal analysis
    try:
        df_volontaire['date'] = pd.to_datetime(df_volontaire[CONFIG['date_column']]).dt.date
        sentiment_trends = df_volontaire.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
        sentiment_trends.plot(kind='bar', stacked=True, figsize=(12, 6))
        plt.title('Sentiment Trends Over Time')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(CONFIG['output_dir'], 'sentiment_trends.png'), format=CONFIG['plot_format'])
        plt.close()
    except KeyError:
        print(f"Warning: Date column '{CONFIG['date_column']}' not found - skipping temporal analysis")

    # Model training ( chnge the if 0 to if 1 or remoe if statement for this to work ) 
    if 0 :
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(df_volontaire['cleaned_feedback'])
        y = df_volontaire['sentiment'].map({'Positive': 1, 'Negative': -1, 'Neutral': 0})

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=CONFIG['test_size'], random_state=CONFIG['random_state']
        )

        models = {
            'Random Forest': RandomForestClassifier(),
            'Logistic Regression': LogisticRegression(max_iter=1000)
        }

        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            print(f"{name} Accuracy: {accuracy_score(y_test, y_pred):.2f}")
            print(classification_report(y_test, y_pred))

        # Save artifacts
        joblib.dump(models['Random Forest'], 'sentiment_analysis_model.pkl')
        joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
        df_volontaire.to_pickle('processed_volontaire_dataset.pkl')

if __name__ == '__main__':
    
    main()