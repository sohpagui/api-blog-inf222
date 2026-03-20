from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import hashlib

app = Flask(__name__)

# Configuration MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'pascal'
app.config['MYSQL_PASSWORD'] = 'Root@1234'
app.config['MYSQL_DB'] = 'blog_db'

# Configuration JWT
app.config['JWT_SECRET_KEY'] = 'inf222-blog-secret-key'

mysql = MySQL(app)
jwt = JWTManager(app)

# ─── AUTH ────────────────────────────────────────
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    nom = data['nom']
    email = data['email']
    mot_de_passe = hashlib.sha256(data['mot_de_passe'].encode()).hexdigest()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO utilisateurs (nom, email, mot_de_passe) VALUES (%s, %s, %s)",
                (nom, email, mot_de_passe))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
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
@app.route('/articles', methods=['GET'])
def get_articles():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()
    cur.close()
    result = [{"id": a[0], "titre": a[1], "contenu": a[2], "auteur_id": a[3]} for a in articles]
    return jsonify(result), 200

@app.route('/articles/<int:id>', methods=['GET'])
def get_article(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM articles WHERE id=%s", (id,))
    a = cur.fetchone()
    cur.close()
    if a:
        return jsonify({"id": a[0], "titre": a[1], "contenu": a[2], "auteur_id": a[3]}), 200
    return jsonify({"message": "Article non trouvé"}), 404

@app.route('/articles', methods=['POST'])
@jwt_required()
def create_article():
    data = request.get_json()
    auteur_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO articles (titre, contenu, auteur_id) VALUES (%s, %s, %s)",
                (data['titre'], data['contenu'], auteur_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Article créé avec succès"}), 201

@app.route('/articles/<int:id>', methods=['PUT'])
@jwt_required()
def update_article(id):
    data = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute("UPDATE articles SET titre=%s, contenu=%s WHERE id=%s",
                (data['titre'], data['contenu'], id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Article modifié avec succès"}), 200

@app.route('/articles/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_article(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Article supprimé avec succès"}), 200

if __name__ == '__main__':
    app.run(debug=True)
