namespace AIMedical.Api.Models.Entities;

public class Medicine
{
    public int Id { get; set; }
    public int TenantId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? GenericName { get; set; }
    public string? Strength { get; set; }
    public string? Form { get; set; }
    public int StockQuantity { get; set; } = 0;
    public decimal UnitPrice { get; set; }
    public DateTime? ExpiryDate { get; set; }
    public string? Barcode { get; set; }
    public int ReorderLevel { get; set; } = 10;

    // Navigation
    public Tenant? Tenant { get; set; }
}
