using AIMedical.Api.Data;
using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Models.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/visits")]
[Authorize]
public class VisitsController : ControllerBase
{
    private readonly AppDbContext _db;

    public VisitsController(AppDbContext db)
    {
        _db = db;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    private int UserId => int.Parse(
        User.FindFirstValue("userId") ?? throw new UnauthorizedAccessException("userId claim missing"));

    [HttpGet]
    public async Task<ActionResult<List<VisitResponse>>> GetAll(
        [FromQuery] int? patientId,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var query = _db.Visits
            .Include(v => v.Patient)
            .Include(v => v.Doctor)
            .Where(v => v.TenantId == TenantId);

        if (patientId.HasValue)
            query = query.Where(v => v.PatientId == patientId.Value);

        var visits = await query
            .OrderByDescending(v => v.VisitDate)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(v => ToResponse(v))
            .ToListAsync();

        return Ok(visits);
    }

    [HttpPost]
    public async Task<ActionResult<VisitResponse>> Create([FromBody] VisitCreateRequest request)
    {
        var visit = new Visit
        {
            TenantId = TenantId,
            PatientId = request.PatientId,
            DoctorId = request.DoctorId,
            AssistantId = request.AssistantId,
            ChiefComplaint = request.ChiefComplaint,
            Hpi = request.Hpi,
            Ros = request.Ros,
            PastHistory = request.PastHistory,
            FamilyHistory = request.FamilyHistory,
            SocialHistory = request.SocialHistory,
            VisitDate = DateTime.UtcNow,
            Status = VisitStatus.InProgress
        };

        _db.Visits.Add(visit);
        await _db.SaveChangesAsync();

        await _db.Entry(visit).Reference(v => v.Patient).LoadAsync();
        await _db.Entry(visit).Reference(v => v.Doctor).LoadAsync();

        return CreatedAtAction(nameof(GetById), new { id = visit.Id }, ToResponse(visit));
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<VisitResponse>> GetById(int id)
    {
        var visit = await _db.Visits
            .Include(v => v.Patient)
            .Include(v => v.Doctor)
            .FirstOrDefaultAsync(v => v.Id == id && v.TenantId == TenantId);

        if (visit is null) return NotFound();
        return Ok(ToResponse(visit));
    }

    [HttpPut("{id:int}")]
    public async Task<ActionResult<VisitResponse>> Update(
        int id, [FromBody] VisitUpdateRequest request)
    {
        var visit = await _db.Visits
            .Include(v => v.Patient)
            .Include(v => v.Doctor)
            .FirstOrDefaultAsync(v => v.Id == id && v.TenantId == TenantId);

        if (visit is null) return NotFound();

        if (request.ChiefComplaint is not null) visit.ChiefComplaint = request.ChiefComplaint;
        if (request.Hpi is not null) visit.Hpi = request.Hpi;
        if (request.Ros is not null) visit.Ros = request.Ros;
        if (request.PastHistory is not null) visit.PastHistory = request.PastHistory;
        if (request.FamilyHistory is not null) visit.FamilyHistory = request.FamilyHistory;
        if (request.SocialHistory is not null) visit.SocialHistory = request.SocialHistory;
        if (request.AiSummary is not null) visit.AiSummary = request.AiSummary;
        if (request.Status is not null && Enum.TryParse<VisitStatus>(request.Status, out var s))
            visit.Status = s;

        await _db.SaveChangesAsync();
        return Ok(ToResponse(visit));
    }

    /// <summary>Only a Doctor may approve a visit.</summary>
    [HttpPost("{id:int}/approve")]
    [Authorize(Roles = "Doctor,HospitalAdmin,SuperAdmin")]
    public async Task<ActionResult<VisitResponse>> Approve(int id, [FromBody] VisitApproveRequest request)
    {
        var visit = await _db.Visits
            .Include(v => v.Patient)
            .Include(v => v.Doctor)
            .FirstOrDefaultAsync(v => v.Id == id && v.TenantId == TenantId);

        if (visit is null) return NotFound();
        if (visit.DoctorApprovedAt.HasValue)
            return Conflict(new { message = "Visit already approved." });

        visit.DoctorApprovedAt = DateTime.UtcNow;
        visit.DoctorApprovedBy = UserId;
        visit.Status = VisitStatus.Completed;

        await _db.SaveChangesAsync();
        return Ok(ToResponse(visit));
    }

    private static VisitResponse ToResponse(Visit v) => new(
        v.Id,
        v.PatientId,
        v.Patient?.Name ?? string.Empty,
        v.DoctorId,
        v.Doctor?.FullName ?? string.Empty,
        v.VisitDate,
        v.Status.ToString(),
        v.ChiefComplaint,
        v.AiSummary,
        v.DoctorApprovedAt);
}
