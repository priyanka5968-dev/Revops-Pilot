"""
Setup SQLite database with sample RevOps pipeline data
"""
import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = r"C:/Users/Priyanka Shah/OneDrive/Desktop/Cognizant/revops_pilot.db"

def setup_database():
    """Create schemas and sample data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Setting up database: {DB_PATH}")
    
    # Create schemas (SQLite doesn't have schemas, using prefixes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_hubspot_deals (
        deal_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        stage TEXT NOT NULL,
        owner TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_modified TIMESTAMP NOT NULL,
        source_system TEXT DEFAULT 'hubspot'
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_sheets_pipeline_sheet (
        pipeline_id TEXT PRIMARY KEY,
        deal_name TEXT NOT NULL,
        deal_amount REAL NOT NULL,
        current_stage TEXT NOT NULL,
        account_owner TEXT NOT NULL,
        created_date TIMESTAMP NOT NULL,
        updated_date TIMESTAMP NOT NULL,
        source_system TEXT DEFAULT 'sheets'
    )
    """)
    
    # Clear existing data
    cursor.execute("DELETE FROM raw_hubspot_deals")
    cursor.execute("DELETE FROM raw_sheets_pipeline_sheet")
    
    # Sample HubSpot deals
    hubspot_data = [
        ("HS-001", "Acme Corp Enterprise Deal", 450000, "proposal", "john.smith@acme.com", 
         datetime.now() - timedelta(days=45), datetime.now() - timedelta(days=2)),
        ("HS-002", "TechCorp Cloud Migration", 320000, "evaluation", "jane.doe@techcorp.com",
         datetime.now() - timedelta(days=30), datetime.now() - timedelta(days=1)),
        ("HS-003", "Global Industries Expansion", 550000, "closed_won", "mike.jones@global.com",
         datetime.now() - timedelta(days=60), datetime.now() - timedelta(days=5)),
        ("HS-004", "StartupX Series A", 150000, "closed_lost", "alice.wang@startupx.com",
         datetime.now() - timedelta(days=15), datetime.now() - timedelta(days=8)),
        ("HS-005", "DataFlow Analytics Platform", 280000, "qualification", "bob.chen@dataflow.com",
         datetime.now() - timedelta(days=20), datetime.now() - timedelta(days=3)),
    ]
    
    for deal in hubspot_data:
        cursor.execute("""
        INSERT INTO raw_hubspot_deals 
        (deal_id, name, amount, stage, owner, created_at, last_modified, source_system)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'hubspot')
        """, deal)
    
    # Sample Sheets data
    sheets_data = [
        ("SH-001", "Enterprise Solutions LLC", 400000, "proposal", "sarah.marketing@ent.com",
         datetime.now() - timedelta(days=40), datetime.now() - timedelta(days=1)),
        ("SH-002", "CloudFirst Consulting", 210000, "evaluation", "david.sales@cloudfirst.com",
         datetime.now() - timedelta(days=25), datetime.now() - timedelta(days=2)),
        ("SH-003", "SecureNet Security", 180000, "closed_won", "emily.account@securenet.com",
         datetime.now() - timedelta(days=50), datetime.now() - timedelta(days=10)),
        ("SH-004", "FinanceHub Pro", 320000, "qualification", "robert.dev@financehub.com",
         datetime.now() - timedelta(days=18), datetime.now() - timedelta(days=1)),
        ("SH-005", "HRFlow Automation", 95000, "closed_lost", "lisa.ops@hrflow.com",
         datetime.now() - timedelta(days=22), datetime.now() - timedelta(days=7)),
    ]
    
    for deal in sheets_data:
        cursor.execute("""
        INSERT INTO raw_sheets_pipeline_sheet 
        (pipeline_id, deal_name, deal_amount, current_stage, account_owner, created_date, updated_date, source_system)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'sheets')
        """, deal)
    
    conn.commit()
    
    # Verify data
    cursor.execute("SELECT COUNT(*) FROM raw_hubspot_deals")
    hs_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM raw_sheets_pipeline_sheet")
    sh_count = cursor.fetchone()[0]
    
    print(f"✓ Created {hs_count} HubSpot deals")
    print(f"✓ Created {sh_count} Sheets deals")
    print(f"✓ Database ready at: {DB_PATH}")
    
    conn.close()

if __name__ == "__main__":
    setup_database()
    print("\n✓ SQLite database setup complete!")
