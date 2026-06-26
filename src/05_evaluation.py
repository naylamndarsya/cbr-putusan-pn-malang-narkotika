from pathlib import Path
import json
import pandas as pd
from src03_import import retrieve_safe

PROJECT = Path(__file__).resolve().parents[1]
EVAL = PROJECT / 'data' / 'eval'
RESULTS = PROJECT / 'data' / 'results'
EVAL.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

def eval_retrieval(k: int = 5):
    queries = json.loads((EVAL / 'queries.json').read_text(encoding='utf-8'))
    rows = []
    predictions = []
    for q in queries:
        top = retrieve_safe(q['query'], k)
        top_ids = [x['case_id'] for x in top]
        scores = [x['similarity'] for x in top]
        gt = q['ground_truth_case_id']
        hit = gt in top_ids
        top1 = top_ids[0] == gt
        precision_at_k = 1 / k if hit else 0.0
        recall_at_k = 1.0 if hit else 0.0
        f1_at_k = (2 * precision_at_k * recall_at_k / (precision_at_k + recall_at_k)) if hit else 0.0
        rows.append({
            'query_id': q['query_id'],
            'ground_truth_case_id': gt,
            'top_1_case_id': top_ids[0],
            'top_5_case_ids': '|'.join(top_ids),
            'top_5_scores': '|'.join(map(str, scores)),
            'hit_at_5': int(hit),
            'top1_correct': int(top1),
            'precision_at_5': precision_at_k,
            'recall_at_5': recall_at_k,
            'f1_at_5': f1_at_k,
        })
        predictions.append({
            'query_id': q['query_id'],
            'query': q['query'],
            'ground_truth_case_id': gt,
            'predicted_case_id': top_ids[0],
            'predicted_solution': top[0]['amar_putusan'],
            'top_5_case_ids': '|'.join(top_ids),
            'top_5_scores': '|'.join(map(str, scores))
        })
    df = pd.DataFrame(rows)
    df.to_csv(EVAL / 'retrieval_metrics.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(predictions).to_csv(RESULTS / 'predictions.csv', index=False, encoding='utf-8-sig')
    summary = pd.DataFrame([{
        'model': 'TF-IDF + Cosine Similarity',
        'jumlah_query': len(df),
        'top1_accuracy': df['top1_correct'].mean(),
        'hit_at_5_accuracy': df['hit_at_5'].mean(),
        'macro_precision_at_5': df['precision_at_5'].mean(),
        'macro_recall_at_5': df['recall_at_5'].mean(),
        'macro_f1_at_5': df['f1_at_5'].mean()
    }])
    summary.to_csv(EVAL / 'prediction_metrics.csv', index=False, encoding='utf-8-sig')
    return df, summary

if __name__ == '__main__':
    detail, summary = eval_retrieval(k=5)
    print(detail)
    print(summary)
