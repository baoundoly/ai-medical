namespace AIMedical.Api.Models.Entities;

public class LabReport
{
    public int Id { get; set; }
    public int VisitId { get; set; }
    public int PatientId { get; set; }
    public int UploadedById { get; set; }
    public string ReportType { get; set; } = string.Empty;
    public string FileUrl { get; set; } = string.Empty;
    public string? OcrText { get; set; }
    public string? AiAnalysis { get; set; }
    public bool IsCritical { get; set; } = false;
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public Visit? Visit { get; set; }
    public Patient? Patient { get; set; }
    public User? UploadedBy { get; set; }
}
