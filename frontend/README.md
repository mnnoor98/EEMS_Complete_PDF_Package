# EEMS Frontend

Angular 22 standalone frontend for the Election Enterprise Management System.

## Run locally

```powershell
npm install
npm start
```

The development server proxies `/api` to the local backend at `http://localhost:5131`.

## Quality checks

```powershell
npm run build
npm test
```

Authentication tokens are kept in `sessionStorage`, never `localStorage`.
