import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../providers/appointment_provider.dart';
import '../widgets/appointment_card.dart';
import '../widgets/empty_state.dart';
import '../widgets/loading_widget.dart';
import '../core/constants.dart';

class AppointmentsScreen extends StatefulWidget {
  const AppointmentsScreen({super.key});

  @override
  State<AppointmentsScreen> createState() => _AppointmentsScreenState();
}

class _AppointmentsScreenState extends State<AppointmentsScreen> {
  DateTime _selectedDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AppointmentProvider>().fetchAppointments(date: _selectedDate);
    });
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime(2030),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
      context.read<AppointmentProvider>().fetchAppointments(date: picked);
    }
  }

  void _showBookAppointmentDialog() {
    final patientIdCtrl = TextEditingController();
    final doctorIdCtrl = TextEditingController();
    final formKey = GlobalKey<FormState>();
    bool isEmergency = false;
    String appointmentType = 'General';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) => Padding(
          padding: EdgeInsets.fromLTRB(
              20, 20, 20, MediaQuery.of(ctx).viewInsets.bottom + 20),
          child: Form(
            key: formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text('Book Appointment', style: AppConstants.subheadingStyle),
                const SizedBox(height: 16),
                TextFormField(
                  controller: patientIdCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Patient ID *'),
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Patient ID required' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: doctorIdCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Doctor ID *'),
                  validator: (v) =>
                      v == null || v.isEmpty ? 'Doctor ID required' : null,
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: appointmentType,
                  decoration: const InputDecoration(labelText: 'Type'),
                  items: const [
                    DropdownMenuItem(value: 'General', child: Text('General')),
                    DropdownMenuItem(
                        value: 'Follow-up', child: Text('Follow-up')),
                    DropdownMenuItem(
                        value: 'Consultation', child: Text('Consultation')),
                    DropdownMenuItem(
                        value: 'Emergency', child: Text('Emergency')),
                  ],
                  onChanged: (v) => setModalState(() => appointmentType = v!),
                ),
                const SizedBox(height: 8),
                CheckboxListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Mark as Emergency'),
                  value: isEmergency,
                  activeColor: AppConstants.errorColor,
                  onChanged: (v) => setModalState(() => isEmergency = v!),
                ),
                const SizedBox(height: 12),
                ElevatedButton(
                  onPressed: () async {
                    if (!formKey.currentState!.validate()) return;
                    final error = await context
                        .read<AppointmentProvider>()
                        .createAppointment({
                      'patientId': int.tryParse(patientIdCtrl.text) ?? 0,
                      'doctorId': int.tryParse(doctorIdCtrl.text) ?? 0,
                      'scheduledAt': _selectedDate.toIso8601String(),
                      'appointmentType': appointmentType,
                      'isEmergency': isEmergency,
                    });
                    if (ctx.mounted) Navigator.pop(ctx);
                    if (error != null && context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                            content: Text(error),
                            backgroundColor: AppConstants.errorColor),
                      );
                    } else if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Appointment booked'),
                          backgroundColor: AppConstants.successColor,
                        ),
                      );
                    }
                  },
                  child: const Text('Book Appointment'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<AppointmentProvider>();
    final todayAppts = provider.todayAppointments;
    final emergencies = provider.emergencyAppointments;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Appointments'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.go('/dashboard'),
        ),
      ),
      body: Column(
        children: [
          // Date selector
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                const Icon(Icons.calendar_today,
                    color: AppConstants.primaryColor, size: 18),
                const SizedBox(width: 8),
                Text(
                  DateFormat('EEEE, dd MMMM yyyy').format(_selectedDate),
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                    color: AppConstants.textPrimary,
                  ),
                ),
                const Spacer(),
                TextButton(
                  onPressed: _pickDate,
                  child: const Text('Change'),
                ),
              ],
            ),
          ),

          // Emergency banner
          if (emergencies.isNotEmpty)
            Container(
              margin: const EdgeInsets.all(12),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: AppConstants.errorColor.withAlpha(26),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppConstants.errorColor.withAlpha(77)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.emergency,
                      color: AppConstants.errorColor, size: 18),
                  const SizedBox(width: 8),
                  Text(
                    '${emergencies.length} Emergency Case(s)',
                    style: const TextStyle(
                      color: AppConstants.errorColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),

          // Token queue grid
          if (todayAppts.isNotEmpty) ...[
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
              child: Row(
                children: [
                  const Text('Token Queue', style: AppConstants.subheadingStyle),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppConstants.primaryColor.withAlpha(26),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${todayAppts.length}',
                      style: const TextStyle(
                        color: AppConstants.primaryColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(
              height: 80,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                itemCount: todayAppts.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (context, index) {
                  final a = todayAppts[index];
                  return Container(
                    width: 56,
                    decoration: BoxDecoration(
                      color: a.isEmergency
                          ? AppConstants.errorColor
                          : AppConstants.primaryColor,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    alignment: Alignment.center,
                    child: a.isEmergency
                        ? const Icon(Icons.emergency,
                            color: Colors.white, size: 20)
                        : Text(
                            '#${a.tokenNumber ?? '--'}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                  );
                },
              ),
            ),
          ],

          // Appointment list
          Expanded(
            child: provider.isLoading
                ? const LoadingWidget(message: 'Loading appointments...')
                : provider.appointments.isEmpty
                    ? EmptyState(
                        icon: Icons.calendar_month_outlined,
                        message: 'No appointments',
                        subMessage: 'Book a new appointment to get started',
                        onAction: _showBookAppointmentDialog,
                        actionLabel: 'Book Appointment',
                      )
                    : RefreshIndicator(
                        onRefresh: () => provider.fetchAppointments(
                            date: _selectedDate),
                        child: ListView.builder(
                          padding: const EdgeInsets.only(bottom: 80, top: 4),
                          itemCount: provider.appointments.length,
                          itemBuilder: (context, index) {
                            final a = provider.appointments[index];
                            return AppointmentCard(
                              appointment: a,
                              onTap: () {},
                              onCancel: a.isScheduled
                                  ? () async {
                                      final error = await provider
                                          .cancelAppointment(a.id);
                                      if (!context.mounted) return;
                                      if (error != null) {
                                        ScaffoldMessenger.of(context)
                                            .showSnackBar(
                                          SnackBar(
                                              content: Text(error),
                                              backgroundColor:
                                                  AppConstants.errorColor),
                                        );
                                      }
                                    }
                                  : null,
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showBookAppointmentDialog,
        backgroundColor: AppConstants.primaryColor,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}
