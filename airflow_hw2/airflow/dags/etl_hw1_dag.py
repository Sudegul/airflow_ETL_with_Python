from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import psycopg2
import os

# Task 1: extract_csv - CSV dosyasını oku ve veritabanına yaz
def extract_csv():
    csv_path = '/opt/airflow/backend/data/in_store_sales.csv'
    df = pd.read_csv(csv_path)

    conn = psycopg2.connect(
        host='db',
        dbname='airflowdb',
        user='airflowuser',
        password='airflowpass',
        port='5432'
    )
    cur = conn.cursor()

    cur.execute("""
        DROP TABLE IF EXISTS in_store_sales;
        CREATE TABLE in_store_sales (
            sale_id SERIAL PRIMARY KEY,
            product_id INT,
            quantity INT,
            sale_date DATE
        );
    """)

    for _, row in df.iterrows():
        cur.execute(
            "INSERT INTO in_store_sales (product_id, quantity, sale_date) VALUES (%s, %s, %s)",
            (int(row['product_id']), int(row['quantity']), row['sale_date'])
        )

    conn.commit()
    cur.close()
    conn.close()

# Task 2: extract_postgres - online_sales tablosundan veriyi çek
def extract_postgres():
    conn = psycopg2.connect(
        host='db',
        dbname='airflowdb',
        user='airflowuser',
        password='airflowpass',
        port='5432'
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM online_sales;")
    rows = cur.fetchall()
    with open('/tmp/online_sales.csv', 'w') as f:
        f.write('product_id,quantity\n')
        for row in rows:
            f.write(f"{row[1]},{row[2]}\n")
    cur.close()
    conn.close()

# Task 3: transform - CSV’den ve PostgreSQL’den alınan verileri işle
def transform():
    df_pg = pd.read_csv('/tmp/online_sales.csv')
    agg_df = df_pg.groupby('product_id')['quantity'].sum().reset_index()
    agg_df.to_csv('/tmp/aggregated_sales.csv', index=False)

# Task 4: load - transform sonucu veritabanına yaz
def load():
    df = pd.read_csv('/tmp/aggregated_sales.csv')
    conn = psycopg2.connect(
        host='db',
        dbname='airflowdb',
        user='airflowuser',
        password='airflowpass',
        port='5432'
    )
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS aggregated_sales;")
    cur.execute("""
        CREATE TABLE aggregated_sales (
            product_id INT,
            total_quantity INT
        );
    """)
    for _, row in df.iterrows():
        cur.execute(
            "INSERT INTO aggregated_sales (product_id, total_quantity) VALUES (%s, %s)",
            (int(row['product_id']), int(row['quantity']))
        )
    conn.commit()
    cur.close()
    conn.close()

# DAG tanımı
default_args = {
    'start_date': datetime(2024, 1, 1),
}

with DAG('sde_gul_etl',
         schedule_interval=None,
         catchup=False,
         default_args=default_args,
         description='HW1 + HW2 ETL pipeline by Sde Gül') as dag:

    task1 = PythonOperator(
        task_id='extract_csv',
        python_callable=extract_csv
    )

    task2 = PythonOperator(
        task_id='extract_postgres',
        python_callable=extract_postgres
    )

    task3 = PythonOperator(
        task_id='transform',
        python_callable=transform
    )

    task4 = PythonOperator(
        task_id='load',
        python_callable=load
    )

    [task1, task2] >> task3 >> task4
