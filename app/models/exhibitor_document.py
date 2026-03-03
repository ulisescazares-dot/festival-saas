from app.extensions import db

class ExhibitorDocument(db.Model):
    __tablename__ = "exhibitor_document"

    id = db.Column(db.Integer, primary_key=True)

    exhibitor_id = db.Column(
        db.Integer,
        db.ForeignKey("exhibitor.id"),
        nullable=False
    )

    file_path = db.Column(db.String(500), nullable=False)
    doc_type = db.Column(db.String(50))