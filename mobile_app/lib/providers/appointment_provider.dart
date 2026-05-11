import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/appointment_model.dart';

class AppointmentProvider extends ChangeNotifier {
  List<Appointment> appointments = [];
  bool isLoading = false;
  String? errorMessage;

  Future<void> fetchAppointments({DateTime? date, String? status}) async {
    isLoading = true;
    notifyListeners();
    try {
      final queryParams = <String, dynamic>{};
      if (date != null) {
        queryParams['date'] =
            '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
      }
      if (status != null) queryParams['status'] = status;

      final response = await ApiClient.instance.dio.get(
        AppConstants.appointmentsEndpoint,
        queryParameters: queryParams,
      );
      final data = response.data;
      List<dynamic> list;
      if (data is List) {
        list = data;
      } else if (data is Map && data['items'] != null) {
        list = data['items'] as List<dynamic>;
      } else {
        list = [];
      }
      appointments = list
          .map((e) => Appointment.fromJson(e as Map<String, dynamic>))
          .toList();
      errorMessage = null;
    } on DioException catch (e) {
      errorMessage = e.response?.data?['message'] as String? ??
          'Failed to load appointments.';
    } catch (_) {
      errorMessage = 'Failed to load appointments.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<String?> createAppointment(Map<String, dynamic> data) async {
    try {
      final response = await ApiClient.instance.dio.post(
        AppConstants.appointmentsEndpoint,
        data: data,
      );
      final appointment =
          Appointment.fromJson(response.data as Map<String, dynamic>);
      appointments.insert(0, appointment);
      notifyListeners();
      return null;
    } on DioException catch (e) {
      return e.response?.data?['message'] as String? ??
          'Failed to book appointment.';
    } catch (_) {
      return 'Failed to book appointment.';
    }
  }

  Future<String?> cancelAppointment(int id) async {
    try {
      await ApiClient.instance.dio.post(
        '${AppConstants.appointmentsEndpoint}/$id/cancel',
      );
      final idx = appointments.indexWhere((a) => a.id == id);
      if (idx >= 0) {
        final a = appointments[idx];
        appointments[idx] = Appointment(
          id: a.id,
          patientId: a.patientId,
          doctorId: a.doctorId,
          scheduledAt: a.scheduledAt,
          appointmentType: a.appointmentType,
          status: 'Cancelled',
          tokenNumber: a.tokenNumber,
          isEmergency: a.isEmergency,
        );
        notifyListeners();
      }
      return null;
    } on DioException catch (e) {
      return e.response?.data?['message'] as String? ??
          'Failed to cancel appointment.';
    } catch (_) {
      return 'Failed to cancel appointment.';
    }
  }

  List<Appointment> get todayAppointments {
    final now = DateTime.now();
    return appointments.where((a) {
      return a.scheduledAt.year == now.year &&
          a.scheduledAt.month == now.month &&
          a.scheduledAt.day == now.day;
    }).toList();
  }

  List<Appointment> get emergencyAppointments =>
      appointments.where((a) => a.isEmergency).toList();
}
