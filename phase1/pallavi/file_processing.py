import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime, TEXT
from sqlalchemy.exc import SQLAlchemyError

def list_files(directory_path):
    return [file for file in directory_path.iterdir() if file.is_file()]

def infer_table_schema(sample_chunk):
    columns = []
    for col_name in sample_chunk.columns:
        col_data = sample_chunk[col_name]
        if col_name in ['phone_number', 'whatsapp_number', 'alternate_phone_number']:
            columns.append(Column(col_name, String(150)))
        elif col_name in ['created_at_epoch', 'updated_at_epoch']:
            columns.append(Column(col_name, BigInteger))
        elif col_name in ['comment', 'latest_comment', 'metadata']:
            columns.append(Column(col_name, TEXT))
        elif pd.api.types.is_integer_dtype(col_data) and not col_data.isna().all():
            columns.append(Column(col_name, Integer))
        elif pd.api.types.is_float_dtype(col_data) and not col_data.isna().all():
            columns.append(Column(col_name, Float))
        elif pd.api.types.is_datetime64_any_dtype(col_data) and not col_data.isna().all():
            columns.append(Column(col_name, DateTime))
        else:
            columns.append(Column(col_name, String(255)))
    return columns

def load_file_to_db(engine, file_path, table_name):
    chunk_size = 15000
    for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
        try:
            chunk.to_sql(name=table_name, con=engine, if_exists='append', index=False)
            logging.info(f'Inserted chunk {i + 1} with {len(chunk)} rows into {table_name}')
        except SQLAlchemyError as e:
            logging.error(f"Error inserting data: {e}")
            raise

def check_directory_structure(directory_path):
    if not directory_path.is_dir():
        raise NotADirectoryError(f"{directory_path} is not a directory.")
    if not any(directory_path.iterdir()):
        raise FileNotFoundError(f"Directory '{directory_path}' is empty.")
