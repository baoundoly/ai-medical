namespace AIMedical.Api.Models.Entities;

public enum UserRole
{
    SuperAdmin,
    HospitalAdmin,
    Doctor,
    Assistant,
    Receptionist,
    Nurse,
    LabTechnician,
    Pharmacist,
    Patient
}

public class User
{
    public int Id { get; set; }
    public int? TenantId { get; set; }
    public string Email { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public UserRole Role { get; set; }
    public bool IsActive { get; set; } = true;
    public bool MfaEnabled { get; set; } = false;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public Tenant? Tenant { get; set; }
}
