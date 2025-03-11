from flask import Flask, jsonify, request, Response
from database import create_app, db
from models import User
import json

app = create_app()


# Rotte API CRUD

# 1. Recupera la lista di tutti gli utenti
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    # Formatta la lista degli utenti in JSON con chiavi esplicitamente ordinate
    users_json = json.dumps(
        [{"id": user.id, "name": user.name, "email": user.email} for user in users],
        ensure_ascii=False,
        indent=4
    )
    return Response(users_json, content_type='application/json; charset=utf-8'), 200


# 2. Recupera i dettagli di un utente specifico
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        # Restituisci i dati dell'utente in formato JSON
        user_json = json.dumps({"id": user.id, "name": user.name, "email": user.email}, ensure_ascii=False, indent=4)
        return Response(user_json, content_type='application/json; charset=utf-8'), 200
    return jsonify({"error": "Utente non trovato"}), 404


# 3. Crea un nuovo utente
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'name' not in data or 'email' not in data:
        return jsonify({"error": "Nome e email sono richiesti"}), 400

    # Creazione di un nuovo utente
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()

    # Restituzione della risposta con i dati dell'utente creato
    return jsonify({"message": "Utente creato con successo!", "data": new_user.to_dict()}), 201


# 4. Aggiorna un utente esistente
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Utente non trovato"}), 404

    data = request.get_json()
    # Modifica dei campi dell'utente
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']

    # Commit delle modifiche nel database
    db.session.commit()

    # Restituzione della risposta con l'utente aggiornato
    return jsonify({"message": "Utente aggiornato con successo!", "data": user.to_dict()}), 200


# 5. Elimina un utente
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Utente non trovato"}), 404

    db.session.delete(user)
    db.session.commit()

    # Restituzione della risposta di eliminazione con successo
    return jsonify({"message": "Utente eliminato con successo"}), 200


if __name__ == '__main__':
    app.run(debug=True)
