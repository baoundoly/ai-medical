using AIMedical.Api.Data;
using AIMedical.Api.Models.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/billing")]
[Authorize]
public class BillingController : ControllerBase
{
    private readonly AppDbContext _db;

    public BillingController(AppDbContext db)
    {
        _db = db;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    [HttpGet("invoices")]
    public async Task<ActionResult> GetInvoices(
        [FromQuery] int? patientId,
        [FromQuery] string? status,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var query = _db.Invoices
            .Include(i => i.Patient)
            .Where(i => i.TenantId == TenantId);

        if (patientId.HasValue) query = query.Where(i => i.PatientId == patientId.Value);
        if (!string.IsNullOrWhiteSpace(status) &&
            Enum.TryParse<InvoiceStatus>(status, ignoreCase: true, out var s))
            query = query.Where(i => i.Status == s);

        var total = await query.CountAsync();
        var items = await query
            .OrderByDescending(i => i.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .Select(i => new
            {
                i.Id, i.PatientId,
                PatientName = i.Patient != null ? i.Patient.Name : string.Empty,
                i.VisitId, i.TotalAmount, i.Discount, i.TaxAmount, i.NetAmount,
                Status = i.Status.ToString(), i.PaymentMethod, i.CreatedAt
            })
            .ToListAsync();

        return Ok(new { Items = items, TotalCount = total, Page = page, PageSize = pageSize });
    }

    [HttpPost("invoices")]
    public async Task<ActionResult> CreateInvoice([FromBody] InvoiceCreateRequest request)
    {
        var netAmount = request.TotalAmount - request.Discount + request.TaxAmount;

        var invoice = new Invoice
        {
            TenantId = TenantId,
            PatientId = request.PatientId,
            VisitId = request.VisitId,
            TotalAmount = request.TotalAmount,
            Discount = request.Discount,
            TaxAmount = request.TaxAmount,
            NetAmount = netAmount,
            Status = InvoiceStatus.Pending,
            CreatedAt = DateTime.UtcNow
        };

        _db.Invoices.Add(invoice);
        await _db.SaveChangesAsync();
        return StatusCode(201, new { invoice.Id, invoice.NetAmount, Status = invoice.Status.ToString() });
    }

    [HttpPost("payments")]
    public async Task<ActionResult> RecordPayment([FromBody] PaymentRequest request)
    {
        var invoice = await _db.Invoices
            .FirstOrDefaultAsync(i => i.Id == request.InvoiceId && i.TenantId == TenantId);

        if (invoice is null) return NotFound(new { message = "Invoice not found." });

        invoice.Status = InvoiceStatus.Paid;
        invoice.PaymentMethod = request.PaymentMethod;
        await _db.SaveChangesAsync();

        return Ok(new { invoice.Id, Status = invoice.Status.ToString(), invoice.PaymentMethod });
    }
}

public record InvoiceCreateRequest(
    [Required] int PatientId,
    int? VisitId,
    [Required][Range(0, double.MaxValue)] decimal TotalAmount,
    decimal Discount = 0,
    decimal TaxAmount = 0
);

public record PaymentRequest(
    [Required] int InvoiceId,
    [Required] string PaymentMethod
);
