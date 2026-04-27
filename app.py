from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'segredo'

def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))

def criar_tabelas():
    db = get_db()
    cursor = db.cursor()

    # Tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    ''')

    # Tabela de itens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        codigo TEXT,
        nome TEXT,
        quantidade INTEGER,
        estoque_minimo INTEGER,
        quantidade_compra INTEGER
    )
    ''')

    db.commit()
    db.close()

criar_tabelas()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (user, pwd))
        result = cursor.fetchone()

        if result:
            session['user'] = user
            return redirect('/dashboard')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, pwd))
        db.commit()

        return redirect('/')

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    return render_template('dashboard.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        minimo = request.form['minimo']
        compra = request.form['compra']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
        INSERT INTO items (codigo, nome, quantidade, estoque_minimo, quantidade_compra)
        VALUES (%s, %s, %s, %s, %s)
        """, (codigo, nome, quantidade, minimo, compra))

        db.commit()
        return redirect('/dashboard')

    return render_template('add_item.html')

@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        codigo = request.form['codigo']
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        minimo = request.form['minimo']
        compra = request.form['compra']

        cursor.execute("""
        UPDATE items
        SET codigo=%s, nome=%s, quantidade=%s, estoque_minimo=%s, quantidade_compra=%s
        WHERE id=%s
        """, (codigo, nome, quantidade, minimo, compra, id))

        db.commit()
        return redirect('/dashboard')

    cursor.execute("SELECT * FROM items WHERE id=%s", (id,))
    item = cursor.fetchone()

    return render_template('edit_item.html', item=item)

@app.route('/entrada/<int:id>', methods=['GET', 'POST'])
def entrada(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        valor = int(request.form['valor'])

        cursor.execute("""
        UPDATE items
        SET quantidade = quantidade + %s
        WHERE id=%s
        """, (valor, id))

        db.commit()
        return redirect('/dashboard')

    return render_template('entrada.html', id=id)

@app.route('/delete_item/<int:id>')
def delete_item(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM items WHERE id=%s", (id,))
    db.commit()

    return redirect('/dashboard')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)