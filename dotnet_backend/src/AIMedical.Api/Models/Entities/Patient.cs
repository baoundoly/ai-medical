namespace AIMedical.Api.Models.Entities;

public class Patient
{
    public int Id { get; set; }
    public int TenantId { get; set; }
    public string PatientUid { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Mobile { get; set; }
    public string? Nid { get; set; }
    public DateTime? DateOfBirth { get; set; }
    public string? Gender { get; set; }
    public string? BloodGroup { get; set; }
    public string? Address { get; set; }
    public string? EmergencyContactName { get; set; }
    public string? EmergencyContactPhone { get; set; }
    public bool IsActive { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public Tenant? Tenant { get; set; }
    public ICollection<Visit> Visits { get; set; } = [];
    public ICollection<Appointment> Appointments { get; set; } = [];
}
