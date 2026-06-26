from pathlib import Path
import argparse
import pandas as pd
from src03_import import retrieve_safe

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / 'data' / 'results'
RESULTS.mkdir(parents=True, exist_ok=True)

def predict_outcome(query: str, k: int = 5) -> dict:
    top_k = retrieve_safe(query, k)
    # Weighted similarity: solusi kasus dengan skor similarity tertinggi dijadikan prediksi utama.
    best = top_k[0]
    return {
        'query': query,
        'predicted_case_id': best['case_id'],
        'predicted_solution': best['amar_putusan'],
        'top_5_case_ids': '|'.join([x['case_id'] for x in top_k]),
        'top_5_scores': '|'.join([str(x['similarity']) for x in top_k])
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', required=True)
    parser.add_argument('--k', type=int, default=5)
    args = parser.parse_args()
    pred = predict_outcome(args.query, args.k)
    pd.DataFrame([pred]).to_csv(RESULTS / 'predictions_manual.csv', index=False, encoding='utf-8-sig')
    print(pred)
