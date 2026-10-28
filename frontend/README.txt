# AdversarialCompiler Frontend

## Install
1. Copy `index.html` into your project's `frontend` folder.
2. Start your backend from the project root:
   `python -m uvicorn backend.app.main:app --reload`
3. Open a second terminal and run:
   `python -m http.server 5500 --directory frontend`
4. Open http://127.0.0.1:5500 in your browser.

The page calls:
- GET /api/health
- POST /api/analyze
- POST /api/robustness

If your API uses a different address, update `API_BASE` near the bottom of index.html.
If browser requests are blocked by CORS, add CORSMiddleware in FastAPI allowing `http://127.0.0.1:5500`.

Security note: this frontend does not execute submitted programs. Do not expose a compiler API to untrusted users without proper sandboxing.
