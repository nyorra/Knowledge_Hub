from fastapi import FastAPI

app = FastAPI()

first_mes = "HelloWorld"

@app.get("/main")
async def get_main_page():
    return {"status": first_mes}
