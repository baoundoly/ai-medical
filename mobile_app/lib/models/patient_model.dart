class Patient {
  final int id;
  final String patientUid;
  final String name;
  final String? mobile;
  final String? gender;
  final String? bloodGroup;
  final DateTime? dateOfBirth;
  final String? address;
  final DateTime createdAt;

  const Patient({
    required this.id,
    required this.patientUid,
    required this.name,
    this.mobile,
    this.gender,
    this.bloodGroup,
    this.dateOfBirth,
    this.address,
    required this.createdAt,
  });

  factory Patient.fromJson(Map<String, dynamic> json) {
    return Patient(
      id: json['id'] as int,
      patientUid: (json['patientUid'] ?? json['patient_uid'] ?? '') as String,
      name: json['name'] as String,
      mobile: json['mobile'] as String?,
      gender: json['gender'] as String?,
      bloodGroup: (json['bloodGroup'] ?? json['blood_group']) as String?,
      dateOfBirth: json['dateOfBirth'] != null
          ? DateTime.tryParse(json['dateOfBirth'] as String)
          : json['date_of_birth'] != null
              ? DateTime.tryParse(json['date_of_birth'] as String)
              : null,
      address: json['address'] as String?,
      createdAt: DateTime.parse(
          (json['createdAt'] ?? json['created_at']) as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'patientUid': patientUid,
      'name': name,
      'mobile': mobile,
      'gender': gender,
      'bloodGroup': bloodGroup,
      'dateOfBirth': dateOfBirth?.toIso8601String(),
      'address': address,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  int? get age {
    if (dateOfBirth == null) return null;
    final now = DateTime.now();
    int years = now.year - dateOfBirth!.year;
    if (now.month < dateOfBirth!.month ||
        (now.month == dateOfBirth!.month && now.day < dateOfBirth!.day)) {
      years--;
    }
    return years;
  }
}
