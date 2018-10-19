import yaml

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    print("hey!")
    init = True
