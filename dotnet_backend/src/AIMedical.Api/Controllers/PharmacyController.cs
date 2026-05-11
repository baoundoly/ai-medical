using AIMedical.Api.Data;
using AIMedical.Api.Models.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.ComponentModel.DataAnnotations;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/pharmacy")]
[Authorize]
public class PharmacyController : ControllerBase
{
    private readonly AppDbContext _db;

    public PharmacyController(AppDbContext db)
    {
        _db = db;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    [HttpGet("medicines")]
    public async Task<ActionResult> GetMedicines(
        [FromQuery] string? search,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var query = _db.Medicines.Where(m => m.TenantId == TenantId);

        if (!string.IsNullOrWhiteSpace(search))
        {
            var term = search.ToLower();
            query = query.Where(m =>
                m.Name.ToLower().Contains(term) ||
                (m.GenericName != null && m.GenericName.ToLower().Contains(term)));
        }

        var total = await query.CountAsync();
        var items = await query
            .OrderBy(m => m.Name)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return Ok(new { Items = items, TotalCount = total, Page = page, PageSize = pageSize });
    }

    [HttpPost("medicines")]
    [Authorize(Roles = "Pharmacist,HospitalAdmin,SuperAdmin")]
    public async Task<ActionResult> AddMedicine([FromBody] MedicineCreateRequest request)
    {
        var medicine = new Medicine
        {
            TenantId = TenantId,
            Name = request.Name,
            GenericName = request.GenericName,
            Strength = request.Strength,
            Form = request.Form,
            StockQuantity = request.StockQuantity,
            UnitPrice = request.UnitPrice,
            ExpiryDate = request.ExpiryDate,
            Barcode = request.Barcode,
            ReorderLevel = request.ReorderLevel
        };

        _db.Medicines.Add(medicine);
        await _db.SaveChangesAsync();
        return StatusCode(201, medicine);
    }

    [HttpPut("medicines/{id:int}/stock")]
    [Authorize(Roles = "Pharmacist,HospitalAdmin,SuperAdmin")]
    public async Task<ActionResult> UpdateStock(int id, [FromBody] StockUpdateRequest request)
    {
        var medicine = await _db.Medicines
            .FirstOrDefaultAsync(m => m.Id == id && m.TenantId == TenantId);

        if (medicine is null) return NotFound();

        medicine.StockQuantity = request.Quantity;
        await _db.SaveChangesAsync();

        return Ok(new { medicine.Id, medicine.Name, medicine.StockQuantity });
    }

    [HttpPost("dispense")]
    [Authorize(Roles = "Pharmacist,HospitalAdmin,SuperAdmin")]
    public async Task<ActionResult> Dispense([FromBody] DispenseRequest request)
    {
        var medicine = await _db.Medicines
            .FirstOrDefaultAsync(m => m.Id == request.MedicineId && m.TenantId == TenantId);

        if (medicine is null) return NotFound(new { message = "Medicine not found." });
        if (medicine.StockQuantity < request.Quantity)
            return UnprocessableEntity(new { message = "Insufficient stock." });

        medicine.StockQuantity -= request.Quantity;

        // Update prescription status to Dispensed
        if (request.PrescriptionId.HasValue)
        {
            var rx = await _db.Prescriptions.FindAsync(request.PrescriptionId.Value);
            if (rx != null && rx.Status == PrescriptionStatus.Signed)
                rx.Status = PrescriptionStatus.Dispensed;
        }

        await _db.SaveChangesAsync();
        return Ok(new { medicine.Id, medicine.Name, RemainingStock = medicine.StockQuantity });
    }
}

public record MedicineCreateRequest(
    [Required] string Name,
    string? GenericName,
    string? Strength,
    string? Form,
    int StockQuantity,
    decimal UnitPrice,
    DateTime? ExpiryDate,
    string? Barcode,
    int ReorderLevel = 10
);

public record StockUpdateRequest([Required][Range(0, int.MaxValue)] int Quantity);

public record DispenseRequest(
    [Required] int MedicineId,
    [Required][Range(1, int.MaxValue)] int Quantity,
    int? PrescriptionId
);
