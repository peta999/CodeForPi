import yaml



with open(r'C:\Users\hoppe\Documents\GitHub\CodeForPi\config.yaml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    list_doc = yaml.safe_load(file)
    #print(list_doc)
    list_doc["huehnerstall"]["verschiebung_abends"] = 5
    print(list_doc["huehnerstall"]["verschiebung_abends"])

print(list_doc)

with open(r"C:\Users\hoppe\Documents\GitHub\CodeForPi\config.yaml", "w") as f:
    yaml.dump(list_doc, f)