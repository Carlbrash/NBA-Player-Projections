from fastapi import FastAPI

app = FastAPI(title='NBA Player Projections', version='0.1.0')

@app.get('/health')
def health():
    return {'status': 'ok', 'phase': 'foundation'}
