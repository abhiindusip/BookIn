from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
import yaml
import os

from booksim_engine import save_generated_config, run_simulation

app = FastAPI(
    title="Booksim Runner",
    description="Run NoC simulations via Booksim using natural language-generated configs.",
    version="1.0.0"
)

# === Models ===

class GeneratedConfigRequest(BaseModel):
    config_str: str

# === Plugin Endpoints ===

@app.post("/run-generated-config")
def run_generated_config(req: GeneratedConfigRequest):
    config_path = save_generated_config(req.config_str)
    result = run_simulation(config_path)
    return result

@app.get("/openapi.yaml", response_class=PlainTextResponse)
def serve_openapi_yaml():
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )
    return yaml.dump(schema, sort_keys=False)

# Serve static plugin files
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

@app.get("/logo.png")
def get_logo():
    return FileResponse("logo.png")

@app.get("/legal")
def legal_info():
    return {"message": "Use of this plugin is subject to the MIT License."}

# === Local dev only: generate openapi.yaml ===

if __name__ == "__main__":
    # Save schema locally
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )
    with open("openapi.yaml", "w") as f:
        yaml.dump(schema, f, sort_keys=False)
    print("✅ openapi.yaml written!")

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
