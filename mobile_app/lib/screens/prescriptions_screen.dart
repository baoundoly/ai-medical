import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/prescription_provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/prescription_card.dart';
import '../widgets/empty_state.dart';
import '../widgets/loading_widget.dart';
import '../core/constants.dart';

class PrescriptionsScreen extends StatefulWidget {
  const PrescriptionsScreen({super.key});

  @override
  State<PrescriptionsScreen> createState() => _PrescriptionsScreenState();
}

class _PrescriptionsScreenState extends State<PrescriptionsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PrescriptionProvider>().fetchPrescriptions();
    });
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
            const Text('Enter your password to digitally sign this prescription:'),
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
              if (passCtrl.text.isEmpty) return;
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
                    content: Text('Prescription signed successfully'),
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

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<PrescriptionProvider>();
    final auth = context.watch<AuthProvider>();
    final isDoctor = auth.user?.isDoctor ?? false;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Prescriptions'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.go('/dashboard'),
        ),
      ),
      body: provider.isLoading
          ? const LoadingWidget(message: 'Loading prescriptions...')
          : provider.prescriptions.isEmpty
              ? const EmptyState(
                  icon: Icons.description_outlined,
                  message: 'No prescriptions found',
                  subMessage: 'Prescriptions will appear here once created',
                )
              : RefreshIndicator(
                  onRefresh: () => provider.fetchPrescriptions(),
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    itemCount: provider.prescriptions.length,
                    itemBuilder: (context, index) {
                      final rx = provider.prescriptions[index];
                      return PrescriptionCard(
                        prescription: rx,
                        showSignButton: isDoctor && !rx.isSigned,
                        onSign: () => _showSignDialog(rx.id),
                      );
                    },
                  ),
                ),
    );
  }
}
