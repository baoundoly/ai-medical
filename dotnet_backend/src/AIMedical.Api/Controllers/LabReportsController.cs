using AIMedical.Api.Data;
using AIMedical.Api.Models.Entities;
using AIMedical.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/lab-reports")]
[Authorize]
public class LabReportsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IAiService _ai;

    public LabReportsController(AppDbContext db, IAiService ai)
    {
        _db = db;
        _ai = ai;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    private int UserId => int.Parse(
        User.FindFirstValue("userId") ?? throw new UnauthorizedAccessException("userId claim missing"));

    [HttpGet]
    public async Task<ActionResult> GetAll(
        [FromQuery] int? patientId,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var query = _db.LabReports
            .Include(r => r.Patient)
            .Include(r => r.UploadedBy)
            .Where(r => r.Visit!.TenantId == TenantId);

        if (patientId.HasValue)
            query = query.Where(r => r.PatientId == patientId.Value);

        var list = await query
            .OrderByDescending(r => r.UploadedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(r => new
            {
                r.Id, r.VisitId, r.PatientId,
                PatientName = r.Patient != null ? r.Patient.Name : string.Empty,
                r.ReportType, r.FileUrl, r.OcrText, r.AiAnalysis, r.IsCritical, r.UploadedAt
            })
            .ToListAsync();

        return Ok(list);
    }

    /// <summary>Upload a lab report file (multipart/form-data).</summary>
    [HttpPost]
    [Consumes("multipart/form-data")]
    public async Task<ActionResult> Upload(
        [FromForm] int visitId,
        [FromForm] int patientId,
        [FromForm] string reportType,
        IFormFile file)
    {
        if (file is null || file.Length == 0)
            return BadRequest(new { message = "No file uploaded." });

        // In production, save to blob storage and return URL.
        // Here we persist a placeholder URL with the original filename.
        var fileName = $"{Guid.NewGuid()}_{file.FileName}";
        var fileUrl = $"/uploads/lab-reports/{fileName}";

        // Run OCR + AI analysis asynchronously on the text extracted from the file.
        // For now we store empty strings until an OCR integration is wired up.
        var report = new LabReport
        {
            VisitId = visitId,
            PatientId = patientId,
            UploadedById = UserId,
            ReportType = reportType,
            FileUrl = fileUrl,
            IsCritical = false,
            UploadedAt = DateTime.UtcNow
        };

        _db.LabReports.Add(report);
        await _db.SaveChangesAsync();

        return StatusCode(201, new { report.Id, report.FileUrl });
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult> GetById(int id)
    {
        var r = await _db.LabReports
            .Include(r => r.Patient)
            .Include(r => r.UploadedBy)
            .FirstOrDefaultAsync(r => r.Id == id && r.Visit!.TenantId == TenantId);

        if (r is null) return NotFound();

        return Ok(new
        {
            r.Id, r.VisitId, r.PatientId,
            PatientName = r.Patient?.Name ?? string.Empty,
            r.ReportType, r.FileUrl, r.OcrText, r.AiAnalysis, r.IsCritical, r.UploadedAt
        });
    }
}
