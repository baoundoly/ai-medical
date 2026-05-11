import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../screens/login_screen.dart';
import '../screens/dashboard_screen.dart';
import '../screens/patients_screen.dart';
import '../screens/patient_detail_screen.dart';
import '../screens/visits_screen.dart';
import '../screens/visit_detail_screen.dart';
import '../screens/appointments_screen.dart';
import '../screens/prescriptions_screen.dart';
import '../screens/emr_screen.dart';

GoRouter buildRouter(AuthProvider authProvider) {
  return GoRouter(
    initialLocation: '/dashboard',
    refreshListenable: authProvider,
    redirect: (BuildContext context, GoRouterState state) {
      final isAuthenticated = authProvider.isAuthenticated;
      final isLoggingIn = state.matchedLocation == '/login';

      if (!isAuthenticated && !isLoggingIn) {
        return '/login';
      }
      if (isAuthenticated && isLoggingIn) {
        return '/dashboard';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/dashboard',
        name: 'dashboard',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/patients',
        name: 'patients',
        builder: (context, state) => const PatientsScreen(),
      ),
      GoRoute(
        path: '/patients/:id',
        name: 'patientDetail',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return PatientDetailScreen(patientId: id);
        },
      ),
      GoRoute(
        path: '/visits',
        name: 'visits',
        builder: (context, state) => const VisitsScreen(),
      ),
      GoRoute(
        path: '/visits/:id',
        name: 'visitDetail',
        builder: (context, state) {
          final id = int.parse(state.pathParameters['id']!);
          return VisitDetailScreen(visitId: id);
        },
      ),
      GoRoute(
        path: '/appointments',
        name: 'appointments',
        builder: (context, state) => const AppointmentsScreen(),
      ),
      GoRoute(
        path: '/prescriptions',
        name: 'prescriptions',
        builder: (context, state) => const PrescriptionsScreen(),
      ),
      GoRoute(
        path: '/emr/:patientId',
        name: 'emr',
        builder: (context, state) {
          final patientId = int.parse(state.pathParameters['patientId']!);
          return EmrScreen(patientId: patientId);
        },
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.error}'),
      ),
    ),
  );
}
