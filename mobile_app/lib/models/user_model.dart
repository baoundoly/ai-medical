class User {
  final int id;
  final String email;
  final String fullName;
  final String role;
  final int? tenantId;

  const User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    this.tenantId,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      email: json['email'] as String,
      fullName: (json['fullName'] ?? json['full_name'] ?? '') as String,
      role: json['role'] as String,
      tenantId: json['tenantId'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'fullName': fullName,
      'role': role,
      'tenantId': tenantId,
    };
  }

  bool get isDoctor => role == 'Doctor';
  bool get isAdmin => role == 'Admin';
  bool get isNurse => role == 'Nurse';
  bool get isReceptionist => role == 'Receptionist';
}
