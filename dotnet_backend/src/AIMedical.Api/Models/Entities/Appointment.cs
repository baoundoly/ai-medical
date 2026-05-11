namespace AIMedical.Api.Models.Entities;

public enum AppointmentStatus
{
    Scheduled,
    Confirmed,
    Waiting,
    InProgress,
    Completed,
    Cancelled,
    NoShow
}

public enum AppointmentType
{
    Regular,
    Emergency,
    FollowUp,
    Telemedicine
}

public class Appointment
{
    public int Id { get; set; }
    public int TenantId { get; set; }
    public int PatientId { get; set; }
    public int DoctorId { get; set; }
    public DateTime ScheduledAt { get; set; }
    public AppointmentType AppointmentType { get; set; } = AppointmentType.Regular;
    public AppointmentStatus Status { get; set; } = AppointmentStatus.Scheduled;
    public int? TokenNumber { get; set; }
    public int? QueuePosition { get; set; }
    public bool IsEmergency { get; set; } = false;
    public string? Notes { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public Patient? Patient { get; set; }
    public User? Doctor { get; set; }
}
