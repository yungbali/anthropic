import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='database.log'
)

class DatabaseManager:
    def __init__(self, db_name: str = 'payments.db'):
        self.db_name = db_name
        self.create_payment_table()

    def get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Create and return a database connection and cursor"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def create_payment_table(self) -> None:
        """Create the payments table if it doesn't exist"""
        try:
            conn, c = self.get_connection()
            c.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    reference TEXT UNIQUE NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    plan_type TEXT NOT NULL
                )
            ''')
            conn.commit()
            logging.info("Payment table created successfully")
        except sqlite3.Error as e:
            logging.error(f"Error creating payment table: {e}")
            raise
        finally:
            conn.close()

    def store_payment(self, 
                     email: str, 
                     reference: str, 
                     amount: float, 
                     status: str,
                     plan_type: str,
                     expires_at: datetime) -> bool:
        """Store a new payment record"""
        try:
            conn, c = self.get_connection()
            c.execute('''
                INSERT INTO payments 
                (email, reference, amount, status, plan_type, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, reference, amount, status, plan_type, expires_at))
            conn.commit()
            logging.info(f"Payment stored successfully for {email}")
            return True
        except sqlite3.IntegrityError:
            logging.warning(f"Duplicate payment reference: {reference}")
            return False
        except sqlite3.Error as e:
            logging.error(f"Error storing payment: {e}")
            return False
        finally:
            conn.close()

    def update_payment_status(self, reference: str, status: str) -> bool:
        """Update the status of a payment"""
        try:
            conn, c = self.get_connection()
            c.execute('''
                UPDATE payments 
                SET status = ? 
                WHERE reference = ?
            ''', (status, reference))
            conn.commit()
            logging.info(f"Payment status updated for reference: {reference}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error updating payment status: {e}")
            return False
        finally:
            conn.close()

    def get_payment_status(self, email: str) -> Optional[Dict]:
        """Get the latest payment status for a user"""
        try:
            conn, c = self.get_connection()
            c.execute('''
                SELECT status, expires_at, plan_type 
                FROM payments 
                WHERE email = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (email,))
            result = c.fetchone()
            if result:
                return {
                    "status": result[0],
                    "expires_at": result[1],
                    "plan_type": result[2]
                }
            return None
        except sqlite3.Error as e:
            logging.error(f"Error getting payment status: {e}")
            return None
        finally:
            conn.close()

    def check_active_subscription(self, email: str) -> bool:
        """Check if user has an active subscription"""
        try:
            conn, c = self.get_connection()
            c.execute('''
                SELECT COUNT(*) 
                FROM payments 
                WHERE email = ? 
                AND status = 'success' 
                AND expires_at > datetime('now')
            ''', (email,))
            result = c.fetchone()
            return result[0] > 0
        except sqlite3.Error as e:
            logging.error(f"Error checking subscription: {e}")
            return False
        finally:
            conn.close()

    def get_payment_history(self, email: str) -> List[Dict]:
        """Get payment history for a user"""
        try:
            conn, c = self.get_connection()
            c.execute('''
                SELECT reference, amount, status, created_at, plan_type, expires_at 
                FROM payments 
                WHERE email = ? 
                ORDER BY created_at DESC
            ''', (email,))
            results = c.fetchall()
            return [{
                "reference": row[0],
                "amount": row[1],
                "status": row[2],
                "created_at": row[3],
                "plan_type": row[4],
                "expires_at": row[5]
            } for row in results]
        except sqlite3.Error as e:
            logging.error(f"Error getting payment history: {e}")
            return []
        finally:
            conn.close()

    def cleanup_expired_payments(self) -> None:
        """Clean up expired payment records"""
        try:
            conn, c = self.get_connection()
            c.execute('''
                DELETE FROM payments 
                WHERE expires_at < datetime('now', '-30 days')
            ''')
            conn.commit()
            logging.info("Expired payments cleaned up")
        except sqlite3.Error as e:
            logging.error(f"Error cleaning up payments: {e}")
        finally:
            conn.close()

# Usage example
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    
    # Example usage
    try:
        # Store a new payment
        db.store_payment(
            email="test@example.com",
            reference="PAY123",
            amount=50.00,
            status="pending",
            plan_type="monthly",
            expires_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Check subscription status
        is_active = db.check_active_subscription("test@example.com")
        print(f"Subscription active: {is_active}")
        
        # Get payment history
        history = db.get_payment_history("test@example.com")
        print(f"Payment history: {history}")
        
    except Exception as e:
        print(f"Error: {e}")