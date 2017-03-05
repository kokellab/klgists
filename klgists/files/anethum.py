import dill

def pkl(data, path: str):
    with open(path, 'wb') as f:
        dill.dump(data, f)

def unpkl(path: str):
    with open(path, 'rb') as f:
        return dill.load(f)
