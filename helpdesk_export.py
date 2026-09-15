# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────
#  PUENTE HELPDESK  ·  Grupo Pionier
#  Ejecuta el store y genera helpdesk.json para el dashboard.
#    - CASO 17 → KPIs, áreas, prioridad, responsables, tendencia, solicitantes
#    - CASO 2  → detalle de cada ticket (para el clic por trabajador)
#
#  REQUISITOS (una sola vez):
#    1. Instalar Python 3 (python.org → MARCAR "Add Python to PATH")
#       o desde Microsoft Store (escribe 'python' en la consola y se abre la Store)
#    2. En consola:  pip install pyodbc
#    3. Tener el "ODBC Driver 17 for SQL Server" (suele venir con SSMS)
#
#  USO:  python helpdesk_export.py
#  Correr desde tu PC en la red de la empresa (para alcanzar LIMDBS04).
# ─────────────────────────────────────────────────────────────
import pyodbc, json, datetime, decimal

SERVER   = 'LIMDBS04'
DATABASE = 'DBGP_PB'
OUT      = 'helpdesk.json'

def _ser(v):
    if isinstance(v, (datetime.datetime, datetime.date)): return v.isoformat()
    if isinstance(v, decimal.Decimal): return float(v)
    return v

def _rows(cur):
    cols = [c[0] for c in cur.description]
    return [{cols[i]: _ser(v) for i, v in enumerate(r)} for r in cur.fetchall()]

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + SERVER + ';DATABASE=' + DATABASE + ';Trusted_Connection=yes;')

# ---- CASO 17: los result sets del reporte gerencial ----
cur = conn.cursor()
cur.execute("EXEC [SP_SCRUM_HELPDESK_GESTION] @caso = 17")
sets = []
while True:
    if cur.description:
        sets.append(_rows(cur))
    if not cur.nextset():
        break

# ---- CASO 2: detalle de todos los tickets (con responsable) ----
cur2 = conn.cursor()
cur2.execute("EXEC [SP_SCRUM_HELPDESK_GESTION] @caso = 2, @Page = 1, @PageSize = 100000")
det = _rows(cur2) if cur2.description else []
tickets = [{
    'ticket':      t.get('NU_REQUEST'),
    'titulo':      t.get('NO_TITLE'),
    'responsable': t.get('NO_USR_RESPONSABLE'),
    'area':        t.get('AREA_ASIGNADA'),
    'subtipo':     t.get('NO_SUBTYPE'),
    'estado':      t.get('NO_STATUS'),
    'prioridad':   t.get('NO_PRIORITY'),
    'solicitante': t.get('SOLICITANTE'),
    'fecha':       (t.get('FE_REQUEST') or '')[:10]
} for t in det]

conn.close()

data = {
    'generado': datetime.datetime.now().strftime('%Y-%m-%d'),
    'rs1_kpis':         sets[0] if len(sets) > 0 else [],
    'rs2_area':         sets[1] if len(sets) > 1 else [],
    'rs3_prioridad':    sets[2] if len(sets) > 2 else [],
    'rs4_responsable':  sets[3] if len(sets) > 3 else [],
    'rs5_tendencia':    sets[4] if len(sets) > 4 else [],
    'rs6_solicitantes': sets[5] if len(sets) > 5 else [],
    'tickets':          tickets
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

print('OK -> ' + OUT)
print('Result sets:', [len(s) for s in sets], '| tickets:', len(tickets))
