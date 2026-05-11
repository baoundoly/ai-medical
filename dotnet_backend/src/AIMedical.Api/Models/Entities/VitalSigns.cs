namespace AIMedical.Api.Models.Entities;

public class VitalSigns
{
    public int Id { get; set; }
    public int VisitId { get; set; }
    public int PatientId { get; set; }
    public int RecordedById { get; set; }
    public int? BpSystolic { get; set; }
    public int? BpDiastolic { get; set; }
    public int? Pulse { get; set; }
    public decimal? Temperature { get; set; }
    public int? Spo2 { get; set; }
    public decimal? Weight { get; set; }
    public decimal? Height { get; set; }
    public decimal? Bmi { get; set; }
    public int? RespiratoryRate { get; set; }
    public string? Consciousness { get; set; }
    public DateTime RecordedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public Visit? Visit { get; set; }
    public Patient? Patient { get; set; }
    public User? RecordedBy { get; set; }
    public NewsScore? NewsScore { get; set; }
}

public class NewsScore
{
    public int Id { get; set; }
    public int VitalId { get; set; }
    public int Score { get; set; }
    public string RiskLevel { get; set; } = string.Empty;
    public DateTime CalculatedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public VitalSigns? Vital { get; set; }
}
