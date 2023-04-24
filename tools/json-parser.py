import json

with open('tools/test.json') as f:
    data = json.load(f)

build_order = data['buildings']

for key in build_order:
    atSupply = key['atSupply']
    type =  key['type']
    unit = key['unit']
    if 'targetQuantity' in key:
        targetQuantity = key['targetQuantity']
    else:
        targetQuantity = None
        
    print(atSupply, type, unit, targetQuantity)