import csv
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Material

csv_file = "eco_block_dataset.csv"  # 👈 your real data file

def import_data():
    db: Session = SessionLocal()
    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check if already imported (optional, based on 'material' + 'date_added')
                existing = db.query(Material).filter_by(
                    material=row["material"],
                    date_added=row["date_added"]
                ).first()
                if existing:
                    continue

                material = Material(
                    material=row["material"],
                    quantity=int(row["quantity"]),
                    source=row["source"],
                    carbon_savings=float(row["carbon_savings"]),
                    project_location=row["project_location"],
                    used_in_project=row["used_in_project"],
                    date_added=row["date_added"],
                    actual_usage=int(row["actual_usage"]) if row.get("actual_usage") else None
                )
                db.add(material)
            db.commit()
            print("✅ Data import complete.")
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_data()
