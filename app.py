from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "pec2025"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def conectar_db():
    conexion = sqlite3.connect("ecoruta.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    return conexion, cursor


@app.route("/")
def index():
    return render_template("login/index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]
        conexion, cursor = conectar_db()

        cursor.execute("""
            SELECT * FROM usuario WHERE correo = ? AND password = ?
        """, (correo, password))

        usuario = cursor.fetchone()
        conexion.close()

        if usuario:
            session["id_usuario"] = usuario["id_usuario"]
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]

            if usuario["rol"] == "Administrador":
                return redirect(url_for("admin_panel"))
            return redirect(url_for("rol"))

        return redirect(url_for("login") + "?error=1")

    return render_template("login/login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]
        rol = request.form["rol"]

        conexion, cursor = conectar_db()

        cursor.execute("SELECT * FROM usuario WHERE correo = ?", (correo,))
        existente = cursor.fetchone()

        if existente:
            conexion.close()
            return redirect(url_for("registro") + "?error=1")

        cursor.execute("""
            INSERT INTO usuario (nombre, correo, password, rol)
            VALUES (?, ?, ?, ?)
        """, (nombre, correo, password, rol))

        conexion.commit()
        conexion.close()

        return redirect(url_for("registro") + "?ok=1")

    return render_template("login/registro.html")


@app.route("/rol")
def rol():
    if "id_usuario" not in session:
        return redirect(url_for("login"))
    return render_template("login/rol.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ==========================
# PANEL MAESTRO
# ==========================

@app.route("/maestros/panel")
def panel_maestro():
    if "id_usuario" not in session or session["rol"] != "Maestro":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()
    cursor.execute("SELECT * FROM maestro")
    maestros = cursor.fetchall()

    cursor.execute("SELECT * FROM actividad")
    actividades = cursor.fetchall()

    cursor.execute("SELECT * FROM evidencia")
    evidencias = cursor.fetchall()

    conexion.close()

    return render_template("maestros/panel.html",
                           maestros=maestros,
                           actividades=actividades,
                           evidencias=evidencias)


# ==========================
# RESPONSABLES
# ==========================

@app.route("/maestros/responsables", methods=["GET", "POST"])
def agregar_maestro():
    if "id_usuario" not in session or session["rol"] != "Maestro":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()

    if request.method == "POST":
        nombre = request.form["nombre"]
        cargo = request.form["cargo"]

        cursor.execute("""
            INSERT INTO maestro (nombre, cargo) VALUES (?, ?)
        """, (nombre, cargo))

        conexion.commit()
        conexion.close()
        return redirect(url_for("agregar_maestro") + "?ok=1")

    cursor.execute("SELECT * FROM maestro")
    maestros = cursor.fetchall()
    conexion.close()

    return render_template("maestros/agregar_maestro.html", maestros=maestros)


@app.route("/maestros/responsables/eliminar/<int:id>")
def eliminar_maestro(id):
    if "id_usuario" not in session or session["rol"] != "Maestro":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()
    cursor.execute("DELETE FROM maestro WHERE id_maestro = ?", (id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("agregar_maestro"))


# ==========================
# ACTIVIDADES MAESTRO
# ==========================

@app.route("/maestros/actividades", methods=["GET", "POST"])
def agregar_actividad():
    if "id_usuario" not in session or session["rol"] != "Maestro":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()

    if request.method == "POST":
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]

        cursor.execute("""
            INSERT INTO actividad (fecha_entrega, descripcion)
            VALUES (?, ?)
        """, (titulo, descripcion))

        conexion.commit()
        conexion.close()
        return redirect(url_for("agregar_actividad") + "?ok=1")

    cursor.execute("SELECT * FROM actividad")
    actividades = cursor.fetchall()
    conexion.close()

    return render_template("maestros/agregar_actividad.html", actividades=actividades)


# ==========================
# EVIDENCIAS MAESTRO
# ==========================

@app.route("/maestros/evidencias")
def ver_evidencias_maestro():
    if "id_usuario" not in session or session["rol"] != "Maestro":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()
    cursor.execute("SELECT * FROM evidencia")
    evidencias = cursor.fetchall()
    conexion.close()

    return render_template("maestros/agregar_evidencia.html", evidencias=evidencias)


# ==========================
# PANEL ALUMNO
# ==========================

@app.route("/alumnos/panel")
def panel_alumno():
    if "id_usuario" not in session or session["rol"] != "Alumno":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()
    cursor.execute("SELECT * FROM actividad")
    actividades = cursor.fetchall()

    cursor.execute("SELECT * FROM maestro")
    maestros = cursor.fetchall()

    cursor.execute("SELECT * FROM evidencia")
    evidencias = cursor.fetchall()

    conexion.close()

    return render_template("alumnos/panel.html",
                           actividades=actividades,
                           maestros=maestros,
                           evidencias=evidencias)


# ==========================
# ACTIVIDADES ALUMNO
# ==========================

@app.route("/alumnos/actividades")
def ver_actividades():
    if "id_usuario" not in session or session["rol"] != "Alumno":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()
    cursor.execute("SELECT * FROM actividad")
    actividades = cursor.fetchall()
    conexion.close()

    return render_template("alumnos/actividades.html", actividades=actividades)


@app.route("/alumnos/actividades/<int:id>")
def ver_actividad(id):

    if "id_usuario" not in session or session["rol"] != "Alumno":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()

    cursor.execute("""
        SELECT *
        FROM actividad
        WHERE id_actividad = ?
    """, (id,))

    actividad = cursor.fetchone()

    if actividad is None:
        conexion.close()
        return redirect(url_for("ver_actividades"))

    cursor.execute("""
        SELECT *
        FROM evidencia
        WHERE id_evidencia = ?
    """, (actividad["id_evidencia"],))

    evidencia = cursor.fetchone()

    conexion.close()

    return render_template(
        "alumnos/ver_actividad.html",
        actividad=actividad,
        evidencia=evidencia
    )

# ==========================
# EVIDENCIAS ALUMNO
# ==========================

@app.route("/alumnos/evidencias", methods=["GET", "POST"])
def ver_evidencias():
    if "id_usuario" not in session or session["rol"] != "Alumno":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()

    if request.method == "POST":
        titulo = request.form["titulo"]
        archivo = request.files["archivo"]

        if archivo:
            nombre_archivo = archivo.filename
            archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo))

            cursor.execute("""
                INSERT INTO evidencia (evidencia, fecha_evidencia)
                VALUES (?, ?)
            """, (nombre_archivo, titulo))

            conexion.commit()
            conexion.close()
            return redirect(url_for("ver_evidencias") + "?ok=1")

    cursor.execute("SELECT * FROM evidencia")
    evidencias = cursor.fetchall()
    conexion.close()

    return render_template("alumnos/evidencias.html", evidencias=evidencias)


@app.route("/alumnos/evidencias/editar/<int:id>", methods=["GET", "POST"])
def editar_evidencia(id):
    if "id_usuario" not in session or session["rol"] != "Alumno":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()

    if request.method == "POST":
        titulo = request.form["titulo"]
        archivo = request.files.get("archivo")

        if archivo and archivo.filename != "":
            nombre_archivo = archivo.filename
            archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo))
            cursor.execute("""
                UPDATE evidencia SET evidencia=?, fecha_evidencia=?
                WHERE id_evidencia=?
            """, (nombre_archivo, titulo, id))
        else:
            cursor.execute("""
                UPDATE evidencia SET fecha_evidencia=?
                WHERE id_evidencia=?
            """, (titulo, id))

        conexion.commit()
        conexion.close()
        return redirect(url_for("ver_evidencias") + "?ok=2")

    cursor.execute("SELECT * FROM evidencia WHERE id_evidencia=?", (id,))
    evidencia = cursor.fetchone()
    conexion.close()

    return render_template("alumnos/editar_evidencia.html", evidencia=evidencia)


