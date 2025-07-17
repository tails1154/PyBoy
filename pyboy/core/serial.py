from flask import Flask, request, jsonify
from pyboy.utils import MAX_CYCLES

app = Flask(__name__)

CYCLES_8192HZ = 128

class Serial:
    def __init__(self):
        self.SB = 0xFF
        self.SC = 0
        self.transfer_enabled = 0
        self.internal_clock = 0
        self._cycles_to_interrupt = 0
        self.last_cycles = 0
        self.clock = 0
        self.clock_target = MAX_CYCLES
        self.received_data = []

    def set_SB(self, value):
        self.SB = value

    def get_SB(self):
        return self.SB

    def set_SC(self, value):
        self.SC = value
        self.transfer_enabled = self.SC & 0x80
        self.internal_clock = self.SC & 1
        if self.internal_clock:
            self.clock_target = self.clock + 8 * CYCLES_8192HZ
        else:
            self.transfer_enabled = 0
            self.clock_target = MAX_CYCLES
        self._cycles_to_interrupt = self.clock_target - self.clock

    def get_SC(self):
        return self.SC

    def send_data(self, data):
        self.received_data.append(data)
        self.set_SB(data)

    def receive_data(self):
        if self.received_data:
            return self.received_data.pop(0)
        else:
            return None

serial = Serial()

@app.route('/serial/send', methods=['POST'])
def send_data():
    data = request.json.get('data')
    if data is None:
        return jsonify({'error': 'No data provided'}), 400
    serial.send_data(data)
    return jsonify({'status': 'ok', 'sent': data})

@app.route('/serial/receive', methods=['GET'])
def receive_data():
    data = serial.receive_data()
    if data is None:
        return jsonify({'status': 'empty'})
    return jsonify({'status': 'ok', 'data': data})

@app.route('/serial/SB', methods=['GET', 'POST'])
def sb():
    if request.method == 'POST':
        value = request.json.get('value')
        serial.set_SB(value)
        return jsonify({'status': 'ok', 'SB': value})
    else:
        return jsonify({'SB': serial.get_SB()})

@app.route('/serial/SC', methods=['GET', 'POST'])
def sc():
    if request.method == 'POST':
        value = request.json.get('value')
        serial.set_SC(value)
        return jsonify({'status': 'ok', 'SC': value})
    else:
        return jsonify({'SC': serial.get_SC()})

if __name__ == '__main__':
    app.run(debug=True)
