import sqlite3, os

db = os.path.join('data', 'BDD', 'ekho.db')
if not os.path.exists(db):
    print('BD no existe todavia en:', db)
else:
    con = sqlite3.connect(db)
    rows = con.execute(
        'SELECT id_cancion, titulo, artista, album, duracion_seg, genero, '
        'plataforma_origen, url_origen, ruta_local, caratula_url, caratula_blob, letra, fecha_importacion '
        'FROM canciones ORDER BY fecha_importacion DESC'
    ).fetchall()
    if not rows:
        print('No hay canciones guardadas aun.')
    else:
        print(f'Total canciones: {len(rows)}\n')
        sep = '=' * 80
        for r in rows:
            (id_c, titulo, artista, album, dur, genero,
             plataforma, url_origen, ruta_local, caratula_url, caratula_blob, letra, fecha) = r

            # Formatear duracion
            if dur:
                mins, secs = divmod(int(dur), 60)
                dur_fmt = f"{mins}:{secs:02d}"
            else:
                dur_fmt = '-'

            # Formatear blob
            if caratula_blob:
                kb = len(caratula_blob) / 1024
                blob_fmt = f"(imagen embebida, {kb:.1f} KB)"
            else:
                blob_fmt = '-'

            print(sep)
            print(f"  ID               : {id_c}")
            print(f"  Titulo           : {titulo or '-'}")
            print(f"  Artista          : {artista or '-'}")
            print(f"  Album            : {album or '-'}")
            print(f"  Duracion         : {dur_fmt}")
            print(f"  Genero           : {genero or '-'}")
            print(f"  Plataforma       : {plataforma or '-'}")
            print(f"  URL origen       : {url_origen or '-'}")
            print(f"  Ruta local       : {ruta_local or '-'}")
            print(f"  Caratula URL     : {caratula_url or '-'}")
            print(f"  Caratula blob    : {blob_fmt}")
            print(f"  Letra            : {'(disponible)' if letra else '-'}")
            print(f"  Fecha importacion: {fecha or '-'}")
        print(sep)
    con.close()
