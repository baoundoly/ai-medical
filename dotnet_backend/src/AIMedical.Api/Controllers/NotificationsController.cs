using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

/// <summary>
/// Stub notifications controller. A full implementation would use SignalR or a
/// dedicated notification store. This provides the expected REST surface.
/// </summary>
[ApiController]
[Route("api/notifications")]
[Authorize]
public class NotificationsController : ControllerBase
{
    private static readonly List<object> _stub =
    [
        new { Id = 1, Title = "Welcome", Body = "Your account is active.", Type = "Info", IsRead = false, CreatedAt = DateTime.UtcNow.AddHours(-1) },
        new { Id = 2, Title = "Critical Lab Result", Body = "Patient MR-001 has a critical result.", Type = "Alert", IsRead = false, CreatedAt = DateTime.UtcNow.AddMinutes(-30) }
    ];

    [HttpGet]
    public ActionResult GetAll()
    {
        var userId = User.FindFirstValue("userId");
        // In production: query user-specific notifications from the database.
        return Ok(_stub);
    }

    [HttpPut("{id:int}/read")]
    public ActionResult MarkRead(int id)
    {
        // In production: update IsRead = true in the database.
        return NoContent();
    }
}
