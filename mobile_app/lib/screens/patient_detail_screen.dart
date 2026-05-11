import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/patient_provider.dart';
import '../providers/visit_provider.dart';
import '../providers/prescription_provider.dart';
import '../models/patient_model.dart';
import '../widgets/visit_card.dart';
import '../widgets/prescription_card.dart';
import '../widgets/loading_widget.dart';
import '../widgets/empty_state.dart';
import '../core/constants.dart';

class PatientDetailScreen extends StatefulWidget {
  final int patientId;

  const PatientDetailScreen({super.key, required this.patientId});

  @override
  State<PatientDetailScreen> createState() => _PatientDetailScreenState();
}

class _PatientDetailScreenState extends State<PatientDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  Patient? _patient;
  bool _loadingPatient = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _loadingPatient = true);
    final patient = await context
        .read<PatientProvider>()
        .fetchPatientById(widget.patientId);
    setState(() {
      _patient = patient;
      _loadingPatient = false;
    });
    await Future.wait([
      context
          .read<VisitProvider>()
          .fetchVisits(patientId: widget.patientId),
      context
          .read<PrescriptionProvider>()
          .fetchPrescriptions(patientId: widget.patientId),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    if (_loadingPatient) {
      return Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new, size: 20),
            onPressed: () => context.pop(),
          ),
          title: const Text('Patient Detail'),
        ),
        body: const LoadingWidget(),
      );
    }

    if (_patient == null) {
      return Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new, size: 20),
            onPressed: () => context.pop(),
          ),
          title: const Text('Patient Detail'),
        ),
        body: const Center(child: Text('Patient not found')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
        title: Text(_patient!.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.timeline_outlined),
            tooltip: 'EMR Timeline',
            onPressed: () => context.go('/emr/${widget.patientId}'),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          labelStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
          tabs: const [
            Tab(text: 'Visits'),
            Tab(text: 'Prescriptions'),
            Tab(text: 'Lab Reports'),
            Tab(text: 'Vitals'),
          ],
        ),
      ),
      body: Column(
        children: [
          _PatientInfoHeader(patient: _patient!),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _VisitsTab(patientId: widget.patientId),
                _PrescriptionsTab(patientId: widget.patientId),
                _LabReportsTab(),
                _VitalsTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PatientInfoHeader extends StatelessWidget {
  final Patient patient;

  const _PatientInfoHeader({required this.patient});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.white,
      child: Row(
        children: [
          CircleAvatar(
            radius: 28,
            backgroundColor: AppConstants.primaryColor.withAlpha(26),
            child: Text(
              patient.name.isNotEmpty ? patient.name[0].toUpperCase() : '?',
              style: const TextStyle(
                color: AppConstants.primaryColor,
                fontWeight: FontWeight.bold,
                fontSize: 22,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(patient.name, style: AppConstants.subheadingStyle),
                const SizedBox(height: 2),
                Text('UID: ${patient.patientUid}',
                    style: const TextStyle(
                        color: AppConstants.primaryColor, fontSize: 12)),
                const SizedBox(height: 4),
                Wrap(
                  spacing: 8,
                  children: [
                    if (patient.gender != null)
                      _Chip(label: patient.gender!, color: AppConstants.secondaryColor),
                    if (patient.bloodGroup != null)
                      _Chip(label: patient.bloodGroup!, color: Colors.red.shade600),
                    if (patient.age != null)
                      _Chip(
                          label: '${patient.age} yrs',
                          color: AppConstants.textSecondary),
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

class _Chip extends StatelessWidget {
  final String label;
  final Color color;

  const _Chip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withAlpha(26),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600),
      ),
    );
  }
}

class _VisitsTab extends StatelessWidget {
  final int patientId;

  const _VisitsTab({required this.patientId});

  @override
  Widget build(BuildContext context) {
    final visitProvider = context.watch<VisitProvider>();
    if (visitProvider.isLoading) return const LoadingWidget();
    if (visitProvider.visits.isEmpty) {
      return const EmptyState(
        icon: Icons.medical_services_outlined,
        message: 'No visits recorded',
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: visitProvider.visits.length,
      itemBuilder: (context, index) {
        final visit = visitProvider.visits[index];
        return VisitCard(
          visit: visit,
          onTap: () => context.go('/visits/${visit.id}'),
        );
      },
    );
  }
}

class _PrescriptionsTab extends StatelessWidget {
  final int patientId;

  const _PrescriptionsTab({required this.patientId});

  @override
  Widget build(BuildContext context) {
    final rxProvider = context.watch<PrescriptionProvider>();
    if (rxProvider.isLoading) return const LoadingWidget();
    if (rxProvider.prescriptions.isEmpty) {
      return const EmptyState(
        icon: Icons.description_outlined,
        message: 'No prescriptions found',
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: rxProvider.prescriptions.length,
      itemBuilder: (context, index) {
        return PrescriptionCard(prescription: rxProvider.prescriptions[index]);
      },
    );
  }
}

class _LabReportsTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const EmptyState(
      icon: Icons.biotech_outlined,
      message: 'No lab reports available',
    );
  }
}

class _VitalsTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const EmptyState(
      icon: Icons.monitor_heart_outlined,
      message: 'No vitals recorded',
    );
  }
}
