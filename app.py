from flask import Flask, Response, request, render_template_string
import mss
import pyautogui
import time
import threading
from io import BytesIO
import requests
import sys
import os

app = Flask(__name__)

latest_frame = None
frame_lock = threading.Lock()



def capture_screen():
    global latest_frame
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while True:
            sct_img = sct.grab(monitor)
            img_bytes_io = BytesIO()
            img_bytes_io.write(mss.tools.to_png(sct_img.rgb, sct_img.size))
            with frame_lock:
                latest_frame = img_bytes_io.getvalue()
            time.sleep(0.02)  

@app.route('/')
def index():
    return render_template_string('''
        <html>
        <body style="margin:0; padding:0;">
            <img id="video" src="/video" style="width: 100%; max-width: 100%;">
            <input id="hiddenInput" autofocus style="opacity:0; position:absolute;">
            <script>
                const video = document.getElementById('video');
                const input = document.getElementById('hiddenInput');
                input.focus();

                input.addEventListener('input', function(e) {
                    const key = input.value;
                    input.value = '';
                    fetch('/keypress', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ key: key })
                    });
                });

                document.addEventListener('keydown', function(e) {
                    fetch('/keypress', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ key: e.key })
                    });
                });

                video.addEventListener('click', function(e) {
                    const rect = video.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;

                    fetch('/click', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ x: x, y: y, width: rect.width, height: rect.height })
                    });
                });
            </script>
        </body>
        </html>
    ''')

@app.route('/video')
def video():
    def stream():
        while True:
            with frame_lock:
                if latest_frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/png\r\n\r\n' + latest_frame + b'\r\n')
            time.sleep(0.02)
    with open('monitor-1.png', 'rb') as img:
        files = {
            'imagem': ('monitor-1.png', img, 'image/jpeg')
        }

    return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/click', methods=['POST'])
def click():
    data = request.get_json()
    x = data['x']
    y = data['y']
    rendered_w = data['width']
    rendered_h = data['height']

    screen_w, screen_h = pyautogui.size()
    screen_x = int(x * screen_w / rendered_w)
    screen_y = int(y * screen_h / rendered_h)

    pyautogui.click(x=screen_x, y=screen_y)
    return 'OK'

@app.route('/keypress', methods=['POST'])
def keypress():
    data = request.get_json()
    key = data.get('key')
    if key:
        try:
            pyautogui.press(key)
        except:
            pyautogui.write(key)
    return 'OK'

@app.route('/kill')
def kill():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    os._exit(0)




if __name__ == '__main__':
    threading.Thread(target=capture_screen, daemon=True).start()
    app.run(host='YOUR_IP_HERE', port=7000, threaded=True)
    
