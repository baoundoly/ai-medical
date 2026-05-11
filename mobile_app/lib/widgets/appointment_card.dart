import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/appointment_model.dart';
import '../core/constants.dart';

class AppointmentCard extends StatelessWidget {
  final Appointment appointment;
  final VoidCallback? onTap;
  final VoidCallback? onCancel;

  const AppointmentCard({
    super.key,
    required this.appointment,
    this.onTap,
    this.onCancel,
  });

  Color _statusColor(String status) {
    switch (status) {
      case 'Scheduled':
        return AppConstants.primaryColor;
      case 'Completed':
        return AppConstants.successColor;
      case 'Cancelled':
        return AppConstants.errorColor;
      default:
        return AppConstants.textSecondary;
    }
  }

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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Token number badge
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: appointment.isEmergency
                      ? AppConstants.errorColor
                      : AppConstants.primaryColor,
                  borderRadius: BorderRadius.circular(10),
                ),
                alignment: Alignment.center,
                child: appointment.isEmergency
                    ? const Icon(Icons.emergency, color: Colors.white, size: 22)
                    : Text(
                        '#${appointment.tokenNumber ?? '--'}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
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
                            appointment.appointmentType,
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                              color: AppConstants.textPrimary,
                            ),
                          ),
                        ),
                        if (appointment.isEmergency)
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppConstants.errorColor.withAlpha(26),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              'EMERGENCY',
                              style: TextStyle(
                                color: AppConstants.errorColor,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.schedule,
                            size: 13, color: AppConstants.textSecondary),
                        const SizedBox(width: 4),
                        Text(
                          DateFormat('dd MMM yyyy, hh:mm a')
                              .format(appointment.scheduledAt),
                          style: AppConstants.captionStyle,
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: _statusColor(appointment.status).withAlpha(26),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        appointment.status,
                        style: TextStyle(
                          color: _statusColor(appointment.status),
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              if (appointment.isScheduled && onCancel != null)
                IconButton(
                  icon: const Icon(Icons.cancel_outlined,
                      color: AppConstants.errorColor, size: 20),
                  onPressed: onCancel,
                  tooltip: 'Cancel',
                ),
            ],
          ),
        ),
      ),
    );
  }
}