@app.route("/alumnos/evidencias/eliminar/<int:id>")
def eliminar_evidencia(id):
    if "id_usuario" not in session or session["rol"] != "Alumno":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()
    cursor.execute("DELETE FROM evidencia WHERE id_evidencia=?", (id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("ver_evidencias"))


# ==========================
# ADMIN
# ==========================

@app.route("/admin/panel")
def admin_panel():
    if "id_usuario" not in session or session["rol"] != "Administrador":
        return redirect(url_for("login"))
    return render_template("admin/panel.html")


@app.route("/admin/usuarios", methods=["GET", "POST"])
def admin_usuarios():
    if "id_usuario" not in session or session["rol"] != "Administrador":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()

    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]
        rol = request.form["rol"]

        cursor.execute("""
            INSERT INTO usuario (nombre, correo, password, rol)
            VALUES (?, ?, ?, ?)
        """, (nombre, correo, password, rol))

        conexion.commit()

    cursor.execute("SELECT * FROM usuario")
    usuarios = cursor.fetchall()
    conexion.close()

    return render_template("admin/admin_usuarios.html", usuarios=usuarios)


@app.route("/admin/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    if "id_usuario" not in session or session["rol"] != "Administrador":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()

    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        rol = request.form["rol"]

        cursor.execute("""
            UPDATE usuario SET nombre=?, correo=?, rol=?
            WHERE id_usuario=?
        """, (nombre, correo, rol, id))

        conexion.commit()
        conexion.close()
        return redirect(url_for("admin_usuarios"))

    cursor.execute("SELECT * FROM usuario WHERE id_usuario=?", (id,))
    usuario = cursor.fetchone()
    conexion.close()

    return render_template("admin/editar_usuario.html", usuario=usuario)


@app.route("/admin/usuarios/eliminar/<int:id>")
def eliminar_usuario(id):
    if "id_usuario" not in session or session["rol"] != "Administrador":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()
    cursor.execute("DELETE FROM usuario WHERE id_usuario=?", (id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_usuarios"))


@app.route("/admin/sedes", methods=["GET", "POST"])
def admin_sedes():
    if "id_usuario" not in session or session["rol"] != "Administrador":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()

    if request.method == "POST":
        nombre    = request.form["nombre"]
        direccion = request.form.get("direccion", "")
        municipio = request.form.get("municipio", "")

        cursor.execute("""
            INSERT INTO sede (nombre, direccion, municipio) VALUES (?, ?, ?)
        """, (nombre, direccion, municipio))

        conexion.commit()
        conexion.close()
        return redirect(url_for("admin_sedes") + "?ok=1")

    cursor.execute("SELECT * FROM sede")
    sedes = cursor.fetchall()
    conexion.close()

    return render_template("admin/admin_sedes.html", sedes=sedes)


@app.route("/admin/sedes/eliminar/<int:id>")
def eliminar_sede(id):
    if "id_usuario" not in session or session["rol"] != "Administrador":
        return redirect(url_for("login"))

    conexion, cursor = conectar_db()
    cursor.execute("DELETE FROM sede WHERE id_sede = ?", (id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_sedes"))


if __name__ == "__main__":
    app.run(debug=True)