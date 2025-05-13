from flask import Flask, request, jsonify, Response, render_template_string
import json
from database import create_app, db
from models import Registrazione, User, Event

#per visualizzare la pagina html, avvii il server e url http://127.0.0.1:5000/vistaRegistrazioneEventi

app = create_app()


# Recupera la lista di tutte le registrazioni agli eventi
@app.route("/registrations", methods=["GET"])
def get_registrations():
    registrations = Registrazione.query.order_by(Registrazione.id).all()

    # Formatta la lista delle registrazioni i
    registrations_json = json.dumps(
        [
            {
                "id": reg.id,
                "user_id": reg.user_id,
                "event_id": reg.event_id,
                "data_registrazione": reg.data_registrazione.isoformat(),
            }
            for reg in registrations
        ],
        ensure_ascii=False,
        indent=4,
    )

    return Response(registrations_json, content_type="application/json; charset=utf-8"), 200


# Permette a un utente di registrarsi a un evento.

@app.route("/registrations", methods=["POST"])
def register_event():
    data = request.json

    # Controlla che i dati siano presenti
    if not data or "user_id" not in data or "event_id" not in data:
        return jsonify({"error": "Dati mancanti"}), 200

    # Verifica che l'utente e l'evento esistano
    user = User.query.get(data["user_id"])
    event = Event.query.get(data["event_id"])

   # if not user or not event:
    # return jsonify({"error": "Utente o evento non trovato"}), 404

    missing = []
    if not user:
        missing.append("l'utente")
    if not event:
        missing.append("l'evento")

    if missing:
        return jsonify({"message": f"Non esiste {' e '.join(missing)}"}), 200

    # Controlla se l'utente è già registrato all'evento
    existing_registration = Registrazione.query.filter_by(user_id=user.id, event_id=event.id).first()
    if existing_registration:
        return jsonify({"error": "L'utente è già registrato a questo evento"}), 200

    # Registra l'utente all'evento
    new_registration = Registrazione(user_id=user.id, event_id=event.id)
    db.session.add(new_registration)
    db.session.commit()

    return jsonify(new_registration.to_dict()), 201


# Permette a un utente di annullare la propria registrazione a un evento.
@app.route("/registrations/<int:user_id>/<int:event_id>", methods=["DELETE"])
def cancel_registration(user_id, event_id):
    registration = Registrazione.query.filter_by(user_id=user_id, event_id=event_id).first()

    if not registration:
        return jsonify({"message": "Registrazione già annullata o inesistente"}), 200


    db.session.delete(registration)
    db.session.commit()

    return jsonify({"message": "Registrazione annullata con successo"}), 200



# rotta pagina html
@app.route('/vistaRegistrazioneEventi')
def vista_registrazione_eventi():
    return render_template_string(open("vistaRegistrazioneEventi.html", encoding="utf-8").read())


if __name__ == "__main__":
    app.run(debug=True)
