from app import db


class UploadHistory(db.Model):

    __tablename__ = "upload_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(300),
        nullable=False
    )

    rows_processed = db.Column(
        db.Integer,
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )