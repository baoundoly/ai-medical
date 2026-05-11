using AIMedical.Api.Data;
using AIMedical.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/emr")]
[Authorize]
public class EmrController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IAiService _ai;

    public EmrController(AppDbContext db, IAiService ai)
    {
        _db = db;
        _ai = ai;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    /// <summary>Full clinical timeline for a patient: visits, vitals, lab reports, prescriptions.</summary>
    [HttpGet("{patientId:int}/timeline")]
    public async Task<ActionResult> GetTimeline(int patientId)
    {
        var visits = await _db.Visits
            .Include(v => v.Doctor)
            .Include(v => v.Prescriptions).ThenInclude(p => p.Items)
            .Include(v => v.LabReports)
            .Include(v => v.VitalSigns)
            .Where(v => v.PatientId == patientId && v.TenantId == TenantId)
            .OrderByDescending(v => v.VisitDate)
            .ToListAsync();

        var timeline = visits.Select(v => new
        {
            v.Id,
            v.VisitDate,
            Status = v.Status.ToString(),
            v.ChiefComplaint,
            v.AiSummary,
            Doctor = v.Doctor?.FullName,
            Prescriptions = v.Prescriptions.Select(p => new
            {
                p.Id,
                Status = p.Status.ToString(),
                p.SignedAt,
                Items = p.Items.Select(i => new
                {
                    i.MedicineName, i.Dosage, i.Frequency, i.Duration
                })
            }),
            LabReports = v.LabReports.Select(r => new
            {
                r.Id, r.ReportType, r.IsCritical, r.UploadedAt
            }),
            Vitals = v.VitalSigns.Select(vs => new
            {
                vs.Id, vs.BpSystolic, vs.BpDiastolic, vs.Pulse,
                vs.Temperature, vs.Spo2, vs.RecordedAt
            })
        });

        return Ok(timeline);
    }

    /// <summary>AI-generated patient summary across all visits.</summary>
    [HttpGet("{patientId:int}/summary")]
    public async Task<ActionResult> GetSummary(int patientId)
    {
        var patient = await _db.Patients
            .FirstOrDefaultAsync(p => p.Id == patientId && p.TenantId == TenantId);

        if (patient is null) return NotFound();

        var visits = await _db.Visits
            .Where(v => v.PatientId == patientId && v.TenantId == TenantId)
            .OrderByDescending(v => v.VisitDate)
            .Take(5)
            .ToListAsync();

        var recentText = string.Join("\n", visits.Select(v =>
            $"Visit {v.VisitDate:yyyy-MM-dd}: {v.ChiefComplaint} | {v.AiSummary}"));

        var aiSummary = await _ai.GetAiSummaryAsync(recentText);

        return Ok(new
        {
            patient.Id, patient.Name, patient.BloodGroup, patient.Gender,
            VisitCount = visits.Count,
            AiSummary = aiSummary ?? "AI layer unavailable."
        });
    }
}
