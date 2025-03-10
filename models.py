from database import db


# Definizione del modello User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


# Definizione del modello Event
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text, nullable=True)
    data = db.Column(db.DateTime, nullable=False)
    luogo = db.Column(db.String(150), nullable=False)


    def to_dict(self):
        return {
            "id": self.id,
            "titolo": self.titolo,
            "descrizione": self.descrizione,
            "data": self.data.isoformat(),
            "luogo": self.luogo,

        }




