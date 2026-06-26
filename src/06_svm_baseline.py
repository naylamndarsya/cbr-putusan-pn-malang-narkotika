from pathlib import Path
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report


PROJECT = Path(__file__).resolve().parents[1]
CASES_PATH = PROJECT / "data" / "processed" / "cases.csv"
EVAL_DIR = PROJECT / "data" / "eval"
EVAL_DIR.mkdir(parents=True, exist_ok=True)


def build_text(row):
    parts = [
        str(row.get("ringkasan_fakta", "")),
        str(row.get("argumen_hukum_utama", "")),
        str(row.get("text_full", "")),
    ]
    return " ".join(parts)


def main():
    df = pd.read_csv(CASES_PATH)

    df["model_text"] = df.apply(build_text, axis=1)
    df = df[df["model_text"].str.strip().str.len() > 0].copy()

    # Label yang dipakai untuk baseline klasifikasi.
    # Label ini dibuat dari pola perbuatan dalam putusan, misalnya:
    # jual_beli_perantara, memiliki_menyimpan_menguasai, lainnya.
    label_col = "label_perbuatan"

    if label_col not in df.columns:
        raise ValueError("Kolom label_perbuatan tidak ditemukan di cases.csv")

    df = df.dropna(subset=[label_col])
    X = df["model_text"]
    y = df[label_col]

    # Stratify dipakai agar distribusi label train-test tetap seimbang.
    # Jika data terlalu kecil untuk stratify, fallback ke split biasa.
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42,
            stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42
        )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            max_features=5000,
            ngram_range=(1, 2)
        )),
        ("svm", LinearSVC())
    ])

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    metrics = {
        "model": "TF-IDF + Linear SVM Baseline",
        "task": "classification baseline menggunakan label_perbuatan",
        "jumlah_data": len(df),
        "jumlah_train": len(X_train),
        "jumlah_test": len(X_test),
        "accuracy": accuracy_score(y_test, y_pred),
        "macro_precision": precision_score(y_test, y_pred, average="macro", zero_division=0),
        "macro_recall": recall_score(y_test, y_pred, average="macro", zero_division=0),
        "macro_f1": f1_score(y_test, y_pred, average="macro", zero_division=0),
        "weighted_precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
        "weighted_recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
        "weighted_f1": f1_score(y_test, y_pred, average="weighted", zero_division=0),
    }

    pd.DataFrame([metrics]).to_csv(
        EVAL_DIR / "svm_baseline_metrics.csv",
        index=False,
        encoding="utf-8-sig"
    )

    report = classification_report(
        y_test,
        y_pred,
        output_dict=True,
        zero_division=0
    )

    pd.DataFrame(report).transpose().to_csv(
        EVAL_DIR / "svm_classification_report.csv",
        encoding="utf-8-sig"
    )

    pred_df = pd.DataFrame({
        "text": X_test.values,
        "actual_label": y_test.values,
        "predicted_label": y_pred
    })

    pred_df.to_csv(
        EVAL_DIR / "svm_test_predictions.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("SVM baseline selesai.")
    print(pd.DataFrame([metrics]))


if __name__ == "__main__":
    main()