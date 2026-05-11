# Migrations

EF Core migrations are generated at build time with:

```bash
dotnet ef migrations add InitialCreate --project src/AIMedical.Api
dotnet ef database update --project src/AIMedical.Api
```

Do **not** commit auto-generated migration files from a developer machine. Generate migrations as part of CI/CD using the production connection string.
