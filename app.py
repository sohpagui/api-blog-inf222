from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import hashlib
from flask_cors import CORS

app = Flask(__name__)

# Configuration MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'pascal'
app.config['MYSQL_PASSWORD'] = 'Root@1234'
app.config['MYSQL_DB'] = 'blog_db'

# Configuration JWT
app.config['JWT_SECRET_KEY'] = 'inf222-blog-secret-key'
CORS(app)
mysql = MySQL(app)
jwt = JWTManager(app)

# ─── AUTH ────────────────────────────────────────
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('nom') or not data.get('email') or not data.get('mot_de_passe'):
        return jsonify({"message": "Nom, email et mot de passe obligatoires"}), 400
    nom = data['nom']
    email = data['email']
    mot_de_passe = hashlib.sha256(data['mot_de_passe'].encode()).hexdigest()
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO utilisateurs (nom, email, mot_de_passe) VALUES (%s, %s, %s)",
                    (nom, email, mot_de_passe))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Utilisateur créé avec succès"}), 201
    except Exception as e:
        return jsonify({"message": "Email déjà utilisé"}), 400

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('mot_de_passe'):
        return jsonify({"message": "Email et mot de passe obligatoires"}), 400
    email = data['email']
    mot_de_passe = hashlib.sha256(data['mot_de_passe'].encode()).hexdigest()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM utilisateurs WHERE email=%s AND mot_de_passe=%s",
                (email, mot_de_passe))
    user = cur.fetchone()
    cur.close()
    if user:
        token = create_access_token(identity=str(user[0]))
        return jsonify({"token": token}), 200
    return jsonify({"message": "Identifiants incorrects"}), 401

# ─── ARTICLES ────────────────────────────────────
@app.route('/api/articles', methods=['GET'])
def get_articles():
    categorie = request.args.get('categorie')
    auteur = request.args.get('auteur')
    date = request.args.get('date')
    cur = mysql.connection.cursor()
    query = "SELECT * FROM articles WHERE 1=1"
    params = []
    if categorie:
        query += " AND categorie=%s"
        params.append(categorie)
    if auteur:
        query += " AND auteur=%s"
        params.append(auteur)
    if date:
        query += " AND DATE(date_creation)=%s"
        params.append(date)
    cur.execute(query, params)
    articles = cur.fetchall()
    cur.close()
    result = [{"id": a[0], "titre": a[1], "contenu": a[2],
               "auteur_id": a[3], "auteur": a[4],
               "date_creation": str(a[5]), "categorie": a[6], "tags": a[7]}
              for a in articles]
    return jsonify(result), 200

@app.route('/api/articles/search', methods=['GET'])
def search_articles():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"message": "Paramètre query obligatoire"}), 400
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles WHERE titre LIKE %s OR contenu LIKE %s",
                (f'%{query}%', f'%{query}%'))
    articles = cur.fetchall()
    cur.close()
    result = [{"id": a[0], "titre": a[1], "contenu": a[2],
               "auteur_id": a[3], "auteur": a[4],
               "date_creation": str(a[5]), "categorie": a[6], "tags": a[7]}
              for a in articles]
    return jsonify(result), 200

@app.route('/api/articles/<int:id>', methods=['GET'])
def get_article(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles WHERE id=%s", (id,))
    a = cur.fetchone()
    cur.close()
    if a:
        return jsonify({"id": a[0], "titre": a[1], "contenu": a[2],
                        "auteur_id": a[3], "auteur": a[4],
                        "date_creation": str(a[5]), "categorie": a[6], "tags": a[7]}), 200
    return jsonify({"message": "Article non trouvé"}), 404

@app.route('/api/articles', methods=['POST'])
@jwt_required()
def create_article():
    data = request.get_json()
    if not data or not data.get('titre') or not data.get('contenu') or not data.get('auteur'):
        return jsonify({"message": "Titre, contenu et auteur obligatoires"}), 400
    auteur_id = get_jwt_identity()
    titre = data['titre']
    contenu = data['contenu']
    auteur = data['auteur']
    categorie = data.get('categorie', 'General')
    tags = data.get('tags', '')
    cur = mysql.connection.cursor()
    cur.execute("""INSERT INTO articles (titre, contenu, auteur_id, auteur, categorie, tags)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (titre, contenu, auteur_id, auteur, categorie, tags))
    mysql.connection.commit()
    new_id = cur.lastrowid
    cur.close()
    return jsonify({"message": "Article créé avec succès", "id": new_id}), 201

@app.route('/api/articles/<int:id>', methods=['PUT'])
@jwt_required()
def update_article(id):
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles WHERE id=%s", (id,))
    article = cur.fetchone()
    if not article:
        cur.close()
        return jsonify({"message": "Article non trouvé"}), 404
    titre = data.get('titre', article[1])
    contenu = data.get('contenu', article[2])
    categorie = data.get('categorie', article[6])
    tags = data.get('tags', article[7])
    cur.execute("UPDATE articles SET titre=%s, contenu=%s, categorie=%s, tags=%s WHERE id=%s",
                (titre, contenu, categorie, tags, id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Article modifié avec succès"}), 200

@app.route('/api/articles/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_article(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles WHERE id=%s", (id,))
    article = cur.fetchone()
    if not article:
        cur.close()
        return jsonify({"message": "Article non trouvé"}), 404
    cur.execute("DELETE FROM articles WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Article supprimé avec succès"}), 200

if __name__ == '__main__':
    app.run(debug=True)
