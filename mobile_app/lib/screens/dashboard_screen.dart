import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/appointment_provider.dart';
import '../providers/patient_provider.dart';
import '../providers/visit_provider.dart';
import '../widgets/stat_card.dart';
import '../widgets/appointment_card.dart';
import '../widgets/loading_widget.dart';
import '../core/constants.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadData());
  }

  Future<void> _loadData() async {
    await Future.wait([
      context.read<PatientProvider>().fetchPatients(),
      context.read<AppointmentProvider>().fetchAppointments(
            date: DateTime.now(),
          ),
      context.read<VisitProvider>().fetchVisits(status: 'Pending'),
    ]);
  }

  void _onNavTap(int index) {
    setState(() => _selectedIndex = index);
    switch (index) {
      case 0:
        context.go('/dashboard');
        break;
      case 1:
        context.go('/patients');
        break;
      case 2:
        context.go('/visits');
        break;
      case 3:
        context.go('/appointments');
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final appointments = context.watch<AppointmentProvider>();
    final patients = context.watch<PatientProvider>();
    final visits = context.watch<VisitProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () async {
              await auth.logout();
              if (context.mounted) context.go('/login');
            },
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
              // Welcome
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppConstants.primaryColor, AppConstants.secondaryColor],
                  ),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Row(
                  children: [
                    const CircleAvatar(
                      backgroundColor: Colors.white24,
                      child: Icon(Icons.person, color: Colors.white),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Welcome, ${auth.user?.fullName ?? 'User'}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          Text(
                            auth.user?.role ?? '',
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.notifications_outlined, color: Colors.white),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              const Text('Overview', style: AppConstants.subheadingStyle),
              const SizedBox(height: 12),

              // Stats grid
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 1.3,
                children: [
                  StatCard(
                    icon: Icons.people_outline,
                    value: patients.isLoading
                        ? '...'
                        : patients.patients.length.toString(),
                    label: 'Total Patients',
                    color: AppConstants.primaryColor,
                    onTap: () => context.go('/patients'),
                  ),
                  StatCard(
                    icon: Icons.calendar_today_outlined,
                    value: appointments.isLoading
                        ? '...'
                        : appointments.todayAppointments.length.toString(),
                    label: "Today's Appointments",
                    color: AppConstants.secondaryColor,
                    onTap: () => context.go('/appointments'),
                  ),
                  StatCard(
                    icon: Icons.pending_actions_outlined,
                    value: visits.isLoading
                        ? '...'
                        : visits.pendingVisits.length.toString(),
                    label: 'Pending Visits',
                    color: AppConstants.warningColor,
                    onTap: () => context.go('/visits'),
                  ),
                  StatCard(
                    icon: Icons.emergency_outlined,
                    value: appointments.isLoading
                        ? '...'
                        : appointments.emergencyAppointments.length.toString(),
                    label: 'Critical Alerts',
                    color: AppConstants.errorColor,
                    onTap: () => context.go('/appointments'),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text("Today's Queue", style: AppConstants.subheadingStyle),
                  TextButton(
                    onPressed: () => context.go('/appointments'),
                    child: const Text('See all'),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              if (appointments.isLoading)
                const LoadingWidget()
              else if (appointments.todayAppointments.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 20),
                  child: Center(
                    child: Text('No appointments today',
                        style: AppConstants.bodyStyle),
                  ),
                )
              else
                ...appointments.todayAppointments.take(5).map(
                      (a) => AppointmentCard(
                        appointment: a,
                        onTap: () {},
                      ),
                    ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: _onNavTap,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          NavigationDestination(
            icon: Icon(Icons.people_outline),
            selectedIcon: Icon(Icons.people),
            label: 'Patients',
          ),
          NavigationDestination(
            icon: Icon(Icons.medical_services_outlined),
            selectedIcon: Icon(Icons.medical_services),
            label: 'Visits',
          ),
          NavigationDestination(
            icon: Icon(Icons.calendar_month_outlined),
            selectedIcon: Icon(Icons.calendar_month),
            label: 'Appointments',
          ),
        ],
      ),
    );
  }
}
