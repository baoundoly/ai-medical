import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/prescription_model.dart';

class PrescriptionProvider extends ChangeNotifier {
  List<Prescription> prescriptions = [];
  bool isLoading = false;
  String? errorMessage;

  Future<void> fetchPrescriptions({int? visitId, int? patientId}) async {
    isLoading = true;
    notifyListeners();
    try {
      final queryParams = <String, dynamic>{};
      if (visitId != null) queryParams['visitId'] = visitId;
      if (patientId != null) queryParams['patientId'] = patientId;

      final response = await ApiClient.instance.dio.get(
        AppConstants.prescriptionsEndpoint,
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
      prescriptions = list
          .map((e) => Prescription.fromJson(e as Map<String, dynamic>))
          .toList();
      errorMessage = null;
    } on DioException catch (e) {
      errorMessage = e.response?.data?['message'] as String? ??
          'Failed to load prescriptions.';
    } catch (_) {
      errorMessage = 'Failed to load prescriptions.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<String?> createPrescription(Map<String, dynamic> data) async {
    try {
      final response = await ApiClient.instance.dio.post(
        AppConstants.prescriptionsEndpoint,
        data: data,
      );
      final prescription =
          Prescription.fromJson(response.data as Map<String, dynamic>);
      prescriptions.insert(0, prescription);
      notifyListeners();
      return null;
    } on DioException catch (e) {
      return e.response?.data?['message'] as String? ??
          'Failed to create prescription.';
    } catch (_) {
      return 'Failed to create prescription.';
    }
  }

  Future<String?> signPrescription(int id, String password) async {
    try {
      await ApiClient.instance.dio.post(
        '${AppConstants.prescriptionsEndpoint}/$id/sign',
        data: {'password': password},
      );
      final idx = prescriptions.indexWhere((p) => p.id == id);
      if (idx >= 0) {
        final p = prescriptions[idx];
        prescriptions[idx] = Prescription(
          id: p.id,
          visitId: p.visitId,
          status: 'Signed',
          signedAt: DateTime.now(),
          items: p.items,
        );
        notifyListeners();
      }
      return null;
    } on DioException catch (e) {
      return e.response?.data?['message'] as String? ??
          'Failed to sign prescription.';
    } catch (_) {
      return 'Failed to sign prescription.';
    }
  }
}
