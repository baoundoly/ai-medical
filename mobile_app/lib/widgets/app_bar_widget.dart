import 'package:flutter/material.dart';

import '../core/constants.dart';

class AppBarWidget extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final bool showBack;
  final VoidCallback? onBack;
  final Widget? bottom;

  const AppBarWidget({
    super.key,
    required this.title,
    this.actions,
    this.showBack = false,
    this.onBack,
    this.bottom,
  });

  @override
  Size get preferredSize =>
      Size.fromHeight(bottom != null ? kToolbarHeight + 48 : kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title),
      backgroundColor: AppConstants.primaryColor,
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: true,
      leading: showBack
          ? IconButton(
              icon: const Icon(Icons.arrow_back_ios_new, size: 20),
              onPressed: onBack ?? () => Navigator.of(context).pop(),
            )
          : null,
      automaticallyImplyLeading: showBack,
      actions: actions,
      bottom: bottom != null ? PreferredSize(
        preferredSize: const Size.fromHeight(48),
        child: bottom!,
      ) : null,
    );
  }
}
