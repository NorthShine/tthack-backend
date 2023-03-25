import uvicorn


if __name__ == "__main__":
    uvicorn.run("main:app", port=5001, log_level="info", reload=True)
