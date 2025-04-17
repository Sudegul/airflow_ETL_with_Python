from flask import Flask, jsonify
import psycopg2
import os
import pandas as pd

app = Flask(__name__)

# Ortam değişkenlerinden bağlantı bilgilerini al
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'airflowdb')
DB_USER = os.environ.get('DB_USER', 'airflowuser')
DB_PASS = os.environ.get('DB_PASS', 'airflowpass')
DB_PORT = os.environ.get('DB_PORT', '5432')


@app.route('/api/data')
def get_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_table;")
        rows = cursor.fetchall()
        data = [{"id": r[0], "name": r[1]} for r in rows]
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/run_etl')
def run_etl():
    try:
        # CSV dosyasını oku
        csv_path = 'data/in_store_sales.csv'
        in_store_df = pd.read_csv(csv_path)

        # Veritabanına bağlan
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        cursor = conn.cursor()

        # Online satış verisini al
        cursor.execute("SELECT product_id, quantity FROM online_sales")
        online_rows = cursor.fetchall()
        online_df = pd.DataFrame(online_rows, columns=['product_id', 'quantity'])

        # Birleştir + Grupla
        combined_df = pd.concat([online_df, in_store_df])
        result_df = combined_df.groupby('product_id').sum().reset_index()

        # Tabloyu oluştur
        cursor.execute("""
            DROP TABLE IF EXISTS aggregated_sales;
            CREATE TABLE aggregated_sales (
                product_id INT,
                total_quantity INT
            );
        """)

        # Sonuçları tabloya yükle
        for _, row in result_df.iterrows():
            cursor.execute(
                "INSERT INTO aggregated_sales (product_id, total_quantity) VALUES (%s, %s)",
                (int(row['product_id']), int(row['quantity']))
            )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "ETL completed successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/aggregated_sales')
def get_aggregated_sales():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, total_quantity FROM aggregated_sales;")
        rows = cursor.fetchall()
        data = [{"product_id": r[0], "total_quantity": r[1]} for r in rows]
        cursor.close()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
