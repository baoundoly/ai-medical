namespace AIMedical.Api.Models.Entities;

public enum VisitStatus
{
    Scheduled,
    InProgress,
    Completed,
    Cancelled
}

public class Visit
{
    public int Id { get; set; }
    public int TenantId { get; set; }
    public int PatientId { get; set; }
    public int DoctorId { get; set; }
    public int? AssistantId { get; set; }
    public DateTime VisitDate { get; set; } = DateTime.UtcNow;
    public VisitStatus Status { get; set; } = VisitStatus.InProgress;
    public string? ChiefComplaint { get; set; }
    public string? Hpi { get; set; }
    public string? Ros { get; set; }
    public string? PastHistory { get; set; }
    public string? FamilyHistory { get; set; }
    public string? SocialHistory { get; set; }
    public string? AiSummary { get; set; }
    public DateTime? DoctorApprovedAt { get; set; }
    public int? DoctorApprovedBy { get; set; }

    // Navigation
    public Patient? Patient { get; set; }
    public User? Doctor { get; set; }
    public ICollection<Prescription> Prescriptions { get; set; } = [];
    public ICollection<LabReport> LabReports { get; set; } = [];
    public ICollection<VitalSigns> VitalSigns { get; set; } = [];
}
