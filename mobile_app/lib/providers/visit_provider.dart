import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/visit_model.dart';

class VisitProvider extends ChangeNotifier {
  List<Visit> visits = [];
  Visit? selectedVisit;
  bool isLoading = false;
  String? errorMessage;

  Future<void> fetchVisits({String? status, int? patientId}) async {
    isLoading = true;
    notifyListeners();
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) queryParams['status'] = status;
      if (patientId != null) queryParams['patientId'] = patientId;

      final response = await ApiClient.instance.dio.get(
        AppConstants.visitsEndpoint,
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
      visits = list.map((e) => Visit.fromJson(e as Map<String, dynamic>)).toList();
      errorMessage = null;
    } on DioException catch (e) {
      errorMessage = e.response?.data?['message'] as String? ?? 'Failed to load visits.';
    } catch (_) {
      errorMessage = 'Failed to load visits.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<Visit?> fetchVisitById(int id) async {
    try {
      final response = await ApiClient.instance.dio.get(
        '${AppConstants.visitsEndpoint}/$id',
      );
      selectedVisit = Visit.fromJson(response.data as Map<String, dynamic>);
      notifyListeners();
      return selectedVisit;
    } catch (_) {
      return null;
    }
  }

  Future<String?> createVisit(Map<String, dynamic> data) async {
    try {
      final response = await ApiClient.instance.dio.post(
        AppConstants.visitsEndpoint,
        data: data,
      );
      final visit = Visit.fromJson(response.data as Map<String, dynamic>);
      visits.insert(0, visit);
      notifyListeners();
      return null;
    } on DioException catch (e) {
      return e.response?.data?['message'] as String? ?? 'Failed to create visit.';
    } catch (_) {
      return 'Failed to create visit.';
    }
  }

  Future<String?> approveVisit(int visitId) async {
    try {
      await ApiClient.instance.dio.post(
        '${AppConstants.visitsEndpoint}/$visitId/approve',
      );
      final idx = visits.indexWhere((v) => v.id == visitId);
      if (idx >= 0) {
        final v = visits[idx];
        visits[idx] = Visit(
          id: v.id,
          patientId: v.patientId,
          doctorId: v.doctorId,
          visitDate: v.visitDate,
          status: 'Completed',
          chiefComplaint: v.chiefComplaint,
          aiSummary: v.aiSummary,
          doctorApprovedAt: DateTime.now(),
        );
        notifyListeners();
      }
      if (selectedVisit?.id == visitId) {
        await fetchVisitById(visitId);
      }
      return null;
    } on DioException catch (e) {
      return e.response?.data?['message'] as String? ?? 'Failed to approve visit.';
    } catch (_) {
      return 'Failed to approve visit.';
    }
  }

  List<Visit> get pendingVisits =>
      visits.where((v) => v.isPending).toList();
  List<Visit> get activeVisits =>
      visits.where((v) => v.isActive).toList();
  List<Visit> get completedVisits =>
      visits.where((v) => v.isCompleted).toList();
}
