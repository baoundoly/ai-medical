import 'package:flutter/material.dart';

class AppConstants {
  // API
  static const String baseUrl = 'http://10.0.2.2:5000/api';

  // Secure storage keys
  static const String tokenKey = 'jwt_token';
  static const String userKey = 'user_data';

  // Endpoints
  static const String loginEndpoint = '/auth/login';
  static const String meEndpoint = '/auth/me';
  static const String patientsEndpoint = '/patients';
  static const String patientDuplicateEndpoint = '/patients/check-duplicate';
  static const String visitsEndpoint = '/visits';
  static const String appointmentsEndpoint = '/appointments';
  static const String prescriptionsEndpoint = '/prescriptions';
  static const String labReportsEndpoint = '/lab-reports';
  static const String vitalsEndpoint = '/vitals';
  static const String emrEndpoint = '/emr';

  // Colors
  static const Color primaryColor = Color(0xFF1d4ed8);
  static const Color secondaryColor = Color(0xFF0369a1);
  static const Color successColor = Color(0xFF16a34a);
  static const Color warningColor = Color(0xFFd97706);
  static const Color errorColor = Color(0xFFdc2626);
  static const Color backgroundColor = Color(0xFFF8FAFC);
  static const Color cardColor = Colors.white;
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);

  // Status colors
  static const Color visitBlue = Color(0xFF3B82F6);
  static const Color prescriptionGreen = Color(0xFF22C55E);
  static const Color labOrange = Color(0xFFF97316);
  static const Color vitalPurple = Color(0xFFA855F7);

  // Text styles
  static const TextStyle headingStyle = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.bold,
    color: textPrimary,
  );

  static const TextStyle subheadingStyle = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: textPrimary,
  );

  static const TextStyle bodyStyle = TextStyle(
    fontSize: 14,
    color: textSecondary,
  );

  static const TextStyle captionStyle = TextStyle(
    fontSize: 12,
    color: textSecondary,
  );

  // Roles
  static const String roleDoctor = 'Doctor';
  static const String roleNurse = 'Nurse';
  static const String roleAdmin = 'Admin';
  static const String roleReceptionist = 'Receptionist';

  // Visit statuses
  static const String visitStatusPending = 'Pending';
  static const String visitStatusActive = 'Active';
  static const String visitStatusCompleted = 'Completed';

  // Appointment statuses
  static const String appointmentStatusScheduled = 'Scheduled';
  static const String appointmentStatusCompleted = 'Completed';
  static const String appointmentStatusCancelled = 'Cancelled';
}
