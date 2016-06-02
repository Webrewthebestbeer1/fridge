from random import uniform

class W1Sim:
    def __init__(self, ids):
        self.sensors = [
            SimSensor(ids[i]) for i in range(3)
        ]

    def get_available_sensors(self):
        return self.sensors


class SimSensor:
    def __init__(self, id):
        self.id = id

    def get_temperature(self):
        return uniform(3.2, 20.1)
