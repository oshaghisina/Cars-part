const DEFAULT_API_PATH = "/api/v1";

const stripTrailingSlash = (value) => value.replace(/\/$/, "");

export const resolveApiBaseUrl = () => {
  const envValue = import.meta?.env?.VITE_API_BASE_URL;
  if (envValue && envValue.trim()) {
    return stripTrailingSlash(envValue.trim());
  }

  if (typeof window !== "undefined" && window.location) {
    return stripTrailingSlash(`${window.location.origin}${DEFAULT_API_PATH}`);
  }

  return DEFAULT_API_PATH;
};

export const API_BASE_URL = resolveApiBaseUrl();
