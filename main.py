import uvicorn
from api_app import app

if __name__ == "__main__":
    print("Iniciando o servidor do FOCUS...")
    print("  Telas desktop: http://127.0.0.1:8000/desktop/telainicialDesktop.html")
    print("  Telas mobile : http://127.0.0.1:8000/mobile/telainicial.html")
    print("  Documentação : http://127.0.0.1:8000/docs")
    uvicorn.run("api_app:app", host="127.0.0.1", port=8000, reload=True)