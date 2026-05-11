import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/visit_model.dart';
import '../core/constants.dart';

class VisitCard extends StatelessWidget {
  final Visit visit;
  final VoidCallback? onTap;

  const VisitCard({super.key, required this.visit, this.onTap});

  Color _statusColor(String status) {
    switch (status) {
      case 'Active':
        return AppConstants.successColor;
      case 'Completed':
        return AppConstants.textSecondary;
      case 'Pending':
        return AppConstants.warningColor;
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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.medical_services_outlined,
                      color: AppConstants.visitBlue, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      visit.chiefComplaint ?? 'No chief complaint',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: AppConstants.textPrimary,
                      ),
                    ),
                  ),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                    decoration: BoxDecoration(
                      color: _statusColor(visit.status).withAlpha(26),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      visit.status,
                      style: TextStyle(
                        color: _statusColor(visit.status),
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.calendar_today,
                      size: 13, color: AppConstants.textSecondary),
                  const SizedBox(width: 4),
                  Text(
                    DateFormat('dd MMM yyyy, hh:mm a').format(visit.visitDate),
                    style: AppConstants.captionStyle,
                  ),
                  if (visit.isApproved) ...[
                    const SizedBox(width: 12),
                    const Icon(Icons.check_circle,
                        size: 13, color: AppConstants.successColor),
                    const SizedBox(width: 4),
                    const Text(
                      'Approved',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppConstants.successColor,
                      ),
                    ),
                  ],
                ],
              ),
              if (visit.aiSummary != null) ...[
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppConstants.visitBlue.withAlpha(13),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                        color: AppConstants.visitBlue.withAlpha(51)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.auto_awesome,
                          size: 14, color: AppConstants.visitBlue),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          visit.aiSummary!,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppConstants.visitBlue,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
