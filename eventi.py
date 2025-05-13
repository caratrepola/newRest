import os
from flask import Flask, request, jsonify, Response,  render_template_string
from models import Registrazione, Event
from database import create_app, db
from datetime import datetime
import json

#per visualizzare la pagina html, avvii il server e url http://127.0.0.1:5000/vistaEventi
app = create_app()


# Rotta per ottenere tutti gli eventi
@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    events_json = json.dumps([event.to_dict() for event in events], ensure_ascii=False, indent=4)
    return Response(events_json, content_type='application/json; charset=utf-8'), 200


# Rotta per ottenere un evento specifico
@app.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get(event_id)
    if event:
        event_json = json.dumps(event.to_dict(), ensure_ascii=False, indent=4)
        return Response(event_json, content_type='application/json; charset=utf-8'), 200
    return jsonify({'error': 'Evento non trovato'}), 404


# Rotta per creare un nuovo evento
@app.route('/events', methods=['POST'])
def create_event():
    data = request.json
    if not data or 'titolo' not in data or 'data' not in data or 'luogo' not in data:
        return jsonify({'error': 'Dati mancanti o non validi'}), 400

    try:
        # Converte la stringa della data in un oggetto datetime
        event_data = datetime.fromisoformat(data['data'])
    except ValueError:
        return jsonify({'error': 'Formato data non valido'}), 400

    # 🔍 Controllo evento duplicato
    existing_event = Event.query.filter_by(titolo=data['titolo'], data=event_data, luogo=data['luogo']).first()
    if existing_event:
        return jsonify({"message": "Evento già esistente", "data": existing_event.to_dict()}), 200

    new_event = Event(
        titolo=data['titolo'],
        descrizione=data.get('descrizione', ''),  # Campo opzionale
        data=event_data,
        luogo=data['luogo']
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify({'message': 'Evento creato con successo!', 'data': new_event.to_dict()}), 201


# Rotta per modificare un evento esistente
@app.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Evento non trovato'}), 404

    data = request.json
    if 'titolo' in data:
        event.titolo = data['titolo']
    if 'descrizione' in data:
        event.descrizione = data['descrizione']
    if 'data' in data:
        try:
            event.data = datetime.fromisoformat(data['data'])
        except ValueError:
            return jsonify({'error': 'Formato data non valido. Usa il formato ISO (YYYY-MM-DDTHH:MM:SS)'}), 400
    if 'luogo' in data:
        event.luogo = data['luogo']

    db.session.commit()
    return jsonify({'message': 'Evento aggiornato con successo!', 'data': event.to_dict()}), 200


# Rotta per eliminare un evento
@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({"message": "Evento già eliminato o non esistente"}), 200

        # Prima di eliminare l'evento, rimuoviamo tutte le registrazioni collegate
        Registrazione.query.filter_by(event_id=event_id).delete()

        db.session.delete(event)
        db.session.commit()

        return jsonify({'message': 'Evento eliminato con successo'}), 200

    except Exception as e:
        db.session.rollback()  # Annulla eventuali modifiche al database in caso di errore
        return jsonify({'error': f'Errore del server: {str(e)}'}), 500

# rotta pagina html
@app.route('/vistaEventi')
def vista_eventi():
    return render_template_string(open("vistaEventi.html", encoding="utf-8").read())

if __name__ == '__main__':
    app.run(debug=True)
