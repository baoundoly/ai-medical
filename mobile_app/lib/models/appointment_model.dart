class Appointment {
  final int id;
  final int patientId;
  final int doctorId;
  final DateTime scheduledAt;
  final String appointmentType;
  final String status;
  final int? tokenNumber;
  final bool isEmergency;

  const Appointment({
    required this.id,
    required this.patientId,
    required this.doctorId,
    required this.scheduledAt,
    required this.appointmentType,
    required this.status,
    this.tokenNumber,
    required this.isEmergency,
  });

  factory Appointment.fromJson(Map<String, dynamic> json) {
    return Appointment(
      id: json['id'] as int,
      patientId: (json['patientId'] ?? json['patient_id']) as int,
      doctorId: (json['doctorId'] ?? json['doctor_id']) as int,
      scheduledAt: DateTime.parse(
          (json['scheduledAt'] ?? json['scheduled_at']) as String),
      appointmentType:
          (json['appointmentType'] ?? json['appointment_type'] ?? 'General')
              as String,
      status: json['status'] as String,
      tokenNumber: (json['tokenNumber'] ?? json['token_number']) as int?,
      isEmergency:
          (json['isEmergency'] ?? json['is_emergency'] ?? false) as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'patientId': patientId,
      'doctorId': doctorId,
      'scheduledAt': scheduledAt.toIso8601String(),
      'appointmentType': appointmentType,
      'status': status,
      'tokenNumber': tokenNumber,
      'isEmergency': isEmergency,
    };
  }

  bool get isScheduled => status == 'Scheduled';
  bool get isCompleted => status == 'Completed';
  bool get isCancelled => status == 'Cancelled';
}
