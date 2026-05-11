import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';

import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/user_model.dart';

class AuthProvider extends ChangeNotifier {
  User? _user;
  String? _token;
  bool _isLoading = false;
  bool _initialized = false;

  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  User? get user => _user;
  String? get token => _token;
  bool get isLoading => _isLoading;
  bool get initialized => _initialized;
  bool get isAuthenticated => _token != null && _user != null;

  Future<void> loadFromStorage() async {
    _isLoading = true;
    notifyListeners();
    try {
      final token = await _storage.read(key: AppConstants.tokenKey);
      if (token != null) {
        _token = token;
        await _fetchCurrentUser();
      }
    } catch (_) {
      _token = null;
      _user = null;
    } finally {
      _isLoading = false;
      _initialized = true;
      notifyListeners();
    }
  }

  Future<String?> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await ApiClient.instance.dio.post(
        AppConstants.loginEndpoint,
        data: {'email': email, 'password': password},
      );
      final data = response.data as Map<String, dynamic>;
      final token = data['token'] as String;
      _token = token;
      await ApiClient.instance.setToken(token);

      if (data['user'] != null) {
        _user = User.fromJson(data['user'] as Map<String, dynamic>);
      } else {
        await _fetchCurrentUser();
      }
      return null; // success
    } on DioException catch (e) {
      final msg = e.response?.data?['message'] as String? ??
          e.response?.data?['error'] as String? ??
          'Login failed. Please check your credentials.';
      return msg;
    } catch (e) {
      return 'An unexpected error occurred.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _user = null;
    _token = null;
    await ApiClient.instance.clearToken();
    notifyListeners();
  }

  Future<void> _fetchCurrentUser() async {
    try {
      final response =
          await ApiClient.instance.dio.get(AppConstants.meEndpoint);
      _user = User.fromJson(response.data as Map<String, dynamic>);
    } catch (_) {
      _token = null;
      _user = null;
    }
  }
}
