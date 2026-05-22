import uvicorn

def start():
    uvicorn.run("vaultpass_backend.main:app", host="0.0.0.0", port=8000, reload=True, app_dir="/src")