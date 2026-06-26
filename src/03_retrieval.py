from pathlib import Path
import argparse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / 'data' / 'processed' / 'cases.csv'

def load_model():
    cases = pd.read_csv(DATA)
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1, max_df=0.95)
    X = vectorizer.fit_transform(cases['text_full'].fillna(''))
    return cases, vectorizer, X

def retrieve(query: str, k: int = 5):
    cases, vectorizer, X = load_model()
    qv = vectorizer.transform([query])
    sims = cosine_similarity(qv, X).ravel()
    order = sims.argsort()[::-1][:k]
    results = []
    for rank, idx in enumerate(order, start=1):
        row = cases.iloc[idx]
        results.append({
            'rank': rank,
            'case_id': row['case_id'],
            'no_perkara': row['no_perkara'],
            'pasal_utama': row.get('pasal_utama', ''),
            'similarity': round(float(sims[idx]), 4),
            'ringkasan_fakta': row.get('ringkasan_fakta', ''),
            'amar_putusan': row.get('amar_putusan', '')
        })
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', required=True)
    parser.add_argument('--k', type=int, default=5)
    args = parser.parse_args()
    for item in retrieve(args.query, args.k):
        print(item)
