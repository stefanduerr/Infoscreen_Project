from app import app
from own_ip import get_local_ip

#if __name__ == '__main__':
    #app.run(host="10.90.12.1", port=80, threaded=True, debug=True)

app.run(host=get_local_ip(), port=80, threaded=True, debug=True)
# Start der Webapp, auf IP der des aktuellen Geräts
