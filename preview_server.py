"""
Preview server for Replit — serves the /docs UI with mocked endpoints.
Extracts _DOCS_HTML directly from api_server.py via AST (no checkout_engine import).
"""
import os, ast, pathlib
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

def _load_docs_html():
    src = (pathlib.Path(__file__).parent / "api_server.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "_DOCS_HTML":
                    return ast.literal_eval(node.value)
    raise RuntimeError("_DOCS_HTML not found in api_server.py")

_DOCS_HTML = _load_docs_html()

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/", include_in_schema=False)
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@app.get("/docs", include_in_schema=False)
async def docs():
    return HTMLResponse(
        _DOCS_HTML,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        }
    )

@app.get("/health")
async def health():
    return {"ok": True, "threads": 200, "retries": 1}

@app.get("/check")
async def check_get(card: str = "", url: str = "", proxy: str = "", low: str = "true"):
    return {
        "status": "CHARGED",
        "status_code": "ORDER_PLACED",
        "amount": "2.99",
        "error": "",
        "retryable": False,
        "receipt_url": "https://demo-store.myshopify.com/orders/12345"
    }

@app.post("/check")
async def check_post():
    return {
        "status": "CHARGED",
        "status_code": "ORDER_PLACED",
        "amount": "2.99",
        "error": "",
        "retryable": False,
        "receipt_url": "https://demo-store.myshopify.com/orders/12345"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
