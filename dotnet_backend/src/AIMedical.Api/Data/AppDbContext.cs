using AIMedical.Api.Models.Entities;
using Microsoft.EntityFrameworkCore;

namespace AIMedical.Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Tenant> Tenants => Set<Tenant>();
    public DbSet<User> Users => Set<User>();
    public DbSet<Patient> Patients => Set<Patient>();
    public DbSet<Visit> Visits => Set<Visit>();
    public DbSet<Appointment> Appointments => Set<Appointment>();
    public DbSet<Prescription> Prescriptions => Set<Prescription>();
    public DbSet<PrescriptionItem> PrescriptionItems => Set<PrescriptionItem>();
    public DbSet<LabReport> LabReports => Set<LabReport>();
    public DbSet<VitalSigns> VitalSigns => Set<VitalSigns>();
    public DbSet<NewsScore> NewsScores => Set<NewsScore>();
    public DbSet<AuditLog> AuditLogs => Set<AuditLog>();
    public DbSet<Medicine> Medicines => Set<Medicine>();
    public DbSet<Invoice> Invoices => Set<Invoice>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Tenant
        modelBuilder.Entity<Tenant>(e =>
        {
            e.HasKey(t => t.Id);
            e.HasIndex(t => t.Code).IsUnique();
            e.Property(t => t.SubscriptionPlan).HasDefaultValue("Basic");
        });

        // User
        modelBuilder.Entity<User>(e =>
        {
            e.HasKey(u => u.Id);
            e.HasIndex(u => u.Email).IsUnique();
            e.Property(u => u.Role).HasConversion<string>();
            e.HasOne(u => u.Tenant)
             .WithMany(t => t.Users)
             .HasForeignKey(u => u.TenantId)
             .OnDelete(DeleteBehavior.Restrict)
             .IsRequired(false);
        });

        // Patient
        modelBuilder.Entity<Patient>(e =>
        {
            e.HasKey(p => p.Id);
            e.HasIndex(p => p.PatientUid).IsUnique();
            e.HasIndex(p => new { p.TenantId, p.Mobile });
            e.HasOne(p => p.Tenant)
             .WithMany(t => t.Patients)
             .HasForeignKey(p => p.TenantId)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // Visit
        modelBuilder.Entity<Visit>(e =>
        {
            e.HasKey(v => v.Id);
            e.Property(v => v.Status).HasConversion<string>();
            e.HasOne(v => v.Patient)
             .WithMany(p => p.Visits)
             .HasForeignKey(v => v.PatientId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(v => v.Doctor)
             .WithMany()
             .HasForeignKey(v => v.DoctorId)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // Appointment
        modelBuilder.Entity<Appointment>(e =>
        {
            e.HasKey(a => a.Id);
            e.Property(a => a.Status).HasConversion<string>();
            e.Property(a => a.AppointmentType).HasConversion<string>();
            e.HasOne(a => a.Patient)
             .WithMany(p => p.Appointments)
             .HasForeignKey(a => a.PatientId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(a => a.Doctor)
             .WithMany()
             .HasForeignKey(a => a.DoctorId)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // Prescription
        modelBuilder.Entity<Prescription>(e =>
        {
            e.HasKey(p => p.Id);
            e.Property(p => p.Status).HasConversion<string>();
            e.Property(p => p.SignatureMethod).HasConversion<string>();
            e.HasOne(p => p.Visit)
             .WithMany(v => v.Prescriptions)
             .HasForeignKey(p => p.VisitId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(p => p.Doctor)
             .WithMany()
             .HasForeignKey(p => p.DoctorId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(p => p.Patient)
             .WithMany()
             .HasForeignKey(p => p.PatientId)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // PrescriptionItem
        modelBuilder.Entity<PrescriptionItem>(e =>
        {
            e.HasKey(pi => pi.Id);
            e.HasOne(pi => pi.Prescription)
             .WithMany(p => p.Items)
             .HasForeignKey(pi => pi.PrescriptionId)
             .OnDelete(DeleteBehavior.Cascade);
        });

        // LabReport
        modelBuilder.Entity<LabReport>(e =>
        {
            e.HasKey(lr => lr.Id);
            e.HasOne(lr => lr.Visit)
             .WithMany(v => v.LabReports)
             .HasForeignKey(lr => lr.VisitId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(lr => lr.Patient)
             .WithMany()
             .HasForeignKey(lr => lr.PatientId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(lr => lr.UploadedBy)
             .WithMany()
             .HasForeignKey(lr => lr.UploadedById)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // VitalSigns
        modelBuilder.Entity<VitalSigns>(e =>
        {
            e.HasKey(vs => vs.Id);
            e.Property(vs => vs.Temperature).HasColumnType("decimal(5,2)");
            e.Property(vs => vs.Weight).HasColumnType("decimal(6,2)");
            e.Property(vs => vs.Height).HasColumnType("decimal(5,2)");
            e.Property(vs => vs.Bmi).HasColumnType("decimal(5,2)");
            e.HasOne(vs => vs.Visit)
             .WithMany(v => v.VitalSigns)
             .HasForeignKey(vs => vs.VisitId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(vs => vs.Patient)
             .WithMany()
             .HasForeignKey(vs => vs.PatientId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(vs => vs.RecordedBy)
             .WithMany()
             .HasForeignKey(vs => vs.RecordedById)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // NewsScore
        modelBuilder.Entity<NewsScore>(e =>
        {
            e.HasKey(ns => ns.Id);
            e.HasOne(ns => ns.Vital)
             .WithOne(vs => vs.NewsScore)
             .HasForeignKey<NewsScore>(ns => ns.VitalId)
             .OnDelete(DeleteBehavior.Cascade);
        });

        // AuditLog
        modelBuilder.Entity<AuditLog>(e =>
        {
            e.HasKey(al => al.Id);
            e.HasIndex(al => new { al.TenantId, al.Timestamp });
        });

        // Medicine
        modelBuilder.Entity<Medicine>(e =>
        {
            e.HasKey(m => m.Id);
            e.Property(m => m.UnitPrice).HasColumnType("decimal(10,2)");
            e.HasOne(m => m.Tenant)
             .WithMany()
             .HasForeignKey(m => m.TenantId)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // Invoice
        modelBuilder.Entity<Invoice>(e =>
        {
            e.HasKey(i => i.Id);
            e.Property(i => i.TotalAmount).HasColumnType("decimal(12,2)");
            e.Property(i => i.Discount).HasColumnType("decimal(12,2)");
            e.Property(i => i.TaxAmount).HasColumnType("decimal(12,2)");
            e.Property(i => i.NetAmount).HasColumnType("decimal(12,2)");
            e.Property(i => i.Status).HasConversion<string>();
            e.HasOne(i => i.Patient)
             .WithMany()
             .HasForeignKey(i => i.PatientId)
             .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(i => i.Tenant)
             .WithMany()
             .HasForeignKey(i => i.TenantId)
             .OnDelete(DeleteBehavior.Restrict);
        });
    }
}
