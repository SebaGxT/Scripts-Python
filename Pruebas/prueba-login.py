from flask import Flask, render_template_string, request

app = Flask(__name__)

# Plantilla HTML con Bootstrap
login_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login Flask</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #74ebd5, #ACB6E5);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            width: 350px;
        }
        .login-box h2 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Iniciar Sesión</h2>
        <form method="POST">
            <div class="mb-3">
                <input type="text" class="form-control" name="usuario" placeholder="Usuario" required>
            </div>
            <div class="mb-3">
                <input type="password" class="form-control" name="password" placeholder="Contraseña" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Entrar</button>
        </form>
        {% if mensaje %}
            <div class="alert alert-info mt-3 text-center">{{ mensaje }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    mensaje = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        if usuario == "admin" and password == "1234":
            mensaje = f"✅ Bienvenido, {usuario}!"
        else:
            mensaje = "❌ Usuario o contraseña incorrectos"
    return render_template_string(login_html, mensaje=mensaje)

if __name__ == "__main__":
    app.run(debug=True)
