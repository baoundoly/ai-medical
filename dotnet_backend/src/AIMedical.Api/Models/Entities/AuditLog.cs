namespace AIMedical.Api.Models.Entities;

public class AuditLog
{
    public long Id { get; set; }
    public int? TenantId { get; set; }
    public int? UserId { get; set; }
    public string Action { get; set; } = string.Empty;
    public string ResourceType { get; set; } = string.Empty;
    public string? ResourceId { get; set; }
    public string? OldValueJson { get; set; }
    public string? NewValueJson { get; set; }
    public string? IpAddress { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}
