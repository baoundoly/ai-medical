import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import 'package:intl/intl.dart';

import '../core/api_client.dart';
import '../core/constants.dart';
import '../widgets/loading_widget.dart';
import '../widgets/empty_state.dart';

enum _EventType { visit, prescription, labReport, vital }

class _EmrEvent {
  final _EventType type;
  final DateTime date;
  final String title;
  final String? subtitle;
  final Map<String, dynamic> data;

  const _EmrEvent({
    required this.type,
    required this.date,
    required this.title,
    this.subtitle,
    required this.data,
  });
}

class EmrScreen extends StatefulWidget {
  final int patientId;

  const EmrScreen({super.key, required this.patientId});

  @override
  State<EmrScreen> createState() => _EmrScreenState();
}

class _EmrScreenState extends State<EmrScreen> {
  bool _loading = true;
  List<_EmrEvent> _events = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadEmr();
  }

  Future<void> _loadEmr() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final response = await ApiClient.instance.dio.get(
        '${AppConstants.emrEndpoint}/${widget.patientId}',
      );
      final data = response.data as Map<String, dynamic>;
      final events = <_EmrEvent>[];

      // Parse visits
      final visits = data['visits'] as List<dynamic>? ?? [];
      for (final v in visits) {
        final vMap = v as Map<String, dynamic>;
        events.add(_EmrEvent(
          type: _EventType.visit,
          date: DateTime.parse(
              (vMap['visitDate'] ?? vMap['visit_date']) as String),
          title: (vMap['chiefComplaint'] ?? vMap['chief_complaint'] ?? 'Visit')
              as String,
          subtitle: vMap['status'] as String?,
          data: vMap,
        ));
      }

      // Parse prescriptions
      final prescriptions = data['prescriptions'] as List<dynamic>? ?? [];
      for (final p in prescriptions) {
        final pMap = p as Map<String, dynamic>;
        final items = pMap['items'] as List<dynamic>? ?? [];
        events.add(_EmrEvent(
          type: _EventType.prescription,
          date: DateTime.parse(
              (pMap['createdAt'] ?? pMap['created_at'] ?? pMap['signedAt'] ??
                  DateTime.now().toIso8601String()) as String),
          title: 'Prescription #${pMap['id']}',
          subtitle: '${items.length} medicine(s)',
          data: pMap,
        ));
      }

      // Parse lab reports
      final labs = data['labReports'] as List<dynamic>? ?? [];
      for (final l in labs) {
        final lMap = l as Map<String, dynamic>;
        events.add(_EmrEvent(
          type: _EventType.labReport,
          date: DateTime.parse(
              (lMap['reportDate'] ?? lMap['report_date'] ??
                  DateTime.now().toIso8601String()) as String),
          title: (lMap['testName'] ?? lMap['test_name'] ?? 'Lab Report') as String,
          subtitle: lMap['status'] as String?,
          data: lMap,
        ));
      }

      // Parse vitals
      final vitals = data['vitals'] as List<dynamic>? ?? [];
      for (final v in vitals) {
        final vMap = v as Map<String, dynamic>;
        events.add(_EmrEvent(
          type: _EventType.vital,
          date: DateTime.parse(
              (vMap['recordedAt'] ?? vMap['recorded_at'] ??
                  DateTime.now().toIso8601String()) as String),
          title: 'Vitals Recorded',
          subtitle:
              'BP: ${vMap['bloodPressure'] ?? vMap['blood_pressure'] ?? '--'}',
          data: vMap,
        ));
      }

      events.sort((a, b) => b.date.compareTo(a.date));
      setState(() {
        _events = events;
        _loading = false;
      });
    } on DioException catch (e) {
      setState(() {
        _error = e.response?.data?['message'] as String? ??
            'Failed to load EMR data.';
        _loading = false;
      });
    } catch (_) {
      setState(() {
        _error = 'Failed to load EMR data.';
        _loading = false;
      });
    }
  }

  Color _eventColor(_EventType type) {
    switch (type) {
      case _EventType.visit:
        return AppConstants.visitBlue;
      case _EventType.prescription:
        return AppConstants.prescriptionGreen;
      case _EventType.labReport:
        return AppConstants.labOrange;
      case _EventType.vital:
        return AppConstants.vitalPurple;
    }
  }

  IconData _eventIcon(_EventType type) {
    switch (type) {
      case _EventType.visit:
        return Icons.medical_services_outlined;
      case _EventType.prescription:
        return Icons.description_outlined;
      case _EventType.labReport:
        return Icons.biotech_outlined;
      case _EventType.vital:
        return Icons.monitor_heart_outlined;
    }
  }

  String _eventLabel(_EventType type) {
    switch (type) {
      case _EventType.visit:
        return 'Visit';
      case _EventType.prescription:
        return 'Prescription';
      case _EventType.labReport:
        return 'Lab Report';
      case _EventType.vital:
        return 'Vitals';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
        title: const Text('EMR Timeline'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadEmr,
          ),
        ],
      ),
      body: _loading
          ? const LoadingWidget(message: 'Loading medical records...')
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.error_outline,
                          color: AppConstants.errorColor, size: 48),
                      const SizedBox(height: 12),
                      Text(_error!, style: AppConstants.bodyStyle),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadEmr,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _events.isEmpty
                  ? const EmptyState(
                      icon: Icons.timeline,
                      message: 'No medical records found',
                      subMessage: 'Patient\'s medical history will appear here',
                    )
                  : Column(
                      children: [
                        _LegendRow(),
                        Expanded(
                          child: RefreshIndicator(
                            onRefresh: _loadEmr,
                            child: ListView.builder(
                              padding: const EdgeInsets.all(16),
                              itemCount: _events.length,
                              itemBuilder: (context, index) {
                                final event = _events[index];
                                final isLast = index == _events.length - 1;
                                return _TimelineItem(
                                  event: event,
                                  color: _eventColor(event.type),
                                  icon: _eventIcon(event.type),
                                  label: _eventLabel(event.type),
                                  isLast: isLast,
                                );
                              },
                            ),
                          ),
                        ),
                      ],
                    ),
    );
  }
}

