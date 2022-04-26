from app import app


app.run(host="0.0.0.0", port=80, threaded=True, debug=True)
# Start der Webapp, auf IP der des aktuellen Geräts
