import json
import os

async def save_json(obj,path:str):
    try:
        dirs = os.path.dirname(path)
        os.makedirs(dirs,exist_ok=True)
        with open(path,'w') as f:
            json.dump(obj,f)
    except:
        pass


    
async def load_json(path:str):
    try:
        with open(path,'r') as f:
            obj = json.load(f)
        return obj
    except:
        pass