from app import app

if __name__ == '__main__':
    app.run(host="10.90.12.1", port=5000, threaded=True, debug=True)
