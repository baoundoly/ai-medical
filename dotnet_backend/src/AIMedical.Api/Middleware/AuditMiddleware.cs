using AIMedical.Api.Data;
using AIMedical.Api.Models.Entities;
using System.Security.Claims;

namespace AIMedical.Api.Middleware;

public class AuditMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<AuditMiddleware> _logger;

    public AuditMiddleware(RequestDelegate next, ILogger<AuditMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context, AppDbContext db)
    {
        await _next(context);

        var method = context.Request.Method;
        if (method is not ("POST" or "PUT" or "DELETE" or "PATCH"))
            return;

        // Only audit successful mutating calls
        if (context.Response.StatusCode >= 500)
            return;

        try
        {
            var userId = GetUserId(context);
            var tenantId = GetTenantId(context);
            var path = context.Request.Path.Value ?? string.Empty;
            var resource = InferResourceType(path);
            var resourceId = InferResourceId(path);
            var ip = context.Connection.RemoteIpAddress?.ToString();

            var log = new AuditLog
            {
                TenantId = tenantId,
                UserId = userId,
                Action = method,
                ResourceType = resource,
                ResourceId = resourceId,
                IpAddress = ip,
                Timestamp = DateTime.UtcNow
            };

            db.AuditLogs.Add(log);
            await db.SaveChangesAsync();
        }
        catch (Exception ex)
        {
            // Sanitize user-controlled values before logging to prevent log-forging.
            var safeMethod = method.Replace(Environment.NewLine, "").Replace("\r", "").Replace("\n", "");
            var safePath = (context.Request.Path.Value ?? string.Empty)
                .Replace(Environment.NewLine, "").Replace("\r", "").Replace("\n", "");

            _logger.LogWarning(ex, "Audit log write failed for {Method} {Path}", safeMethod, safePath);
        }
    }

    private static int? GetUserId(HttpContext context)
    {
        var claim = context.User.FindFirstValue("userId")
            ?? context.User.FindFirstValue(ClaimTypes.NameIdentifier);
        return int.TryParse(claim, out var id) ? id : null;
    }

    private static int? GetTenantId(HttpContext context)
    {
        var claim = context.User.FindFirstValue("tenantId");
        return int.TryParse(claim, out var id) ? id : null;
    }

    private static string InferResourceType(string path)
    {
        var segments = path.Split('/', StringSplitOptions.RemoveEmptyEntries);
        // e.g. /api/patients/42 -> "patients"
        return segments.Length >= 2 ? segments[1] : path;
    }

    private static string? InferResourceId(string path)
    {
        var segments = path.Split('/', StringSplitOptions.RemoveEmptyEntries);
        return segments.Length >= 3 ? segments[2] : null;
    }
}
