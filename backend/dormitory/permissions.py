from typing import Iterable, Optional
from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasRequiredDjangoPerms(BasePermission):
    """
    DRF permission: view.permission_required = ["app_label.codename", ...]
    Grants access if request.user has ALL listed Django perms.
    If view.permission_required is missing/empty -> allow (use with IsAuthenticated together).
    """

    def has_permission(self, request, view) -> bool:
        required: Optional[Iterable[str]] = getattr(view, "permission_required", None)
        if not required:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return all(user.has_perm(perm) for perm in required)


class IsInAnyRole(BasePermission):
    """
    DRF permission: view.roles_any = ["admin", "manager", ...]
    Grants if user.profile has ANY of the listed role codes. Superuser always allowed.
    If roles_any is empty/missing -> allow.
    """

    def has_permission(self, request, view) -> bool:
        roles_any: Optional[Iterable[str]] = getattr(view, "roles_any", None)
        if not roles_any:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        profile = getattr(user, "profile", None)
        if not profile:
            return False
        return profile.roles.filter(code__in=roles_any).exists()


class IsInAllRoles(BasePermission):
    """
    DRF permission: view.roles_all = ["staff", "auditor", ...]
    Grants if user.profile has ALL of the listed role codes. Superuser always allowed.
    If roles_all is empty/missing -> allow.
    """

    def has_permission(self, request, view) -> bool:
        roles_all: Optional[Iterable[str]] = getattr(view, "roles_all", None)
        if not roles_all:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        profile = getattr(user, "profile", None)
        if not profile:
            return False
        user_roles = set(profile.roles.values_list("code", flat=True))
        return set(roles_all).issubset(user_roles)


class ReadOnly(BasePermission):
    """Allow only safe (GET/HEAD/OPTIONS) methods."""

    def has_permission(self, request, view) -> bool:
        return request.method in SAFE_METHODS
