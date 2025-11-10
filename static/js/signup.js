// Signup Page Script
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signup-form');
    const errorDiv = document.getElementById('error-message');
    const successDiv = document.getElementById('success-message');
    const signupBtn = document.getElementById('signup-btn');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');

    // Password strength indicator
    const strengthBar = document.querySelector('.password-strength-bar');
    const passwordHint = document.querySelector('.password-hint');

    // Check password strength
    passwordInput.addEventListener('input', function() {
        const password = passwordInput.value;
        const strength = checkPasswordStrength(password);
        
        strengthBar.className = 'password-strength-bar ' + strength.class;
        passwordHint.textContent = strength.message;
        passwordHint.style.color = strength.color;
    });

    // Form submit handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // Validation
        if (!username || !email || !password || !confirmPassword) {
            showError('Please fill in all fields');
            return;
        }

        if (username.length < 3) {
            showError('Username must be at least 3 characters');
            return;
        }

        if (!isValidEmail(email)) {
            showError('Please enter a valid email address');
            return;
        }

        if (password.length < 6) {
            showError('Password must be at least 6 characters');
            return;
        }

        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }

        // Hide messages
        hideMessages();
        
        // Disable button
        signupBtn.disabled = true;
        signupBtn.textContent = 'Creating Account...';

        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                showSuccess('Account created successfully! Redirecting to login...');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showError(data.error || 'Signup failed. Please try again.');
                signupBtn.disabled = false;
                signupBtn.textContent = 'Sign Up';
            }
        } catch (error) {
            console.error('Signup error:', error);
            showError('Connection error. Please check your internet and try again.');
            signupBtn.disabled = false;
            signupBtn.textContent = 'Sign Up';
        }
    });

    // Helper functions
    function checkPasswordStrength(password) {
        if (password.length === 0) {
            return { class: '', message: '', color: '#666' };
        }
        
        if (password.length < 6) {
            return { 
                class: 'weak', 
                message: 'Weak - Use at least 6 characters', 
                color: '#f44336' 
            };
        }
        
        const hasLower = /[a-z]/.test(password);
        const hasUpper = /[A-Z]/.test(password);
        const hasNumber = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*]/.test(password);
        
        const strength = [hasLower, hasUpper, hasNumber, hasSpecial].filter(Boolean).length;
        
        if (strength <= 2) {
            return { 
                class: 'medium', 
                message: 'Medium - Add numbers or special characters', 
                color: '#ff9800' 
            };
        }
        
        return { 
            class: 'strong', 
            message: 'Strong password!', 
            color: '#4caf50' 
        };
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        successDiv.style.display = 'none';
    }

    function showSuccess(message) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        errorDiv.style.display = 'none';
    }

    function hideMessages() {
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';
    }
});