class _LegendRow extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Wrap(
        spacing: 16,
        runSpacing: 6,
        children: const [
          _LegendItem(color: AppConstants.visitBlue, label: 'Visits'),
          _LegendItem(color: AppConstants.prescriptionGreen, label: 'Prescriptions'),
          _LegendItem(color: AppConstants.labOrange, label: 'Lab Reports'),
          _LegendItem(color: AppConstants.vitalPurple, label: 'Vitals'),
        ],
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 11, color: AppConstants.textSecondary)),
      ],
    );
  }
}

class _TimelineItem extends StatelessWidget {
  final _EmrEvent event;
  final Color color;
  final IconData icon;
  final String label;
  final bool isLast;

  const _TimelineItem({
    required this.event,
    required this.color,
    required this.icon,
    required this.label,
    required this.isLast,
  });

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Timeline column
          SizedBox(
            width: 40,
            child: Column(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: color.withAlpha(26),
                    shape: BoxShape.circle,
                    border: Border.all(color: color, width: 2),
                  ),
                  child: Icon(icon, color: color, size: 15),
                ),
                if (!isLast)
                  Expanded(
                    child: Container(
                      width: 2,
                      color: color.withAlpha(51),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          // Event card
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(bottom: isLast ? 0 : 12),
              child: Card(
                margin: EdgeInsets.zero,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: color.withAlpha(26),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              label,
                              style: TextStyle(
                                color: color,
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          const Spacer(),
                          Text(
                            DateFormat('dd MMM yyyy').format(event.date),
                            style: AppConstants.captionStyle,
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        event.title,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                          color: AppConstants.textPrimary,
                        ),
                      ),
                      if (event.subtitle != null) ...[
                        const SizedBox(height: 2),
                        Text(event.subtitle!, style: AppConstants.captionStyle),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
