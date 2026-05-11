import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../providers/visit_provider.dart';
import '../widgets/visit_card.dart';
import '../widgets/empty_state.dart';
import '../widgets/loading_widget.dart';
import '../core/constants.dart';

class VisitsScreen extends StatefulWidget {
  const VisitsScreen({super.key});

  @override
  State<VisitsScreen> createState() => _VisitsScreenState();
}

class _VisitsScreenState extends State<VisitsScreen> {
  String _selectedFilter = 'All';

  static const List<String> _filters = ['All', 'Pending', 'Active', 'Completed'];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<VisitProvider>().fetchVisits();
    });
  }

  List _filteredVisits(VisitProvider provider) {
    if (_selectedFilter == 'All') return provider.visits;
    return provider.visits
        .where((v) => v.status == _selectedFilter)
        .toList();
  }

  void _showCreateVisitDialog() {
    final patientIdCtrl = TextEditingController();
    final complaintCtrl = TextEditingController();
    final formKey = GlobalKey<FormState>();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.fromLTRB(
            20, 20, 20, MediaQuery.of(ctx).viewInsets.bottom + 20),
        child: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text('Create New Visit', style: AppConstants.subheadingStyle),
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
                controller: complaintCtrl,
                decoration:
                    const InputDecoration(labelText: 'Chief Complaint *'),
                maxLines: 3,
                validator: (v) =>
                    v == null || v.isEmpty ? 'Chief complaint required' : null,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () async {
                  if (!formKey.currentState!.validate()) return;
                  final error = await context.read<VisitProvider>().createVisit({
                    'patientId': int.tryParse(patientIdCtrl.text) ?? 0,
                    'chiefComplaint': complaintCtrl.text.trim(),
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
                        content: Text('Visit created'),
                        backgroundColor: AppConstants.successColor,
                      ),
                    );
                  }
                },
                child: const Text('Create Visit'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<VisitProvider>();
    final filtered = _filteredVisits(provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Visits'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.go('/dashboard'),
        ),
      ),
      body: Column(
        children: [
          // Filter chips
          SizedBox(
            height: 56,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              itemCount: _filters.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (context, index) {
                final filter = _filters[index];
                final selected = _selectedFilter == filter;
                return FilterChip(
                  label: Text(filter),
                  selected: selected,
                  onSelected: (_) {
                    setState(() => _selectedFilter = filter);
                  },
                  selectedColor: AppConstants.primaryColor.withAlpha(26),
                  checkmarkColor: AppConstants.primaryColor,
                  labelStyle: TextStyle(
                    color: selected
                        ? AppConstants.primaryColor
                        : AppConstants.textSecondary,
                    fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
                  ),
                );
              },
            ),
          ),
          Expanded(
            child: provider.isLoading
                ? const LoadingWidget(message: 'Loading visits...')
                : filtered.isEmpty
                    ? EmptyState(
                        icon: Icons.medical_services_outlined,
                        message: 'No visits found',
                        subMessage: 'Create a new visit to get started',
                        onAction: _showCreateVisitDialog,
                        actionLabel: 'Create Visit',
                      )
                    : RefreshIndicator(
                        onRefresh: () => provider.fetchVisits(),
                        child: ListView.builder(
                          padding: const EdgeInsets.only(bottom: 80, top: 4),
                          itemCount: filtered.length,
                          itemBuilder: (context, index) {
                            final visit = filtered[index];
                            return VisitCard(
                              visit: visit,
                              onTap: () => context.go('/visits/${visit.id}'),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showCreateVisitDialog,
        backgroundColor: AppConstants.primaryColor,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}
