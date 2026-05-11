import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../providers/visit_provider.dart';
import '../providers/prescription_provider.dart';
import '../providers/auth_provider.dart';
import '../models/visit_model.dart';
import '../widgets/prescription_card.dart';
import '../widgets/loading_widget.dart';
import '../core/constants.dart';

class VisitDetailScreen extends StatefulWidget {
  final int visitId;

  const VisitDetailScreen({super.key, required this.visitId});

  @override
  State<VisitDetailScreen> createState() => _VisitDetailScreenState();
}

class _VisitDetailScreenState extends State<VisitDetailScreen> {
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    await context.read<VisitProvider>().fetchVisitById(widget.visitId);
    final visit = context.read<VisitProvider>().selectedVisit;
    if (visit != null) {
      await context
          .read<PrescriptionProvider>()
          .fetchPrescriptions(visitId: widget.visitId);
    }
    setState(() => _loading = false);
  }

  Future<void> _approveVisit() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Approve Visit'),
        content: const Text(
            'Are you sure you want to approve and complete this visit?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Approve'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    final error = await context.read<VisitProvider>().approveVisit(widget.visitId);
    if (!mounted) return;
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text(error), backgroundColor: AppConstants.errorColor),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Visit approved successfully'),
          backgroundColor: AppConstants.successColor,
        ),
      );
      await _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new, size: 20),
            onPressed: () => context.pop(),
          ),
          title: const Text('Visit Detail'),
        ),
        body: const LoadingWidget(),
      );
    }

    final visit = context.watch<VisitProvider>().selectedVisit;
    final prescriptions = context.watch<PrescriptionProvider>().prescriptions;
    final authUser = context.watch<AuthProvider>().user;
    final isDoctor = authUser?.isDoctor ?? false;

    if (visit == null) {
      return Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new, size: 20),
            onPressed: () => context.pop(),
          ),
          title: const Text('Visit Detail'),
        ),
        body: const Center(child: Text('Visit not found')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
        title: const Text('Visit Detail'),
        actions: [
          if (isDoctor && !visit.isApproved)
            TextButton(
              onPressed: _approveVisit,
              child: const Text('Approve',
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _StatusBanner(visit: visit),
              const SizedBox(height: 16),
              _InfoSection(visit: visit),
              if (visit.aiSummary != null) ...[
                const SizedBox(height: 16),
                _AiSummaryBox(summary: visit.aiSummary!),
              ],
              const SizedBox(height: 16),
              _SectionTitle(title: 'Prescriptions (${prescriptions.length})'),
              const SizedBox(height: 8),
              if (prescriptions.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 20),
                  child: Center(
                    child: Text('No prescriptions', style: AppConstants.bodyStyle),
                  ),
                )
              else
                ...prescriptions.map(
                  (rx) => PrescriptionCard(
                    prescription: rx,
                    showSignButton: isDoctor,
                    onSign: () => _showSignDialog(rx.id),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  void _showSignDialog(int prescriptionId) {
    final passCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Sign Prescription'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Enter your password to sign:'),
            const SizedBox(height: 12),
            TextField(
              controller: passCtrl,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Password',
                prefixIcon: Icon(Icons.lock_outline),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final error = await context
                  .read<PrescriptionProvider>()
                  .signPrescription(prescriptionId, passCtrl.text);
              if (!mounted) return;
              if (error != null) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                      content: Text(error),
                      backgroundColor: AppConstants.errorColor),
                );
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Prescription signed'),
                    backgroundColor: AppConstants.successColor,
                  ),
                );
              }
            },
            child: const Text('Sign'),
          ),
        ],
      ),
    );
  }
}

class _StatusBanner extends StatelessWidget {
  final Visit visit;

  const _StatusBanner({required this.visit});

  Color get _color {
    switch (visit.status) {
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
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: _color.withAlpha(13),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _color.withAlpha(77)),
      ),
      child: Row(
        children: [
          Icon(Icons.circle, color: _color, size: 12),
          const SizedBox(width: 8),
          Text(
            'Status: ${visit.status}',
            style: TextStyle(
              color: _color,
              fontWeight: FontWeight.w600,
              fontSize: 14,
            ),
          ),
          if (visit.isApproved) ...[
            const SizedBox(width: 16),
            const Icon(Icons.verified, color: AppConstants.successColor, size: 16),
            const SizedBox(width: 4),
            Text(
              'Approved ${DateFormat('dd MMM').format(visit.doctorApprovedAt!)}',
              style: const TextStyle(
                  color: AppConstants.successColor, fontSize: 12),
            ),
          ],
        ],
      ),
    );
  }
}

class _InfoSection extends StatelessWidget {
  final Visit visit;

  const _InfoSection({required this.visit});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Visit Information', style: AppConstants.subheadingStyle),
            const Divider(height: 16),
            _InfoRow(
              icon: Icons.calendar_today,
              label: 'Visit Date',
              value: DateFormat('dd MMM yyyy, hh:mm a').format(visit.visitDate),
            ),
            if (visit.chiefComplaint != null) ...[
              const SizedBox(height: 10),
              _InfoRow(
                icon: Icons.chat_bubble_outline,
                label: 'Chief Complaint',
                value: visit.chiefComplaint!,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 16, color: AppConstants.textSecondary),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label,
                  style: const TextStyle(
                      fontSize: 11, color: AppConstants.textSecondary)),
              const SizedBox(height: 2),
              Text(value,
                  style: const TextStyle(
                      fontSize: 14, color: AppConstants.textPrimary)),
            ],
          ),
        ),
      ],
    );
  }
}

class _AiSummaryBox extends StatelessWidget {
  final String summary;

  const _AiSummaryBox({required this.summary});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppConstants.visitBlue.withAlpha(13),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppConstants.visitBlue.withAlpha(51)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.auto_awesome, color: AppConstants.visitBlue, size: 16),
              SizedBox(width: 6),
              Text(
                'AI Summary',
                style: TextStyle(
                  color: AppConstants.visitBlue,
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            summary,
            style: const TextStyle(
              color: AppConstants.textPrimary,
              fontSize: 14,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String title;

  const _SectionTitle({required this.title});

  @override
  Widget build(BuildContext context) {
    return Text(title, style: AppConstants.subheadingStyle);
  }
}
