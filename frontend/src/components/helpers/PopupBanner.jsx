import { useEffect, useState } from "react";

const popupStyles = {
  success:
    "border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-800/60 dark:bg-emerald-950/80 dark:text-emerald-200",
  error:
    "border-red-200 bg-red-50 text-red-800 dark:border-red-800/60 dark:bg-red-950/80 dark:text-red-200",
  warning:
    "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-800/60 dark:bg-amber-950/80 dark:text-amber-200",
  info:
    "border-indigo-200 bg-indigo-50 text-indigo-800 dark:border-indigo-800/60 dark:bg-indigo-950/80 dark:text-indigo-200",
};

export default function PopupBanner() {
  const [popup, setPopup] = useState(null);

  useEffect(() => {
    const handlePopupMessage = (event) => {
      setPopup(event.detail);

      window.clearTimeout(window.__popupBannerTimeout);

      window.__popupBannerTimeout = window.setTimeout(() => {
        setPopup(null);
      }, event.detail?.duration ?? 3000);
    };

    window.addEventListener("popup-message", handlePopupMessage);

    return () => {
      window.removeEventListener("popup-message", handlePopupMessage);
      window.clearTimeout(window.__popupBannerTimeout);
    };
  }, []);

  if (!popup) {
    return null;
  }

  const type = popup.type ?? "info";

  return (
    <div className="fixed left-0 right-0 top-4 z-50 flex justify-center px-4">
      <div
        className={[
          "w-full max-w-2xl rounded-2xl border px-4 py-3 shadow-xl backdrop-blur",
          "transition-all duration-200",
          popupStyles[type] ?? popupStyles.info,
        ].join(" ")}
        role="status"
      >
        <div className="flex items-start justify-between gap-4">
          <p className="text-sm font-medium">{popup.message}</p>

          <button
            type="button"
            onClick={() => setPopup(null)}
            className="rounded-full px-2 text-lg leading-none opacity-70 hover:opacity-100"
            aria-label="Close popup"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );
}