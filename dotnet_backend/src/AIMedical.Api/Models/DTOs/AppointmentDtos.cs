using System.ComponentModel.DataAnnotations;

namespace AIMedical.Api.Models.DTOs;

public record AppointmentCreateRequest(
    [Required] int PatientId,
    [Required] int DoctorId,
    [Required] DateTime ScheduledAt,
    string? AppointmentType,
    bool IsEmergency = false,
    string? Notes = null
);

public record AppointmentUpdateStatusRequest([Required] string Status);

public record AppointmentResponse(
    int Id,
    int PatientId,
    string PatientName,
    int DoctorId,
    string DoctorName,
    DateTime ScheduledAt,
    string AppointmentType,
    string Status,
    int? TokenNumber,
    int? QueuePosition,
    bool IsEmergency,
    string? Notes,
    DateTime CreatedAt
);

public record QueueEntry(
    int AppointmentId,
    int PatientId,
    string PatientName,
    int QueuePosition,
    int? TokenNumber,
    bool IsEmergency
);
