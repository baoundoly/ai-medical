class Visit {
  final int id;
  final int patientId;
  final int? doctorId;
  final DateTime visitDate;
  final String status;
  final String? chiefComplaint;
  final String? aiSummary;
  final DateTime? doctorApprovedAt;

  const Visit({
    required this.id,
    required this.patientId,
    this.doctorId,
    required this.visitDate,
    required this.status,
    this.chiefComplaint,
    this.aiSummary,
    this.doctorApprovedAt,
  });

  factory Visit.fromJson(Map<String, dynamic> json) {
    return Visit(
      id: json['id'] as int,
      patientId: (json['patientId'] ?? json['patient_id']) as int,
      doctorId: (json['doctorId'] ?? json['doctor_id']) as int?,
      visitDate: DateTime.parse(
          (json['visitDate'] ?? json['visit_date']) as String),
      status: json['status'] as String,
      chiefComplaint:
          (json['chiefComplaint'] ?? json['chief_complaint']) as String?,
      aiSummary: (json['aiSummary'] ?? json['ai_summary']) as String?,
      doctorApprovedAt: json['doctorApprovedAt'] != null
          ? DateTime.tryParse(json['doctorApprovedAt'] as String)
          : json['doctor_approved_at'] != null
              ? DateTime.tryParse(json['doctor_approved_at'] as String)
              : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'patientId': patientId,
      'doctorId': doctorId,
      'visitDate': visitDate.toIso8601String(),
      'status': status,
      'chiefComplaint': chiefComplaint,
      'aiSummary': aiSummary,
      'doctorApprovedAt': doctorApprovedAt?.toIso8601String(),
    };
  }

  bool get isPending => status == 'Pending';
  bool get isActive => status == 'Active';
  bool get isCompleted => status == 'Completed';
  bool get isApproved => doctorApprovedAt != null;
}
