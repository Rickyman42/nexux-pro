# -*- coding: utf-8 -*-
"""Rellena los dias anteriores de la semana en la agenda del rodaje.

seed-agenda.mjs siembra UN dia. En la vista semanal del CRM eso deja cinco
columnas vacias al lado de la del sabado, y un anuncio que quiere decir "mira
todo lo que te gestiona" ensenando una agenda desierta dice lo contrario.

Se anaden citas de lunes a viernes (ya pasadas, asi que no compiten con el hueco
de las 18:00 del sabado) directamente en appointments.json. **No se suben a
Google Calendar**: el plano graba el CRM, que lee este fichero, y crear treinta
eventos mas en el calendario solo deja basura que limpiar.

Uso:  llena-semana.py            anade
      llena-semana.py --revertir deja solo las del sabado
"""
import json
import pathlib
import sys
from datetime import datetime, timedelta

CLIENTE = pathlib.Path('/home/nexux/nexux-clients/clients/'
                       'estudio-ricardo-demo-mostoles-946279')
APT = CLIENTE / 'appointments.json'

# Ni lleno ni vacio: un dia de trabajo normal, con la tarde mas cargada que la
# manana, que es como funciona un centro de estetica.
PLANTILLA = [
    ('09:30', 'Tratamiento facial',       'pro_marta',  'Marta',  60),
    ('10:00', 'Manicura',                 'pro_ana',    'Ana',    45),
    ('11:00', 'Depilación',               'pro_noelia', 'Noelia', 30),
    ('12:00', 'Tratamiento corporal',     'pro_lucia',  'Lucia',  75),
    ('16:00', 'Manicura',                 'pro_ana',    'Ana',    45),
    ('16:30', 'Masaje descontracturante', 'pro_marta',  'Marta',  60),
    ('17:30', 'Primera consulta',         'pro_noelia', 'Noelia', 30),
    ('18:00', 'Depilación',               'pro_lucia',  'Lucia',  30),
]

# Nombres distintos por dia para que no se repitan al mirar la semana entera
NOMBRES = {
    0: ['Marta Ibáñez', 'Cristina Roldán', 'Sofía Merino', 'Andrea Gil',
        'Patricia Luna', 'Elena Cortés', 'Raúl Vega', 'Nerea Ocaña'],
    1: ['Lucía Prats', 'Sara Espejo', 'Irene Blasco', 'Natalia Ruano',
        'Clara Bermejo', 'Miriam Toledo', 'Iván Serrano', 'Alba Reina'],
    2: ['Julia Nadal', 'Rocío Quintana', 'Belén Arroyo', 'Sandra Mena',
        'Teresa Valle', 'Ana Redondo', 'Óscar Pardo', 'Laura Cid'],
    3: ['Marina Bosch', 'Nuria Salas', 'Eva Montero', 'Carla Espín',
        'Rosa Delgado', 'Aitana Ferrer', 'Sergio Lara', 'Vega Morán'],
    4: ['Isabel Cano', 'Paula Riera', 'Lidia Fuentes', 'Amparo Gil',
        'Celia Navarro', 'Ángela Ruiz', 'Adrián Soto', 'Marta Bueno'],
}


def slug(s):
    import unicodedata
    n = unicodedata.normalize('NFD', s.lower())
    n = ''.join(c for c in n if unicodedata.category(c) != 'Mn')
    return 'svc_' + n.replace(' ', '_')


def main():
    citas = json.loads(APT.read_text(encoding='utf-8'))
    sabado = [c for c in citas if c['id'].startswith('rodaje-')
              or not c['id'].startswith('semana-')]

    if '--revertir' in sys.argv:
        quedan = [c for c in citas if not c['id'].startswith('semana-')]
        APT.write_text(json.dumps(quedan, indent=2, ensure_ascii=False), encoding='utf-8')
        print('quitadas %d citas de relleno, quedan %d' % (len(citas) - len(quedan), len(quedan)))
        return

    # El lunes de esta semana, a partir de la fecha de la primera cita sembrada
    ref = datetime.fromisoformat(sabado[0]['datetime'].replace('Z', '+00:00'))
    lunes = ref - timedelta(days=ref.weekday())

    ahora = datetime.utcnow().isoformat() + 'Z'
    nuevas = []
    for d in range(5):                       # lunes a viernes
        dia = (lunes + timedelta(days=d)).date().isoformat()
        for i, (hora, servicio, pro_id, pro, dur) in enumerate(PLANTILLA):
            # Madrid es UTC+2 en agosto: la hora local se guarda en Z restando 2
            utc = '%02d:%s' % (int(hora[:2]) - 2, hora[3:])
            nuevas.append({
                'id': 'semana-%d-%02d' % (d, i),
                'service_id': slug(servicio),
                'service': servicio,
                'professional_id': pro_id,
                'professional_name': pro,
                'assignment_mode': 'explicit',
                'resource_allocations': [],
                'client_name': NOMBRES[d][i],
                # sin client_phone: el numero se veria al abrir el evento
                'datetime': '%sT%s:00.000Z' % (dia, utc),
                'duration_min': dur,
                'status': 'confirmed',
                'source': 'crm',
                'source_event_id': '',
                'version': 1,
                'created_at': ahora,
                'updated_at': ahora,
                'reminder_24h_sent': False,
                'reminder_1h_sent': False,
            })

    todas = [c for c in citas if not c['id'].startswith('semana-')] + nuevas
    APT.write_text(json.dumps(todas, indent=2, ensure_ascii=False), encoding='utf-8')
    print('semana del %s' % lunes.date())
    print('  %d citas de relleno (lunes a viernes)' % len(nuevas))
    print('  %d citas en total' % len(todas))


if __name__ == '__main__':
    main()
