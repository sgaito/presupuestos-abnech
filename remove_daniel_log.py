#!/usr/bin/env python3
"""
Script para eliminar por completo toda la funcionalidad del "log de Daniel"
de la aplicación: código en app.py, bloques en admin_usuarios.html y el
archivo log_daniel.txt. Ejecutar cuando se quiera dejar de registrar y
visualizar accesos de ese usuario (privacidad).

Uso: python remove_daniel_log.py
Requisito: ejecutar desde la raíz del proyecto (donde está app.py).
"""

import os
import sys

# Raíz del proyecto (donde está este script)
ROOT = os.path.dirname(os.path.abspath(__file__))
APP_PY = os.path.join(ROOT, 'app.py')
ADMIN_HTML = os.path.join(ROOT, 'templates', 'admin_usuarios.html')
LOG_FILE = os.path.join(ROOT, 'log_daniel.txt')


def main():
    if not os.path.isfile(APP_PY):
        print('Error: no se encuentra app.py en la raíz del proyecto.')
        sys.exit(1)

    changes = []

    # --- app.py ---
    with open(APP_PY, 'r', encoding='utf-8') as f:
        app_content = f.read()

    # 1) Constante + función append_daniel_log
    old1 = """# Log de accesos de Daniel (solo para Gaito: login y cada entrada a una sección)
DANIEL_LOG_FILE = 'log_daniel.txt'


def append_daniel_log(accion):
    \"\"\"Escribe una línea en el log de Daniel (solo visible para Gaito).\"\"\"
    try:
        ahora = datetime.now(ZoneInfo('America/Argentina/Buenos_Aires'))
        with open(DANIEL_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(ahora.strftime('%Y-%m-%d %H:%M:%S') + ' ' + accion + '\\n')
    except OSError:
        pass
# Archivo para almacenar perfiles de laboratorios"""
    if old1 in app_content:
        app_content = app_content.replace(old1, '# Archivo para almacenar perfiles de laboratorios')
        changes.append('app.py: eliminados DANIEL_LOG_FILE y append_daniel_log()')
    else:
        print('Advertencia: no se encontró el bloque DANIEL_LOG_FILE/append_daniel_log en app.py (¿ya eliminado?)')

    # 2) before_request log_daniel_navigation
    old2 = """
@app.before_request
def log_daniel_navigation():
    \"\"\"Registra cada vez que Daniel entra a una sección de la app (para que lo vea Gaito).\"\"\"
    if session.get('username') != 'DanielABNECH':
        return
    # Solo registrar peticiones GET a rutas de contenido (no estáticos ni favicon)
    if request.method != 'GET':
        return
    path = request.path or ''
    if path.startswith('/static') or path == '/favicon.ico':
        return
    # Descripción legible de la ruta para el log
    if path in ('', '/') or path.startswith('/login'):
        accion = 'Entrada: /login'
    else:
        accion = 'Entrada: ' + path
    append_daniel_log(accion)

# Crear carpeta de logos"""
    if old2 in app_content:
        app_content = app_content.replace(old2, '\n# Crear carpeta de logos')
        changes.append('app.py: eliminado before_request log_daniel_navigation')
    else:
        print('Advertencia: no se encontró log_daniel_navigation en app.py')

    # 3) En login: if username == 'DanielABNECH' y append_daniel_log
    old3 = """                logger.info(f"Usuario {username} inició sesión")
                if username == 'DanielABNECH':
                    append_daniel_log('Login')
                flash(f'¡Bienvenido, {username}!', 'success')"""
    new3 = """                logger.info(f"Usuario {username} inició sesión")
                flash(f'¡Bienvenido, {username}!', 'success')"""
    if old3 in app_content:
        app_content = app_content.replace(old3, new3)
        changes.append('app.py: eliminado registro de login de Daniel en login()')
    else:
        print('Advertencia: no se encontró el bloque append_daniel_log en login')

    # 4) En admin_usuarios: bloque daniel_log_lines y variable en return
    old4 = """    # Obtener precio de Particular para mostrar en el template
    precio_particular = get_precio_particular()
    
    # Log Daniel (solo para ver desde el panel, temporal)
    daniel_log_lines = []
    if os.path.isfile(DANIEL_LOG_FILE):
        try:
            with open(DANIEL_LOG_FILE, 'r', encoding='utf-8') as f:
                daniel_log_lines = f.read().strip().split('\\n')[-50:]  # últimas 50
        except OSError:
            pass
    
    return render_template('admin_usuarios.html', 
                         users=users, 
                         current_user=session.get('username'),
                         obras_sin_cobertura_anexo=anexo_config.get('obras_sin_cobertura', []),
                         todas_las_obras=todas_las_obras,
                         precio_particular=precio_particular,
                         daniel_log_lines=daniel_log_lines)"""
    new4 = """    # Obtener precio de Particular para mostrar en el template
    precio_particular = get_precio_particular()
    
    return render_template('admin_usuarios.html', 
                         users=users, 
                         current_user=session.get('username'),
                         obras_sin_cobertura_anexo=anexo_config.get('obras_sin_cobertura', []),
                         todas_las_obras=todas_las_obras,
                         precio_particular=precio_particular)"""
    if old4 in app_content:
        app_content = app_content.replace(old4, new4)
        changes.append('app.py: eliminada carga y paso de daniel_log_lines en admin_usuarios()')
    else:
        print('Advertencia: no se encontró el bloque daniel_log_lines en admin_usuarios')

    # 5) Rutas admin_daniel_log_content y admin_daniel_log_clear
    old5 = """

@app.route('/admin/daniel_log', methods=['GET'])
@require_login
def admin_daniel_log_content():
    \"\"\"Devuelve las últimas líneas del log de Daniel (solo Gaito). Para actualización en vivo.\"\"\"
    if not is_gaito_admin():
        return jsonify({'success': False, 'lines': []}), 403
    lines = []
    if os.path.isfile(DANIEL_LOG_FILE):
        try:
            with open(DANIEL_LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split('\\n')[-50:]
        except OSError:
            pass
    return jsonify({'success': True, 'lines': lines})


@app.route('/admin/daniel_log/clear', methods=['POST'])
@require_login
def admin_daniel_log_clear():
    \"\"\"Vacía el log de Daniel. Solo Gaito.\"\"\"
    if not is_gaito_admin():
        return jsonify({'success': False, 'message': 'Sin permiso.'}), 403
    try:
        with open(DANIEL_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write('')
        return jsonify({'success': True})
    except OSError:
        return jsonify({'success': False, 'message': 'No se pudo vaciar el archivo.'}), 500


# Ruta para obtener preview de precios"""
    new5 = """

# Ruta para obtener preview de precios"""
    if old5 in app_content:
        app_content = app_content.replace(old5, new5)
        changes.append('app.py: eliminadas rutas /admin/daniel_log y /admin/daniel_log/clear')
    else:
        print('Advertencia: no se encontraron las rutas admin daniel_log en app.py')

    with open(APP_PY, 'w', encoding='utf-8') as f:
        f.write(app_content)

    # --- templates/admin_usuarios.html ---
    if os.path.isfile(ADMIN_HTML):
        with open(ADMIN_HTML, 'r', encoding='utf-8') as f:
            admin_content = f.read()

        # Card Log Daniel
        old_card = """            {% if current_user == 'Gaito' and daniel_log_lines is defined %}
            <div class="admin-card">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <h2 style="margin:0;">Log Daniel</h2>
                    <button type="button" id="btn-vaciar-log-daniel" class="admin-btn admin-btn-secondary admin-btn-sm" title="Vaciar el registro">Vaciar log</button>
                </div>
                <pre id="log-daniel-content" style="margin:0; font-size:0.85rem; max-height:200px; overflow:auto;">{% for line in daniel_log_lines %}{{ line }}{{ '\\n' }}{% endfor %}{% if not daniel_log_lines %}— vacío —{% endif %}</pre>
            </div>
            {% endif %}

            """
        if old_card in admin_content:
            admin_content = admin_content.replace(old_card, '            \n')
            changes.append('admin_usuarios.html: eliminada tarjeta "Log Daniel"')
        else:
            print('Advertencia: no se encontró la tarjeta Log Daniel en admin_usuarios.html')

        # JS: botón vaciar log + polling en vivo
        old_js = """        var btnVaciarLog = document.getElementById('btn-vaciar-log-daniel');
        if (btnVaciarLog) {
            btnVaciarLog.addEventListener('click', function() {
                if (!confirm('¿Vaciar el log de Daniel? Se borrará todo el registro.')) return;
                fetch('{{ url_for("admin_daniel_log_clear") }}', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: 'csrf_token={{ csrf_token() }}'
                }).then(function(r) { return r.json(); }).then(function(d) {
                    if (d.success) {
                        var pre = document.getElementById('log-daniel-content');
                        if (pre) pre.textContent = '— vacío —';
                    } else alert('Error: ' + (d.message || 'No se pudo vaciar'));
                }).catch(function() { alert('Error de conexión'); });
            });
        }
        (function logDanielLive() {
            var pre = document.getElementById('log-daniel-content');
            if (!pre) return;
            function updateLog() {
                fetch('{{ url_for("admin_daniel_log_content") }}')
                    .then(function(r) { return r.json(); })
                    .then(function(d) {
                        if (!d.success) return;
                        var atBottom = pre.scrollHeight - pre.scrollTop <= pre.clientHeight + 2;
                        pre.textContent = d.lines && d.lines.length ? d.lines.join('\\n') + '\\n' : '— vacío —';
                        if (atBottom) pre.scrollTop = pre.scrollHeight;
                    })
                    .catch(function() {});
            }
            setInterval(updateLog, 4000);
        })();
"""
        if old_js in admin_content:
            admin_content = admin_content.replace(old_js, '')
            changes.append('admin_usuarios.html: eliminado JS del log (vaciar + actualización en vivo)')
        else:
            print('Advertencia: no se encontró el bloque JS del log en admin_usuarios.html')

        with open(ADMIN_HTML, 'w', encoding='utf-8') as f:
            f.write(admin_content)
    else:
        print('Advertencia: no se encuentra templates/admin_usuarios.html')

    # --- Borrar archivo log_daniel.txt ---
    if os.path.isfile(LOG_FILE):
        try:
            os.remove(LOG_FILE)
            changes.append('Eliminado archivo log_daniel.txt')
        except OSError as e:
            print(f'Error al eliminar log_daniel.txt: {e}')
    else:
        changes.append('No existía log_daniel.txt (nada que borrar)')

    # Resumen
    print('--- Resumen ---')
    for c in changes:
        print('  •', c)
    print('Listo. Toda la funcionalidad del log de Daniel ha sido removida.')


if __name__ == '__main__':
    main()
