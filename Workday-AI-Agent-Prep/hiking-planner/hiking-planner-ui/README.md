# Trail Plan — Hiking Trip Planner UI

React + TypeScript (Vite) frontend for the hiking planner. Enter your **home address** and **hike start day & time** to get a trip summary and a social post to invite friends.

## Run

1. **Start the API** (from `hiking-planner/`, with `ANTHROPIC_API_KEY` in `.env`):

   ```bash
   cd ..   # from hiking-planner-ui, go to hiking-planner
   uvicorn hiking_api:app --reload --port 8000
   ```

2. **Start the UI** (from `hiking-planner/`):

   ```bash
   cd hiking-planner-ui
   npm install
   npm run dev
   ```

3. Open **http://localhost:5173**. The dev server proxies `/api` to `http://localhost:8000`.

## Build

```bash
npm run build
```

Output is in `dist/`. For production, serve the API and point the same origin at the API or configure your reverse proxy.
