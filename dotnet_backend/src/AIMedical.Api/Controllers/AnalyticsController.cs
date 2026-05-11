using AIMedical.Api.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/analytics")]
[Authorize(Roles = "Doctor,HospitalAdmin,SuperAdmin")]
public class AnalyticsController : ControllerBase
{
    private readonly AppDbContext _db;

    public AnalyticsController(AppDbContext db)
    {
        _db = db;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    /// <summary>Top chief complaints grouped by month.</summary>
    [HttpGet("disease-trends")]
    public async Task<ActionResult> DiseaseTrends(
        [FromQuery] int months = 6)
    {
        var cutoff = DateTime.UtcNow.AddMonths(-months);
        var trends = await _db.Visits
            .Where(v => v.TenantId == TenantId &&
                        v.VisitDate >= cutoff &&
                        v.ChiefComplaint != null)
            .GroupBy(v => new
            {
                Year = v.VisitDate.Year,
                Month = v.VisitDate.Month,
                v.ChiefComplaint
            })
            .Select(g => new
            {
                g.Key.Year,
                g.Key.Month,
                Complaint = g.Key.ChiefComplaint,
                Count = g.Count()
            })
            .OrderByDescending(x => x.Count)
            .Take(50)
            .ToListAsync();

        return Ok(trends);
    }

    /// <summary>Most prescribed medicines and prescriptions per doctor.</summary>
    [HttpGet("prescription-analytics")]
    public async Task<ActionResult> PrescriptionAnalytics([FromQuery] int days = 30)
    {
        var cutoff = DateTime.UtcNow.AddDays(-days);

        var topMeds = await _db.PrescriptionItems
            .Where(i => i.Prescription!.CreatedAt >= cutoff &&
                        i.Prescription.Visit!.TenantId == TenantId)
            .GroupBy(i => i.MedicineName)
            .Select(g => new { Medicine = g.Key, Count = g.Count() })
            .OrderByDescending(x => x.Count)
            .Take(20)
            .ToListAsync();

        var perDoctor = await _db.Prescriptions
            .Include(p => p.Doctor)
            .Where(p => p.CreatedAt >= cutoff && p.Visit!.TenantId == TenantId)
            .GroupBy(p => new { p.DoctorId, DoctorName = p.Doctor != null ? p.Doctor.FullName : "Unknown" })
            .Select(g => new { g.Key.DoctorId, g.Key.DoctorName, Count = g.Count() })
            .OrderByDescending(x => x.Count)
            .ToListAsync();

        return Ok(new { TopMedicines = topMeds, PerDoctor = perDoctor });
    }
}
