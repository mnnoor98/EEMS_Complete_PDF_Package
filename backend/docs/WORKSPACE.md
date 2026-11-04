# EEMS

Election operations management platform for parliamentary and local-government elections.

## Workspace layout

- `backend/` — ASP.NET Core 8 modular monolith, EF Core migrations and automated tests.
- `frontend/` — independent Angular client workspace.
- `backend/docs/` — backend, database and workspace documentation.
- `frontend/docs/` — frontend documentation.

The backend and frontend have separate dependency, build and runtime boundaries. Database credentials must never be committed.

## Backend

```powershell
cd backend
dotnet restore EEMS.sln
dotnet build EEMS.sln
dotnet test EEMS.sln
```

## Frontend

Frontend implementation belongs only under `frontend/`. See `frontend/README.md` for its boundary and planned setup.
