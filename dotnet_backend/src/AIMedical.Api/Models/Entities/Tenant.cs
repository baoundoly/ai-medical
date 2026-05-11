namespace AIMedical.Api.Models.Entities;

public class Tenant
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Code { get; set; } = string.Empty;
    public string? Address { get; set; }
    public string SubscriptionPlan { get; set; } = "Basic";
    public bool IsActive { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public ICollection<User> Users { get; set; } = [];
    public ICollection<Patient> Patients { get; set; } = [];
}
