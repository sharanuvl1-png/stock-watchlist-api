import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_path='watchlist.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                company_name TEXT,
                sector TEXT,
                entry_price REAL,
                target_price REAL,
                stop_loss REAL,
                risk_reward_ratio TEXT,
                technical_signal TEXT,
                reasoning TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_stock(self, stock_data):
        """Add a new stock to the watchlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO stocks (symbol, company_name, sector, entry_price, 
                                  target_price, stop_loss, risk_reward_ratio,
                                  technical_signal, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock_data.get('symbol'),
                stock_data.get('company_name'),
                stock_data.get('sector'),
                stock_data.get('entry_price'),
                stock_data.get('target_price'),
                stock_data.get('stop_loss'),
                stock_data.get('risk_reward_ratio'),
                stock_data.get('technical_signal'),
                stock_data.get('reasoning')
            ))
            conn.commit()
            return {'success': True, 'message': 'Stock added successfully'}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': 'Stock already exists'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()
    
    def get_all_stocks(self):
        """Retrieve all stocks from watchlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM stocks WHERE status = "active" ORDER BY added_date DESC')
        columns = [description[0] for description in cursor.description]
        stocks = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return stocks
    
    def get_stock(self, symbol):
        """Retrieve a specific stock by symbol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM stocks WHERE symbol = ? AND status = "active"', (symbol,))
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(zip(columns, row))
        return None
    
    def update_stock(self, symbol, update_data):
        """Update stock information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values()) + [symbol]
        
        try:
            cursor.execute(f'UPDATE stocks SET {set_clause} WHERE symbol = ?', values)
            conn.commit()
            return {'success': True, 'message': 'Stock updated successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()
    
    def delete_stock(self, symbol):
        """Soft delete a stock (mark as inactive)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE stocks SET status = "inactive" WHERE symbol = ?', (symbol,))
            conn.commit()
            return {'success': True, 'message': 'Stock removed successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()
    
    def get_stocks_by_sector(self, sector):
        """Get all stocks in a specific sector"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM stocks WHERE sector = ? AND status = "active"', (sector,))
        columns = [description[0] for description in cursor.description]
        stocks = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return stocks
