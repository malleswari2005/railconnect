from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from core.decorators import get_user_role
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, CustomAuthenticationForm

def register_view(request):
    """Handles new user registration."""
    if request.user.is_authenticated:
        role = get_user_role(request.user)
        if role == 'Admin':
            return redirect('/admin-portal/')
        elif role == 'TTE':
            return redirect('/tte/')
        elif role == 'Operations':
            return redirect('/operations/')
        return redirect('core:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Ensure new self-registered users are assigned to Passenger group
            passenger_group, _ = Group.objects.get_or_create(name='Passenger')
            user.groups.add(passenger_group)

            # Profile is auto-created by signal, update extra fields
            profile = user.profile
            profile.phone_number = form.cleaned_data.get('phone_number')
            profile.id_proof_type = form.cleaned_data.get('id_proof_type')
            profile.id_proof_number = form.cleaned_data.get('id_proof_number')
            profile.save()

            messages.success(request, "Account created. Please log in.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """Custom login view with flash messages and role-based next-url redirect."""
    if request.user.is_authenticated:
        role = get_user_role(request.user)
        if role == 'Admin':
            return redirect('/admin-portal/')
        elif role == 'TTE':
            return redirect('/tte/')
        elif role == 'Operations':
            return redirect('/operations/')
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)

            # Role-based redirect
            role = get_user_role(user)
            if role == 'Admin':
                return redirect('/admin-portal/')
            elif role == 'TTE':
                return redirect('/tte/')
            elif role == 'Operations':
                return redirect('/operations/')
            return redirect('core:home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """Handles logout."""
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('core:home')

@login_required
def profile_view(request):
    """User profile management view."""
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
    })

@login_required
def password_change_view(request):
    """Allows user to change password securely."""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password was successfully changed. Please log in with your new credentials.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/password_change.html', {'form': form})
