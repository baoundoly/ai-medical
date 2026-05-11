class PrescriptionItem {
  final int id;
  final String medicineName;
  final String? dosage;
  final String? frequency;
  final String? duration;
  final String? mealInstruction;

  const PrescriptionItem({
    required this.id,
    required this.medicineName,
    this.dosage,
    this.frequency,
    this.duration,
    this.mealInstruction,
  });

  factory PrescriptionItem.fromJson(Map<String, dynamic> json) {
    return PrescriptionItem(
      id: json['id'] as int,
      medicineName:
          (json['medicineName'] ?? json['medicine_name'] ?? '') as String,
      dosage: json['dosage'] as String?,
      frequency: json['frequency'] as String?,
      duration: json['duration'] as String?,
      mealInstruction:
          (json['mealInstruction'] ?? json['meal_instruction']) as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'medicineName': medicineName,
      'dosage': dosage,
      'frequency': frequency,
      'duration': duration,
      'mealInstruction': mealInstruction,
    };
  }
}

class Prescription {
  final int id;
  final int visitId;
  final String status;
  final DateTime? signedAt;
  final List<PrescriptionItem> items;

  const Prescription({
    required this.id,
    required this.visitId,
    required this.status,
    this.signedAt,
    required this.items,
  });

  factory Prescription.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? [];
    return Prescription(
      id: json['id'] as int,
      visitId: (json['visitId'] ?? json['visit_id']) as int,
      status: json['status'] as String,
      signedAt: json['signedAt'] != null
          ? DateTime.tryParse(json['signedAt'] as String)
          : json['signed_at'] != null
              ? DateTime.tryParse(json['signed_at'] as String)
              : null,
      items: rawItems
          .map((e) => PrescriptionItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'visitId': visitId,
      'status': status,
      'signedAt': signedAt?.toIso8601String(),
      'items': items.map((e) => e.toJson()).toList(),
    };
  }

  bool get isSigned => signedAt != null;
  bool get isDraft => status == 'Draft';
}
