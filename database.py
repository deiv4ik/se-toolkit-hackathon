import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "innopolis_guide"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5433")
        )
        self.conn.autocommit = True

    def get_places(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM places ORDER BY id")
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

    def get_prompts(self, place_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT science_type, prompt_text FROM science_prompts WHERE place_id = %s", (place_id,))
            return {row[0]: row[1] for row in cur.fetchall()}

    def log_request(self, place_id, lat, lon):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO user_requests (place_id, latitude, longitude) VALUES (%s, %s, %s)",
                (place_id, lat, lon)
            )

    def get_popular_places(self, limit=5):
        with self.conn.cursor() as cur:
            # ИСПРАВЛЕНО: добавлены p.name в GROUP BY
            cur.execute("""
                SELECT p.place_id, p.name, count(ur.id) as request_count 
                FROM places p 
                LEFT JOIN user_requests ur ON p.place_id = ur.place_id 
                GROUP BY p.place_id, p.name 
                ORDER BY request_count DESC 
                LIMIT %s
            """, (limit,))
            
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
