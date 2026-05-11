using AIMedical.Api.Data;
using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Models.Entities;
using AIMedical.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/prescriptions")]
[Authorize]
public class PrescriptionsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IAiService _ai;

    public PrescriptionsController(AppDbContext db, IAiService ai)
    {
        _db = db;
        _ai = ai;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    private int UserId => int.Parse(
        User.FindFirstValue("userId") ?? throw new UnauthorizedAccessException("userId claim missing"));

    [HttpGet]
    public async Task<ActionResult<List<PrescriptionResponse>>> GetAll(
        [FromQuery] int? patientId,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var query = _db.Prescriptions
            .Include(p => p.Patient)
            .Include(p => p.Doctor)
            .Include(p => p.Items)
            .Where(p => p.Visit != null && p.Visit.TenantId == TenantId);

        if (patientId.HasValue)
            query = query.Where(p => p.PatientId == patientId.Value);

        var list = await query
            .OrderByDescending(p => p.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return Ok(list.Select(ToResponse).ToList());
    }

    [HttpPost]
    [Authorize(Roles = "Doctor,HospitalAdmin,SuperAdmin")]
    public async Task<ActionResult<PrescriptionResponse>> Create([FromBody] PrescriptionCreateRequest request)
    {
        var prescription = new Prescription
        {
            VisitId = request.VisitId,
            PatientId = request.PatientId,
            DoctorId = UserId,
            Status = PrescriptionStatus.Draft,
            CreatedAt = DateTime.UtcNow,
            Items = request.Items.Select(i => new PrescriptionItem
            {
                MedicineName = i.MedicineName,
                Dosage = i.Dosage,
                Frequency = i.Frequency,
                Duration = i.Duration,
                MealInstruction = i.MealInstruction
            }).ToList()
        };

        _db.Prescriptions.Add(prescription);
        await _db.SaveChangesAsync();

        await _db.Entry(prescription).Reference(p => p.Patient).LoadAsync();
        await _db.Entry(prescription).Reference(p => p.Doctor).LoadAsync();

        return CreatedAtAction(nameof(GetById), new { id = prescription.Id }, ToResponse(prescription));
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<PrescriptionResponse>> GetById(int id)
    {
        var p = await _db.Prescriptions
            .Include(p => p.Patient)
            .Include(p => p.Doctor)
            .Include(p => p.Items)
            .FirstOrDefaultAsync(p => p.Id == id && p.Visit!.TenantId == TenantId);

        if (p is null) return NotFound();
        return Ok(ToResponse(p));
    }

    /// <summary>Sign a prescription. Only Doctors may sign.</summary>
    [HttpPost("{id:int}/sign")]
    [Authorize(Roles = "Doctor,HospitalAdmin,SuperAdmin")]
    public async Task<ActionResult<PrescriptionResponse>> Sign(
        int id, [FromBody] PrescriptionSignRequest request)
    {
        var p = await _db.Prescriptions
            .Include(p => p.Patient)
            .Include(p => p.Doctor)
            .Include(p => p.Items)
            .FirstOrDefaultAsync(p => p.Id == id && p.Visit!.TenantId == TenantId);

        if (p is null) return NotFound();
        if (p.Status == PrescriptionStatus.Signed)
            return Conflict(new { message = "Already signed." });

        if (!Enum.TryParse<SignatureMethod>(request.SignatureMethod, ignoreCase: true, out var method))
            return BadRequest(new { message = "Invalid signature method." });

        p.Status = PrescriptionStatus.Signed;
        p.SignedAt = DateTime.UtcNow;
        p.SignatureMethod = method;

        // Generate deterministic hash for digital signatures
        if (method == SignatureMethod.Digital)
        {
            var payload = $"{p.Id}:{p.DoctorId}:{p.SignedAt:O}";
            p.DigitalSignatureHash = request.DigitalSignatureHash
                ?? Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(payload)));
        }

        await _db.SaveChangesAsync();
        return Ok(ToResponse(p));
    }

    /// <summary>Parse a voice-recorded prescription via the AI layer.</summary>
    [HttpPost("voice-parse")]
    [Authorize(Roles = "Doctor,HospitalAdmin,SuperAdmin")]
    public async Task<ActionResult<object>> VoiceParse([FromBody] VoicePrescriptionRequest request)
    {
        var result = await _ai.ParseVoicePrescriptionAsync(request.AudioBase64);
        if (result is null)
            return StatusCode(503, new { message = "AI layer unavailable." });

        return Ok(new { prescription = result });
    }

    private static PrescriptionResponse ToResponse(Prescription p) => new(
        p.Id, p.VisitId, p.PatientId,
        p.Patient?.Name ?? string.Empty,
        p.DoctorId,
        p.Doctor?.FullName ?? string.Empty,
        p.Status.ToString(),
        p.SignedAt,
        p.CreatedAt,
        p.Items.Select(i => new PrescriptionItemResponse(
            i.Id, i.MedicineName, i.Dosage, i.Frequency, i.Duration, i.MealInstruction))
        .ToList());
}
