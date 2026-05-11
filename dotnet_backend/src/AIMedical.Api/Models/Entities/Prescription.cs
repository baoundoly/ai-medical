namespace AIMedical.Api.Models.Entities;

public enum PrescriptionStatus
{
    Draft,
    Signed,
    Dispensed,
    Cancelled
}

public enum SignatureMethod
{
    Digital,
    Manual
}

public class Prescription
{
    public int Id { get; set; }
    public int VisitId { get; set; }
    public int PatientId { get; set; }
    public int DoctorId { get; set; }
    public PrescriptionStatus Status { get; set; } = PrescriptionStatus.Draft;
    public DateTime? SignedAt { get; set; }
    public SignatureMethod? SignatureMethod { get; set; }
    public string? DigitalSignatureHash { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public Visit? Visit { get; set; }
    public Patient? Patient { get; set; }
    public User? Doctor { get; set; }
    public ICollection<PrescriptionItem> Items { get; set; } = [];
}

public class PrescriptionItem
{
    public int Id { get; set; }
    public int PrescriptionId { get; set; }
    public string MedicineName { get; set; } = string.Empty;
    public string Dosage { get; set; } = string.Empty;
    public string Frequency { get; set; } = string.Empty;
    public string Duration { get; set; } = string.Empty;
    public string? MealInstruction { get; set; }

    // Navigation
    public Prescription? Prescription { get; set; }
}
