#!/usr/bin/env python
"""
Check Recs

Propósito:
- Herramienta de diagnóstico ligada a la aplicación principal.
- Instancia `Api()` como lo hace `app.py`, inspecciona la base de datos (tablas, conteos,
    muestras de `canciones`/`embeddings`/`historial`) y prueba el `RecommendationEngine`
    en el contexto de la aplicación.

Notas:
- No modifica la base de datos; solo realiza lecturas y llamadas al engine.
"""
import json
import os
import sys

# Asegurar que el root del proyecto está en sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api import Api


def main():
    api = Api()
    # Mostrar info de la base de datos usada por la API
    conn = api.db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cur.fetchall()]
        print('tables:', tables)

        for t in ('canciones','embeddings','historial_reproduccion'):
            try:
                cur.execute(f"SELECT COUNT(*) as c FROM {t}")
                print(f"{t}:", cur.fetchone()['c'])
            except Exception:
                print(f"{t}: (no existe)")

        print('\nSample canciones:')
        try:
            cur.execute('SELECT id_cancion, titulo, artista, ruta_local FROM canciones LIMIT 10')
            rows = cur.fetchall()
            for r in rows:
                print(dict(r))
        except Exception:
            print('(no se pudo leer canciones)')
    finally:
        conn.close()

    # Intentar obtener recomendaciones directamente
    print('\n--- Engine internals ---')
    try:
        engine = api._get_recommendation_engine()
        print('engine songs count:', len(getattr(engine, 'songs', [])))
        print('engine history count:', len(getattr(engine, 'history', [])))
        try:
            home = engine.generate_home_recommendations(top_k=8)
            print('generate_home_recommendations ->', len(home))
        except Exception as e:
            print('generate_home_recommendations error:', repr(e))
        try:
            pop = engine._rank_by_popularity(8, 'test')
            print('_rank_by_popularity ->', len(pop))
        except Exception as e:
            print('_rank_by_popularity error:', repr(e))
    except Exception as e:
        print('engine creation error:', repr(e))


if __name__ == '__main__':
    main()
