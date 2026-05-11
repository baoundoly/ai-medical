import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/patient_model.dart';

class PatientProvider extends ChangeNotifier {
  List<Patient> patients = [];
  Patient? selectedPatient;
  bool isLoading = false;
  String? errorMessage;
  int currentPage = 1;
  bool hasMore = true;

  Future<void> fetchPatients({String? search, int page = 1}) async {
    if (page == 1) {
      isLoading = true;
      patients = [];
      notifyListeners();
    }
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'pageSize': 20,
      };
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      final response = await ApiClient.instance.dio.get(
        AppConstants.patientsEndpoint,
        queryParameters: queryParams,
      );
      final data = response.data;
      List<dynamic> list;
      if (data is List) {
        list = data;
        hasMore = list.length == 20;
      } else if (data is Map && data['items'] != null) {
        list = data['items'] as List<dynamic>;
        hasMore = (data['hasMore'] as bool?) ?? list.length == 20;
      } else {
        list = [];
        hasMore = false;
      }
      final newPatients =
          list.map((e) => Patient.fromJson(e as Map<String, dynamic>)).toList();
      if (page == 1) {
        patients = newPatients;
      } else {
        patients = [...patients, ...newPatients];
      }
      currentPage = page;
      errorMessage = null;
    } on DioException catch (e) {
      errorMessage = e.response?.data?['message'] as String? ?? 'Failed to load patients.';
    } catch (_) {
      errorMessage = 'Failed to load patients.';
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<Patient?> fetchPatientById(int id) async {
    try {
      final response = await ApiClient.instance.dio.get(
        '${AppConstants.patientsEndpoint}/$id',
      );
      selectedPatient =
          Patient.fromJson(response.data as Map<String, dynamic>);
      notifyListeners();
      return selectedPatient;
    } catch (_) {
      return null;
    }
  }

  Future<String?> createPatient(Map<String, dynamic> data) async {
    try {
      final response = await ApiClient.instance.dio.post(
        AppConstants.patientsEndpoint,
        data: data,
      );
      final patient =
          Patient.fromJson(response.data as Map<String, dynamic>);
      patients.insert(0, patient);
      notifyListeners();
      return null;
    } on DioException catch (e) {
      return e.response?.data?['message'] as String? ?? 'Failed to create patient.';
    } catch (_) {
      return 'Failed to create patient.';
    }
  }

  Future<Map<String, dynamic>?> checkDuplicates({
    required String name,
    String? mobile,
    String? dob,
  }) async {
    try {
      final response = await ApiClient.instance.dio.post(
        AppConstants.patientDuplicateEndpoint,
        data: {
          'name': name,
          'mobile': mobile,
          'dateOfBirth': dob,
        },
      );
      return response.data as Map<String, dynamic>?;
    } catch (_) {
      return null;
    }
  }
}
