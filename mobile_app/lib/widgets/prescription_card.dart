import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/prescription_model.dart';
import '../core/constants.dart';

class PrescriptionCard extends StatelessWidget {
  final Prescription prescription;
  final VoidCallback? onSign;
  final bool showSignButton;

  const PrescriptionCard({
    super.key,
    required this.prescription,
    this.onSign,
    this.showSignButton = false,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.description_outlined,
                    color: AppConstants.prescriptionGreen, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Prescription #${prescription.id}',
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 15,
                    color: AppConstants.textPrimary,
                  ),
                ),
                const Spacer(),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                  decoration: BoxDecoration(
                    color: prescription.isSigned
                        ? AppConstants.successColor.withAlpha(26)
                        : AppConstants.warningColor.withAlpha(26),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    prescription.status,
                    style: TextStyle(
                      color: prescription.isSigned
                          ? AppConstants.successColor
                          : AppConstants.warningColor,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            if (prescription.signedAt != null) ...[
              const SizedBox(height: 4),
              Text(
                'Signed: ${DateFormat('dd MMM yyyy').format(prescription.signedAt!)}',
                style: const TextStyle(
                    fontSize: 12, color: AppConstants.successColor),
              ),
            ],
            const Divider(height: 16),
            ...prescription.items.map((item) => _MedicineItemRow(item: item)),
            if (showSignButton && !prescription.isSigned) ...[
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: onSign,
                  icon: const Icon(Icons.edit, size: 16),
                  label: const Text('Sign Prescription'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppConstants.prescriptionGreen,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _MedicineItemRow extends StatelessWidget {
  final PrescriptionItem item;

  const _MedicineItemRow({required this.item});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.medication_outlined,
              size: 16, color: AppConstants.prescriptionGreen),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.medicineName,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                    color: AppConstants.textPrimary,
                  ),
                ),
                const SizedBox(height: 2),
                Wrap(
                  spacing: 8,
                  children: [
                    if (item.dosage != null)
                      _InfoChip(icon: Icons.scale, text: item.dosage!),
                    if (item.frequency != null)
                      _InfoChip(icon: Icons.repeat, text: item.frequency!),
                    if (item.duration != null)
                      _InfoChip(icon: Icons.timer_outlined, text: item.duration!),
                    if (item.mealInstruction != null)
                      _InfoChip(
                          icon: Icons.restaurant, text: item.mealInstruction!),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String text;

  const _InfoChip({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 11, color: AppConstants.textSecondary),
        const SizedBox(width: 3),
        Text(text, style: AppConstants.captionStyle),
      ],
    );
  }
}
