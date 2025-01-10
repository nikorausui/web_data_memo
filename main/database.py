import mysql.connector
import numpy as np

class DatabaseHandler:
    def __init__(self, config):
        self.config = config
        self.connection = self._initialize_database()

    def _initialize_database(self):
        # データベース接続
        try:
            connection = mysql.connector.connect(**self.config)
        except mysql.connector.errors.ProgrammingError as e:
            if "Unknown database" in str(e):
                # データベースが存在しない場合は作成
                self._create_database()
                connection = mysql.connector.connect(**self.config)
            else:
                raise e

        # テーブルが存在しない場合は作成
        self._create_table_if_not_exists(connection)
        return connection

    def _create_database(self):
        # データベース作成用の一時接続
        temp_config = self.config.copy()
        temp_config.pop("database")  # データベース名を一時的に削除
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE {self.config['database']}")
        cursor.close()
        connection.close()

    def _create_table_if_not_exists(self, connection):
        # 必要なテーブルを作成
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS web_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255) NOT NULL,
            summary TEXT NOT NULL,
            content LONGTEXT NOT NULL,
            embedding LONGBLOB NOT NULL
        );
        """
        cursor.execute(create_table_query)
        cursor.close()

    def insert_data(self, url, summary, content, embedding):
        cursor = self.connection.cursor()
        sql = """
            INSERT INTO web_data (url, summary, content, embedding)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (url, summary, content, embedding.tobytes()))
        self.connection.commit()
        cursor.close()

    def search_vectors(self, query_vector, top_k):
        cursor = self.connection.cursor(dictionary=True)
        sql = "SELECT id, url, summary, embedding FROM web_data"
        cursor.execute(sql)
        results = cursor.fetchall()

        data_with_distances = []
        for row in results:
            db_vector = np.frombuffer(row['embedding'], dtype=np.float32)
            distance = np.linalg.norm(query_vector - db_vector)
            data_with_distances.append({**row, "distance": distance})

        sorted_data = sorted(data_with_distances, key=lambda x: x['distance'])[:top_k]
        cursor.close()
        return sorted_data

    def get_data_list(self, page, limit):
        cursor = self.connection.cursor(dictionary=True)
        offset = (page - 1) * limit
        sql = "SELECT id, url, summary FROM web_data LIMIT %s OFFSET %s"
        cursor.execute(sql, (limit, offset))
        results = cursor.fetchall()
        cursor.close()
        return results

    def update_data(self, data_id, new_summary):
        cursor = self.connection.cursor()
        sql = "UPDATE web_data SET summary = %s WHERE id = %s"
        cursor.execute(sql, (new_summary, data_id))
        self.connection.commit()
        cursor.close()

    def delete_data(self, data_id):
        cursor = self.connection.cursor()
        sql = "DELETE FROM web_data WHERE id = %s"
        cursor.execute(sql, (data_id,))
        self.connection.commit()
        cursor.close()
