import uvicorn
from App import App

if __name__ == '__main__':
    app_instance = App()
    uvicorn.run(app_instance.app, host="0.0.0.0", port=8888, timeout_keep_alive=60)
