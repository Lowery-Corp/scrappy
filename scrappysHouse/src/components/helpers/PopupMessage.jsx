export function popupMessage(message, type = "info", duration = 3000) {
  window.dispatchEvent(
    new CustomEvent("popup-message", {
      detail: {
        message,
        type,
        duration,
      },
    }),
  );
}