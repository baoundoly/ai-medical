import 'package:flutter/material.dart';

import '../models/patient_model.dart';
import '../core/constants.dart';

class PatientCard extends StatelessWidget {
  final Patient patient;
  final VoidCallback? onTap;

  const PatientCard({
    super.key,
    required this.patient,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              CircleAvatar(
                backgroundColor: AppConstants.primaryColor.withAlpha(26),
                radius: 24,
                child: Text(
                  patient.name.isNotEmpty
                      ? patient.name[0].toUpperCase()
                      : '?',
                  style: const TextStyle(
                    color: AppConstants.primaryColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            patient.name,
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 15,
                              color: AppConstants.textPrimary,
                            ),
                          ),
                        ),
                        if (patient.bloodGroup != null)
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.red.shade50,
                              borderRadius: BorderRadius.circular(6),
                              border: Border.all(color: Colors.red.shade200),
                            ),
                            child: Text(
                              patient.bloodGroup!,
                              style: TextStyle(
                                color: Colors.red.shade700,
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'UID: ${patient.patientUid}',
                      style: const TextStyle(
                        color: AppConstants.primaryColor,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        if (patient.mobile != null) ...[
                          const Icon(Icons.phone,
                              size: 13, color: AppConstants.textSecondary),
                          const SizedBox(width: 4),
                          Text(
                            patient.mobile!,
                            style: AppConstants.captionStyle,
                          ),
                          const SizedBox(width: 12),
                        ],
                        if (patient.gender != null) ...[
                          const Icon(Icons.person_outline,
                              size: 13, color: AppConstants.textSecondary),
                          const SizedBox(width: 4),
                          Text(patient.gender!, style: AppConstants.captionStyle),
                        ],
                        if (patient.age != null) ...[
                          const SizedBox(width: 12),
                          Text(
                            '${patient.age} yrs',
                            style: AppConstants.captionStyle,
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right,
                  color: AppConstants.textSecondary, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
