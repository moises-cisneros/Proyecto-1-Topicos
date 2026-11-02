#!/usr/bin/env python3
"""
SMS Sentinel - Pruebas Automatizadas de Integridad de Datos (tests/test_data_integrity.py)
Valida la consistencia estructural del dataset crudo y las particiones estratificadas train/test.
Garantiza ausencia de nulos, estricto etiquetado binario (ham/spam) y ratio 80/20 reproducible.
"""
import os
import pandas as pd
import pytest

RAW_DATA_PATH = "data/raw/sms_spanish.csv"
TRAIN_DATA_PATH = "data/processed/train.csv"
TEST_DATA_PATH = "data/processed/test.csv"

def test_raw_dataset_exists_and_populated():
    """Verifica que el dataset crudo exista y contenga el volumen minimo esperado."""
    assert os.path.exists(RAW_DATA_PATH), f"No existe el archivo crudo: {RAW_DATA_PATH}"
    df = pd.read_csv(RAW_DATA_PATH)
    assert len(df) >= 5000, f"Se esperaban al menos 5000 registros, encontrados: {len(df)}"

def test_raw_dataset_schema():
    """Verifica que el esquema contenga exactamente las columnas requeridas 'label' y 'text'."""
    df = pd.read_csv(RAW_DATA_PATH)
    expected_cols = {"label", "text"}
    assert set(df.columns) == expected_cols, f"Columnas esperadas: {expected_cols}, obtenidas: {set(df.columns)}"

def test_raw_dataset_no_nulls():
    """Verifica la ausencia total de valores nulos o vacios en el dataset crudo."""
    df = pd.read_csv(RAW_DATA_PATH)
    null_counts = df.isnull().sum()
    assert null_counts["label"] == 0, f"Existen {null_counts['label']} nulos en la columna 'label'"
    assert null_counts["text"] == 0, f"Existen {null_counts['text']} nulos en la columna 'text'"
    
    # Comprobar textos vacios tras strip
    empty_texts = df["text"].astype(str).str.strip().eq("").sum()
    assert empty_texts == 0, f"Se encontraron {empty_texts} textos en blanco"

def test_raw_dataset_labels_valid():
    """Verifica que las etiquetas sean exclusivamente binarias: 'ham' o 'spam'."""
    df = pd.read_csv(RAW_DATA_PATH)
    unique_labels = set(df["label"].unique())
    assert unique_labels == {"ham", "spam"}, f"Etiquetas invalidas detectadas: {unique_labels}"

def test_processed_splits_exist():
    """Verifica que los archivos particionados train.csv y test.csv existan."""
    assert os.path.exists(TRAIN_DATA_PATH), f"No existe el archivo de entrenamiento: {TRAIN_DATA_PATH}"
    assert os.path.exists(TEST_DATA_PATH), f"No existe el archivo de prueba: {TEST_DATA_PATH}"

def test_processed_splits_no_nulls():
    """Verifica que ni train ni test tengan valores nulos."""
    train_df = pd.read_csv(TRAIN_DATA_PATH)
    test_df = pd.read_csv(TEST_DATA_PATH)
    
    assert train_df.isnull().sum().sum() == 0, "Existen nulos en train.csv"
    assert test_df.isnull().sum().sum() == 0, "Existen nulos en test.csv"

def test_split_ratio_80_20():
    """Verifica que la particion cumpla exactamente con el 80% train y 20% test."""
    train_df = pd.read_csv(TRAIN_DATA_PATH)
    test_df = pd.read_csv(TEST_DATA_PATH)
    
    total = len(train_df) + len(test_df)
    test_ratio = len(test_df) / total
    train_ratio = len(train_df) / total
    
    # Tolerancia de +/- 0.5% debido a redondeo discreto
    assert 0.195 <= test_ratio <= 0.205, f"Ratio de test fuera de rango: {test_ratio:.4f}"
    assert 0.795 <= train_ratio <= 0.805, f"Ratio de train fuera de rango: {train_ratio:.4f}"

def test_stratification_balance():
    """Verifica que la proporcion de clases se mantenga consistente entre train y test."""
    train_df = pd.read_csv(TRAIN_DATA_PATH)
    test_df = pd.read_csv(TEST_DATA_PATH)
    
    train_spam_prop = (train_df["label"] == "spam").mean()
    test_spam_prop = (test_df["label"] == "spam").mean()
    
    diff = abs(train_spam_prop - test_spam_prop)
    # La diferencia entre ambas particiones estratificadas debe ser menor al 0.5%
    assert diff < 0.005, f"Diferencia de estratificacion excesiva: {diff:.4f} ({train_spam_prop:.4f} vs {test_spam_prop:.4f})"
