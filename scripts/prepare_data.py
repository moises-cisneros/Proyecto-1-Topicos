#!/usr/bin/env python3
"""
SMS Sentinel - Script de Particion Estratificada de Datos
Divide el dataset crudo en train (80%) y test (20%) con estratificacion y semilla fija 42.
Garantiza reproducibilidad determinista y aislamiento estricto del conjunto de prueba.
"""
import os
import pandas as pd
from sklearn.model_selection import train_test_split

RAW_DATA_PATH = "data/raw/sms_spanish.csv"
PROCESSED_DIR = "data/processed"
TRAIN_PATH = os.path.join(PROCESSED_DIR, "train.csv")
TEST_PATH = os.path.join(PROCESSED_DIR, "test.csv")

def prepare_splits(raw_path: str = RAW_DATA_PATH, random_state: int = 42, test_size: float = 0.2):
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"No se encontro el archivo crudo en: {raw_path}")

    print(f"[*] Cargando dataset desde {raw_path}...")
    df = pd.read_csv(raw_path)

    # Validaciones basicas de integridad
    if "label" not in df.columns or "text" not in df.columns:
        raise ValueError("El dataset debe contener las columnas 'label' y 'text'.")

    # Asegurar tipos y limpiar espacios
    df["label"] = df["label"].astype(str).str.strip().str.lower()
    df["text"] = df["text"].astype(str).str.strip()

    # Particion estratificada
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df["label"]
    )

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    train_df.to_csv(TRAIN_PATH, index=False, encoding="utf-8")
    test_df.to_csv(TEST_PATH, index=False, encoding="utf-8")

    print(f"[OK] Particiones generadas con exito (random_state={random_state}, test_size={test_size}):")
    print(f"     -> Train ({1-test_size:.0%}): {len(train_df)} filas")
    print(f"        Ham: {(train_df['label'] == 'ham').sum()} ({(train_df['label'] == 'ham').mean():.2%}) | Spam: {(train_df['label'] == 'spam').sum()} ({(train_df['label'] == 'spam').mean():.2%})")
    print(f"     -> Test  ({test_size:.0%}): {len(test_df)} filas")
    print(f"        Ham: {(test_df['label'] == 'ham').sum()} ({(test_df['label'] == 'ham').mean():.2%}) | Spam: {(test_df['label'] == 'spam').sum()} ({(test_df['label'] == 'spam').mean():.2%})")

    return train_df, test_df

if __name__ == "__main__":
    prepare_splits()
