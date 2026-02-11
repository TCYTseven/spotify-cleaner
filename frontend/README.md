# Frontend (Next.js)

Web UI for the Intelligent Music Agent platform.

## Run locally

1. Configure backend URL:

```bash
cp .env.example .env.local
```

2. Install and run dev server:

```bash
npm install
npm run dev
```

3. Open:

`http://localhost:3000`

## Environment

- `NEXT_PUBLIC_API_BASE_URL` (default in example: `http://127.0.0.1:8000`)

## Notes

- This UI expects the FastAPI backend to be running separately.
- CORS is configured in the backend for localhost Next.js origins by default.
