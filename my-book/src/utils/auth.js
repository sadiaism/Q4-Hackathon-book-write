// Authentication utility functions for the Docusaurus app

/**
 * Get the authentication token from localStorage
 * @returns {string|null} The auth token or null if not found
 */
export function getAuthToken() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('authToken');
}

/**
 * Set the authentication token in localStorage
 * @param {string} token - The auth token to store
 */
export function setAuthToken(token) {
  if (typeof window === 'undefined') return;
  localStorage.setItem('authToken', token);
}

/**
 * Remove the authentication token from localStorage
 */
export function removeAuthToken() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
}

/**
 * Get the current user from localStorage
 * @returns {Object|null} The user object or null if not found
 */
export function getCurrentUser() {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (e) {
      console.error('Error parsing user data:', e);
      return null;
    }
  }
  return null;
}

/**
 * Check if the user is authenticated
 * @returns {boolean} True if authenticated, false otherwise
 */
export function isAuthenticated() {
  return !!getAuthToken();
}

/**
 * Get the base API URL for the backend
 * @returns {string} The base API URL
 */
export function getApiBaseUrl() {
  // Access Docusaurus config from window if available
  if (typeof window !== 'undefined' && window.docusaurus?.siteConfig?.customFields?.apiUrl) {
    return window.docusaurus.siteConfig.customFields.apiUrl;
  }
  // Fallback to localhost for development
  return 'http://localhost:8000';
}

/**
 * Make an authenticated API request
 * @param {string} endpoint - The API endpoint
 * @param {Object} options - Request options
 * @returns {Promise} The fetch response
 */
export async function authenticatedFetch(endpoint, options = {}) {
  const token = getAuthToken();
  const apiUrl = getApiBaseUrl();

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${apiUrl}${endpoint}`, config);

    // If the response is 401 (unauthorized), remove the token and redirect
    if (response.status === 401) {
      removeAuthToken();
      window.location.href = '/auth/signin';
    }

    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Sign out the current user
 */
export function signOut() {
  if (typeof window === 'undefined') return;
  removeAuthToken();
  // Optionally redirect to home or sign-in page
  window.location.href = '/';
}