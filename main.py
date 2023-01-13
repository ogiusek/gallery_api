from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
cors = CORS(app, resources={r'*': {'origins': '*'}})
# cors = CORS(app, resources={r'*': {'origins': ['http://simplecreator.pl']}})
conn = sqlite3.connect('./database/database.db', check_same_thread=False)

# @app.route('/', methods=['GET', 'POST', 'DELETE', 'PATCH'])
# def init_get():
#   request.method POST GET DELETE PATCH
#   request.json
#   return jsonify(jsonify({'value': 'works'})


@app.route('/all/', defaults={'path': ''})
@app.route('/all/<path:path>')
def get_all(path):
    result = []
    if path == 'users':
        results = conn.execute('SELECT * FROM users')
        for res in results:
            result.append(res)
        return result
    elif path == 'images':
        results = conn.execute('SELECT * FROM images')
        for res in results:
            result.append(res)
    elif path == 'likes':
        results = conn.execute('SELECT * FROM likes')
        for res in results:
            result.append(res)
    elif path == 'comments':
        results = conn.execute('SELECT * FROM comments')
        for res in results:
            result.append(res)
    return result
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/users/', defaults={'path': ''})
@app.route('/users/<path:path>', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def users(path):
    if request.method == 'GET':
        results = conn.execute('SELECT * FROM users WHERE login = ?', [path])
        for res in results:
            return jsonify(res)
        return jsonify({'value': 'not found in database'})
    elif request.method == 'POST':
        req = request.json
        try:
            conn.execute('INSERT INTO users(login, password) VALUES(?, ?)', [req['login'], req['password']])
            conn.commit()
        except:
            return jsonify({'value': 'exists'})
    elif request.method == 'DELETE':
        req = request.json
        conn.execute('DELETE FROM users WHERE login = ?', [req['login']])
    elif request.method == 'PATCH':
        req = request.json
        conn.execute('UPDATE users SET password = ?, login = ? WHERE login = ?', [req['password'],
                                                                                  req['newLogin'],
                                                                                  req['login']])
    else:
        return jsonify({'value': 'not found'})
    return jsonify({'value': 'worked'})
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/images/', defaults={'path': ''})
@app.route('/images/<path:path>', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def images(path):
    if request.method == 'GET':
        results = conn.execute('''SELECT images.*,
                                  SUM(likes.value) as likes,
                                  SUM(NOT likes.value) as unlikes,
                                  CASE
                                    WHEN images.user_login = ? THEN CASE 
                                      WHEN likes.value is true THEN 1
                                      WHEN likes.value is false THEN -1
                                      ELSE 0
                                    END
                                    ELSE 0
                                  END AS liked,
                                  CASE
                                    WHEN SUM(likes.value) - SUM(NOT likes.value) IS NULL THEN 0
                                    ELSE SUM(likes.value) - SUM(NOT likes.value)
                                  END AS like_unlike_diff
                                  FROM images
                                  LEFT JOIN likes ON images.image_id = likes.image_id
                                  GROUP BY images.image_id
                                  ORDER BY like_unlike_diff DESC, init_date DESC;''', [path])
        result = []
        for res in results:
            result.append(res)
        if len(result) > 0:
            return result
        return jsonify({'value': 'not found in database'})
    elif request.method == 'POST':
        req = request.json
        try:
            conn.execute('INSERT INTO images(name, description, value, user_login) VALUES(?, ?, ?, ?)',
                         [req['name'],
                          req['description'],
                          req['value'],
                          req['user_login']])
            conn.commit()
        except:
            return jsonify({'value': 'exists'})
    elif request.method == 'DELETE':
        req = request.json
        conn.execute('DELETE FROM images WHERE image_id = ?', [req['id']])
        conn.commit()
    elif request.method == 'PATCH':
        req = request.json
        conn.execute('UPDATE images SET name = ?, description = ?, value = ? WHERE image_id = ?', [
            req['name'],
            req['description'],
            req['value'],
            req['id']])
        conn.commit()
    else:
        return jsonify({'value': 'not found'})
    return jsonify({'value': 'work'})
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/comments/', defaults={'path': ''})
@app.route('/comments/<path:path>', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def comments(path):
    if request.method == 'GET':
        # results = conn.execute('SELECT * FROM comments WHERE image_id = ?', [path])
        results = conn.execute('''SELECT comments.*,
            SUM(likeComment.value) as likes,
            SUM(NOT likeComment.value) as unlikes,
            CASE
                WHEN comments.user_login = ? THEN CASE 
                    WHEN likeComment.value is true THEN 1
                    WHEN likeComment.value is false THEN -1
                    ELSE 0
                END
                ELSE 0
            END AS liked,
            CASE
                WHEN SUM(likeComment.value) - SUM(NOT likeComment.value) IS NULL THEN 0
                ELSE SUM(likeComment.value) - SUM(NOT likeComment.value)
            END AS like_unlike_diff
            FROM comments
            LEFT JOIN likeComment ON comments.comment_id = likeComment.comment_id
            WHERE comments.image_id = ?
            GROUP BY comments.comment_id
            ORDER BY like_unlike_diff DESC, init_date DESC;''', [path.split('/')[0], path.split('/')[1]])
        result = []
        for res in results:
            result.append(res)
        return result
    elif request.method == 'POST':
        req = request.json
        try:
            conn.execute('INSERT INTO comments(value, image_id, user_login) VALUES(?, ?, ?)',
                         [req['value'],
                          req['image_id'],
                          req['user_login']])
            conn.commit()
        except:
            return jsonify({'value': 'error'})
    elif request.method == 'DELETE':
        req = request.json
        conn.execute('DELETE FROM comments WHERE comment_id = ?', [
            req['id']])
        conn.commit()
    elif request.method == 'PATCH':
        req = request.json
        conn.execute('UPDATE comments SET value = ? WHERE comment_id = ?', [req['value'], req['id']])
        conn.commit()
    else:
        return jsonify({'value': 'error'})
    return jsonify({'value': 'worked'})
# ----------------------------------------------------------------------------------------------------------------------


@app.route('/likes/', defaults={'path': ''})
@app.route('/likes/<path:path>', methods=['GET', 'POST', 'DELETE'])
def likes(path):
    if request.method == 'GET':
        result = conn.execute('SELECT * FROM likes where image_id = ?', [path])
        listed_result = [0, 0, []]
        for element in result:
            listed_result[2].append(element)
            if element[3]:
                listed_result[0] += 1
            else:
                listed_result[1] += 1
        return jsonify(listed_result)
    elif request.method == 'POST':
        req = request.json
        try:
            conn.execute('DElETE FROM likes WHERE image_id = ? AND user_login = ?', [
                req['image_id'],
                req['user_login']])
            conn.commit()
            conn.execute('INSERT INTO likes(value, image_id, user_login) VALUES(?, ? ,?)', [
                req['value'],
                req['image_id'],
                req['user_login']])
            conn.commit()
        except:
            return jsonify({'value': 'error'})
    elif request.method == 'DELETE':
        req = request.json
        conn.execute('DElETE FROM likes WHERE image_id = ? AND user_login = ?', [
            req['image_id'],
            req['user_login']])
        conn.commit()
    else:
        return jsonify({'value': 'not found'})
    return jsonify({'value': 'worked'})


@app.route('/likeComment/', defaults={'path': ''})
@app.route('/likeComment/<path:path>', methods=['GET', 'POST', 'DELETE'])
def like_comment(path):
    if request.method == 'GET':
        result = conn.execute('SELECT * FROM likeComment where comment_id = ?', [path])
        listed_result = [0, 0, []]
        for element in result:
            listed_result[2].append(element)
            if element[3]:
                listed_result[0] += 1
            else:
                listed_result[1] += 1
        return jsonify(listed_result)
    elif request.method == 'POST':
        req = request.json
        try:
            conn.execute('DElETE FROM likeComment WHERE comment_id = ? AND user_login = ?', [
                req['comment_id'],
                req['user_login']])
            conn.commit()
            conn.execute('INSERT INTO likeComment(value, comment_id, user_login) VALUES(?, ? ,?)', [
                req['value'],
                req['comment_id'],
                req['user_login']])
            conn.commit()
        except:
            return jsonify({'value': 'error'})
    elif request.method == 'DELETE':
        req = request.json
        conn.execute('DElETE FROM likeComment WHERE comment_id = ? AND user_login = ?', [
            req['image_id'],
            req['user_login']])
        conn.commit()
    else:
        return jsonify({'value': 'not found'})
    return jsonify({'value': 'worked'})


@app.route('/custom', methods=['POST'])
def custom():
    req = request.json
    response = conn.execute(req['sql'], req['values'])
    conn.commit()
    return jsonify({'value': response})


conn.execute('''CREATE TABLE IF NOT EXISTS users(
            login TEXT UNIQUE NOT NULL,
            password INTEGER NOT NULL,
            init_date DATE default CURRENT_TIMESTAMP);''')
# ----------------------------------------------------------------------------------------------------------------------
conn.execute('''CREATE TABLE IF NOT EXISTS images(
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_login TEXT,
            name VARCHAR(30) NOT NULL,
            description VARCHAR(150),
            value TEXT UNIQUE NOT NULL,
            init_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_login) REFERENCES users(login));''')
# ----------------------------------------------------------------------------------------------------------------------
conn.execute('''CREATE TABLE IF NOT EXISTS likes(
            like_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_login TEXT,
            image_id INTEGER,
            value BOOLEAN NOT NULL,
            FOREIGN KEY(user_login) REFERENCES users(login),
            FOREIGN KEY(image_id) REFERENCES images(image_id));''')
# ----------------------------------------------------------------------------------------------------------------------
conn.execute('''CREATE TABLE IF NOT EXISTS comments(
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_login TEXT,
            image_id INTEGER,
            value TEXT NOT NULL,
            init_date DATE default CURRENT_TIMESTAMP,
            FOREIGN KEY(user_login) REFERENCES users(login),
            FOREIGN KEY(image_id) REFERENCES images(image_id));''')
# ----------------------------------------------------------------------------------------------------------------------
conn.execute('''CREATE TABLE IF NOT EXISTS likeComment(
            like_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_login TEXT,
            comment_id INTEGER,
            value BOOLEAN NOT NULL,
            FOREIGN KEY(user_login) REFERENCES users(login),
            FOREIGN KEY(comment_id) REFERENCES comments(comment_id));''')

if __name__ == '__main__':
    from waitress import serve
    # serve(app, host='213.155.174.52', port=5000)
    serve(app, host='127.0.0.1', port=5000)
