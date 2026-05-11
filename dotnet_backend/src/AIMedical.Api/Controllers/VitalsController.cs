using AIMedical.Api.Data;
using AIMedical.Api.Models.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/vitals")]
[Authorize]
public class VitalsController : ControllerBase
{
    private readonly AppDbContext _db;

    public VitalsController(AppDbContext db)
    {
        _db = db;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    private int UserId => int.Parse(
        User.FindFirstValue("userId") ?? throw new UnauthorizedAccessException("userId claim missing"));

    [HttpGet("{visitId:int}")]
    public async Task<ActionResult> GetByVisit(int visitId)
    {
        var vitals = await _db.VitalSigns
            .Where(v => v.VisitId == visitId && v.Visit!.TenantId == TenantId)
            .OrderByDescending(v => v.RecordedAt)
            .ToListAsync();

        return Ok(vitals);
    }

    [HttpPost]
    public async Task<ActionResult> Record([FromBody] VitalsRecordRequest request)
    {
        var vital = new VitalSigns
        {
            VisitId = request.VisitId,
            PatientId = request.PatientId,
            RecordedById = UserId,
            BpSystolic = request.BpSystolic,
            BpDiastolic = request.BpDiastolic,
            Pulse = request.Pulse,
            Temperature = request.Temperature,
            Spo2 = request.Spo2,
            Weight = request.Weight,
            Height = request.Height,
            RespiratoryRate = request.RespiratoryRate,
            Consciousness = request.Consciousness,
            RecordedAt = DateTime.UtcNow
        };

        if (vital.Weight.HasValue && vital.Height.HasValue && vital.Height.Value > 0)
        {
            var heightM = vital.Height.Value / 100m;
            vital.Bmi = Math.Round(vital.Weight.Value / (heightM * heightM), 1);
        }

        _db.VitalSigns.Add(vital);
        await _db.SaveChangesAsync();

        // Calculate and persist NEWS2 score
        var news = CalculateNews2(vital);
        _db.NewsScores.Add(news);
        await _db.SaveChangesAsync();

        return StatusCode(201, new { vital.Id, NewsScore = new { news.Score, news.RiskLevel } });
    }

    [HttpGet("{visitId:int}/news-score")]
    public async Task<ActionResult> GetNewsScore(int visitId)
    {
        var latest = await _db.VitalSigns
            .Include(v => v.NewsScore)
            .Where(v => v.VisitId == visitId && v.Visit!.TenantId == TenantId)
            .OrderByDescending(v => v.RecordedAt)
            .FirstOrDefaultAsync();

        if (latest is null) return NotFound();
        return Ok(latest.NewsScore);
    }

    /// <summary>NEWS2 scoring algorithm (Royal College of Physicians).</summary>
    private static NewsScore CalculateNews2(VitalSigns v)
    {
        int score = 0;

        // Respiratory rate
        score += v.RespiratoryRate switch
        {
            <= 8 => 3,
            <= 11 => 1,
            <= 20 => 0,
            <= 24 => 2,
            _ => 3
        };

        // SpO2 (Scale 1 – no hypercapnic respiratory failure)
        score += v.Spo2 switch
        {
            <= 91 => 3,
            <= 93 => 2,
            <= 95 => 1,
            _ => 0
        };

        // Systolic BP
        score += v.BpSystolic switch
        {
            <= 90 => 3,
            <= 100 => 2,
            <= 110 => 1,
            <= 219 => 0,
            _ => 3
        };

        // Pulse
        score += v.Pulse switch
        {
            <= 40 => 3,
            <= 50 => 1,
            <= 90 => 0,
            <= 110 => 1,
            <= 130 => 2,
            _ => 3
        };

        // Consciousness (A=Alert, C=Confusion, V=Voice, P=Pain, U=Unresponsive)
        score += v.Consciousness?.ToUpper() switch
        {
            "A" or "ALERT" => 0,
            _ => 3
        };

        // Temperature
        score += v.Temperature switch
        {
            <= 35.0m => 3,
            <= 36.0m => 1,
            <= 38.0m => 0,
            <= 39.0m => 1,
            _ => 2
        };

        var riskLevel = score switch
        {
            0 => "Low",
            <= 4 => "Low",
            5 or 6 => "Medium",
            _ => "High"
        };

        return new NewsScore
        {
            VitalId = v.Id,
            Score = score,
            RiskLevel = riskLevel,
            CalculatedAt = DateTime.UtcNow
        };
    }
}

public record VitalsRecordRequest(
    int VisitId,
    int PatientId,
    int? BpSystolic,
    int? BpDiastolic,
    int? Pulse,
    decimal? Temperature,
    int? Spo2,
    decimal? Weight,
    decimal? Height,
    int? RespiratoryRate,
    string? Consciousness
);
