# EEMS Backend

ASP.NET Core 8 modular monolith with PostgreSQL and EF Core.

## Local database configuration

```powershell
dotnet user-secrets set "ConnectionStrings:EemsDatabase" "Host=localhost;Port=5432;Database=eems_dev;Username=eems_app;Password=YOUR_LOCAL_PASSWORD" --project src/EEMS.Api
```

## Commands

```powershell
dotnet restore EEMS.sln
dotnet build EEMS.sln
dotnet test EEMS.sln
dotnet run --project src/EEMS.Api
```

Tenant identifiers must come from verified server context. Client-supplied tenant identifiers are not trusted.
