// This is a module for client-side authorization state management

// caching to avoid redundant api calls

let currentUser = null;
let fetchPromise = null;

// if we already have a cached user, then we return it immediately
export async function getCurrentUser() {
  if (currentUser) {
    return currentUser;
  }

  // Return in-progress fetch to prevent duplicate API calls; this is important as multiple parts of the page might call the getCurrentUser at the same time and we don't want to spam the API with duplicate requests
  if (fetchPromise) {
    return fetchPromise;
  }

  const token = localStorage.getItem("access_token");
  if (!token) {
    return null;
  }

  fetchPromise = (async () => {
    try {
      const response = await fetch("/api/users/me", { // we are calling this api endpoint instead of just decoding the token in JS because calling this endpoint validates that the token is still good on the server and gets us the full user info. So the server is the authority whether a token is still valid.
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        currentUser = await response.json();
        return currentUser;
      }

      localStorage.removeItem("access_token");
      return null;
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    } finally {
      fetchPromise = null;
    }
  })();

  return fetchPromise;
}

export function logout() {
  localStorage.removeItem("access_token");
  currentUser = null;
  window.location.href = "/";
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function setToken(token) {
  localStorage.setItem("access_token", token);
}

export function clearUserCache() {
  currentUser = null;
}