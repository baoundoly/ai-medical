namespace AIMedical.Api.Models.Entities;

public enum InvoiceStatus
{
    Draft,
    Pending,
    Paid,
    PartiallyPaid,
    Cancelled
}

public class Invoice
{
    public int Id { get; set; }
    public int TenantId { get; set; }
    public int PatientId { get; set; }
    public int? VisitId { get; set; }
    public decimal TotalAmount { get; set; }
    public decimal Discount { get; set; } = 0;
    public decimal TaxAmount { get; set; } = 0;
    public decimal NetAmount { get; set; }
    public InvoiceStatus Status { get; set; } = InvoiceStatus.Pending;
    public string? PaymentMethod { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public Patient? Patient { get; set; }
    public Visit? Visit { get; set; }
    public Tenant? Tenant { get; set; }
}
