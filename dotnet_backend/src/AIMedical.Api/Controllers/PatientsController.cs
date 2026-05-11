using AIMedical.Api.Models.DTOs;
using AIMedical.Api.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace AIMedical.Api.Controllers;

[ApiController]
[Route("api/patients")]
[Authorize]
public class PatientsController : ControllerBase
{
    private readonly IPatientService _patients;

    public PatientsController(IPatientService patients)
    {
        _patients = patients;
    }

    private int TenantId => int.Parse(
        User.FindFirstValue("tenantId") ?? throw new UnauthorizedAccessException("tenantId claim missing"));

    [HttpGet]
    public async Task<ActionResult<PagedResponse<PatientResponse>>> GetAll(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        [FromQuery] string? search = null)
    {
        var result = await _patients.GetPatientsAsync(TenantId, page, pageSize, search);
        return Ok(result);
    }

    [HttpPost]
    public async Task<ActionResult<PatientResponse>> Create([FromBody] PatientCreateRequest request)
    {
        var patient = await _patients.CreatePatientAsync(TenantId, request);
        return CreatedAtAction(nameof(GetById), new { id = patient.Id }, patient);
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<PatientResponse>> GetById(int id)
    {
        var patient = await _patients.GetPatientByIdAsync(TenantId, id);
        if (patient is null) return NotFound();
        return Ok(patient);
    }

    [HttpPut("{id:int}")]
    public async Task<ActionResult<PatientResponse>> Update(
        int id, [FromBody] PatientUpdateRequest request)
    {
        var patient = await _patients.UpdatePatientAsync(TenantId, id, request);
        if (patient is null) return NotFound();
        return Ok(patient);
    }

    [HttpPost("check-duplicate")]
    public async Task<ActionResult<DuplicateCheckResponse>> CheckDuplicate(
        [FromBody] DuplicateCheckRequest request)
    {
        var result = await _patients.CheckDuplicatesAsync(TenantId, request);
        return Ok(result);
    }
}
