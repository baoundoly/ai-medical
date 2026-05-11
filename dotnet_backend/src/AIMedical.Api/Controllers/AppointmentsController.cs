using AIMedical.Api.Data;
using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Models.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/appointments")]
[Authorize]
public class AppointmentsController : ControllerBase
{
    private readonly AppDbContext _db;

    public AppointmentsController(AppDbContext db)
    {
        _db = db;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    [HttpGet]
    public async Task<ActionResult<List<AppointmentResponse>>> GetAll(
        [FromQuery] int? doctorId,
        [FromQuery] DateTime? date,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var query = _db.Appointments
            .Include(a => a.Patient)
            .Include(a => a.Doctor)
            .Where(a => a.TenantId == TenantId);

        if (doctorId.HasValue) query = query.Where(a => a.DoctorId == doctorId.Value);
        if (date.HasValue)
        {
            var d = date.Value.Date;
            query = query.Where(a => a.ScheduledAt.Date == d);
        }

        var result = await query
            .OrderBy(a => a.ScheduledAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(a => ToResponse(a))
            .ToListAsync();

        return Ok(result);
    }

    [HttpPost]
    public async Task<ActionResult<AppointmentResponse>> Create([FromBody] AppointmentCreateRequest request)
    {
        // Assign next token for the doctor on that day
        var dateKey = request.ScheduledAt.Date;
        var maxToken = await _db.Appointments
            .Where(a => a.TenantId == TenantId &&
                        a.DoctorId == request.DoctorId &&
                        a.ScheduledAt.Date == dateKey)
            .MaxAsync(a => (int?)a.TokenNumber) ?? 0;

        var apptType = Enum.TryParse<AppointmentType>(
            request.AppointmentType, ignoreCase: true, out var t)
            ? t : AppointmentType.Regular;

        var appt = new Appointment
        {
            TenantId = TenantId,
            PatientId = request.PatientId,
            DoctorId = request.DoctorId,
            ScheduledAt = request.ScheduledAt,
            AppointmentType = apptType,
            Status = AppointmentStatus.Scheduled,
            TokenNumber = maxToken + 1,
            QueuePosition = maxToken + 1,
            IsEmergency = request.IsEmergency,
            Notes = request.Notes,
            CreatedAt = DateTime.UtcNow
        };

        _db.Appointments.Add(appt);
        await _db.SaveChangesAsync();

        await _db.Entry(appt).Reference(a => a.Patient).LoadAsync();
        await _db.Entry(appt).Reference(a => a.Doctor).LoadAsync();

        return CreatedAtAction(nameof(GetAll), new { }, ToResponse(appt));
    }

    [HttpPut("{id:int}/status")]
    public async Task<ActionResult<AppointmentResponse>> UpdateStatus(
        int id, [FromBody] AppointmentUpdateStatusRequest request)
    {
        var appt = await _db.Appointments
            .Include(a => a.Patient)
            .Include(a => a.Doctor)
            .FirstOrDefaultAsync(a => a.Id == id && a.TenantId == TenantId);

        if (appt is null) return NotFound();

        if (!Enum.TryParse<AppointmentStatus>(request.Status, ignoreCase: true, out var status))
            return BadRequest(new { message = $"Unknown status '{request.Status}'." });

        appt.Status = status;
        await _db.SaveChangesAsync();
        return Ok(ToResponse(appt));
    }

    [HttpGet("queue")]
    public async Task<ActionResult<List<QueueEntry>>> GetQueue(
        [FromQuery] int doctorId,
        [FromQuery] DateTime? date)
    {
        var dateKey = (date ?? DateTime.UtcNow).Date;
        var queue = await _db.Appointments
            .Include(a => a.Patient)
            .Where(a => a.TenantId == TenantId &&
                        a.DoctorId == doctorId &&
                        a.ScheduledAt.Date == dateKey &&
                        a.Status != AppointmentStatus.Completed &&
                        a.Status != AppointmentStatus.Cancelled)
            .OrderBy(a => a.IsEmergency ? 0 : 1)
            .ThenBy(a => a.QueuePosition)
            .Select(a => new QueueEntry(
                a.Id, a.PatientId,
                a.Patient != null ? a.Patient.Name : string.Empty,
                a.QueuePosition ?? 0,
                a.TokenNumber,
                a.IsEmergency))
            .ToListAsync();

        return Ok(queue);
    }

    private static AppointmentResponse ToResponse(Appointment a) => new(
        a.Id, a.PatientId,
        a.Patient?.Name ?? string.Empty,
        a.DoctorId,
        a.Doctor?.FullName ?? string.Empty,
        a.ScheduledAt,
        a.AppointmentType.ToString(),
        a.Status.ToString(),
        a.TokenNumber,
        a.QueuePosition,
        a.IsEmergency,
        a.Notes,
        a.CreatedAt);
}
