class Charger:

    def __init__(self):
        print('This object was initialized!')




with open('../coding-challenge-charger-uptime-main/input_1.txt', encoding="utf-8") as f:
    read_data = f.read()
    print(read_data)

sparky = Charger() # This object was initialized!