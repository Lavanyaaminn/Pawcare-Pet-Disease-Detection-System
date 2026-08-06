/**
 * PawCare – Client-Side Form Validation
 * Shared validation helpers for login and register forms.
 */

/**
 * Show a client-side error message in the #clientError box.
 * @param {string} message - The error text to display.
 */
function showClientError(message) {
  var errorBox = document.getElementById("clientError");
  errorBox.textContent = message;
  errorBox.style.display = "block";
}

/**
 * Hide the client-side error box.
 */
function hideClientError() {
  var errorBox = document.getElementById("clientError");
  errorBox.style.display = "none";
  errorBox.textContent = "";
}

/**
 * Validate email format using a simple regex pattern.
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
  var pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

/**
 * Validate the login form before submission.
 * @param {Event} event
 */
function validateLogin(event) {
  hideClientError();

  var email = document.getElementById("email").value.trim();
  var password = document.getElementById("password").value;

  if (!email || !password) {
    event.preventDefault();
    showClientError("Email and password are required.");
    return false;
  }

  if (!isValidEmail(email)) {
    event.preventDefault();
    showClientError("Please enter a valid email address.");
    return false;
  }

  return true;
}

/**
 * Validate the register form before submission.
 * @param {Event} event
 */
function validateRegister(event) {
  hideClientError();

  var fullName = document.getElementById("full_name").value.trim();
  var email = document.getElementById("email").value.trim();
  var password = document.getElementById("password").value;
  var confirmPassword = document.getElementById("confirm_password").value;

  if (!fullName || !email || !password || !confirmPassword) {
    event.preventDefault();
    showClientError("All fields are required. Please fill in every field.");
    return false;
  }

  if (!isValidEmail(email)) {
    event.preventDefault();
    showClientError("Please enter a valid email address.");
    return false;
  }

  if (password.length < 6) {
    event.preventDefault();
    showClientError("Password must be at least 6 characters long.");
    return false;
  }

  if (password !== confirmPassword) {
    event.preventDefault();
    showClientError("Passwords do not match. Please try again.");
    return false;
  }

  return true;
}
