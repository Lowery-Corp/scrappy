import { useState } from "react";
import { Link, NavLink, Navigate, Route, Routes } from "react-router";
import { useAuth } from "./auth/AuthProvider";
import ProtectedRoute from "./components/ProtectedRoute";
import UserLayout from "./layouts/UserLayout";
import AuthLayout from "./layouts/AuthLayout";
import Login from "./pages/Login";
import CreateUser from "./pages/CreateUser";
import Admin from "./pages/Admin";
import About from "./pages/About";
import FileStore from "./pages/FileStore";
import Unauthorized from "./pages/Unauthorized";
import DocumentChat from "./pages/DocumentChat";

export default function App() {
  const { user, logout, isAuthenticated, authLoading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = isAuthenticated
    ? [
        { to: "/about", label: "About" },
        { to: "/store", label: "File Store" },
        { to: "/chat/new", label: "Document Chat" },
        ...(user?.permissions?.includes("read:admin")
          ? [{ to: "/auth/admin", label: "Admin" }]
          : []),
      ]
    : [{ to: "/about", label: "About" }];

  const closeMobileMenu = () => setMobileMenuOpen(false);

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm text-slate-500">
        <div className="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-2 shadow-sm">
          <span className="h-2 w-2 animate-pulse rounded-full bg-indigo-500" />
          Loading your workspace…
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <nav className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 shadow-[0_1px_12px_rgba(15,23,42,0.04)] backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/90">
        <div className="mx-auto max-w-[1600px] px-4 sm:px-6 lg:px-8">
          <div className="flex h-[4.25rem] items-center justify-between gap-4">
            <div className="flex min-w-0 items-center gap-8">
              <Link
                to={isAuthenticated ? "/" : "/user/login"}
                onClick={closeMobileMenu}
                className="flex shrink-0 items-center gap-2.5 text-lg font-bold tracking-tight text-slate-950 dark:text-white"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-black text-white shadow-lg shadow-indigo-500/20">
                  S
                </span>
                Scrappy
              </Link>

              <div className="hidden min-w-0 items-center gap-1 md:flex">
                {navItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `rounded-lg px-3 py-2 text-sm font-medium transition ${
                        isActive
                          ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-300"
                          : "text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
                      }`
                    }
                  >
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/"
                    className="hidden rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:border-indigo-200 hover:text-indigo-700 sm:inline-flex dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:border-indigo-500/50 dark:hover:text-indigo-300"
                  >
                    {user?.username}
                  </Link>
                  <button
                    onClick={logout}
                    className="hidden rounded-lg px-3 py-2 text-sm font-semibold text-slate-500 transition hover:bg-rose-50 hover:text-rose-600 sm:inline-flex dark:text-slate-300 dark:hover:bg-rose-500/10 dark:hover:text-rose-300"
                  >
                    Sign out
                  </button>
                </>
              ) : (
                <Link
                  to="/user/login"
                  className="hidden rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 sm:inline-flex"
                >
                  Sign in
                </Link>
              )}
              <button
                type="button"
                aria-expanded={mobileMenuOpen}
                aria-controls="mobile-navigation"
                aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
                onClick={() => setMobileMenuOpen((open) => !open)}
                className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition hover:bg-slate-100 md:hidden dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                <span className="text-lg">{mobileMenuOpen ? "×" : "☰"}</span>
              </button>
            </div>
          </div>

          {mobileMenuOpen && (
            <div id="mobile-navigation" className="border-t border-slate-100 py-3 md:hidden dark:border-slate-800">
              <div className="grid gap-1">
                {navItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={closeMobileMenu}
                    className={({ isActive }) =>
                      `rounded-lg px-3 py-2.5 text-sm font-medium ${
                        isActive
                          ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-300"
                          : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                      }`
                    }
                  >
                    {item.label}
                  </NavLink>
                ))}
                {isAuthenticated ? (
                  <button
                    onClick={() => {
                      closeMobileMenu();
                      logout();
                    }}
                    className="mt-1 rounded-lg px-3 py-2.5 text-left text-sm font-semibold text-rose-600 hover:bg-rose-50 dark:text-rose-300 dark:hover:bg-rose-500/10"
                  >
                    Sign out
                  </button>
                ) : (
                  <Link
                    to="/user/login"
                    onClick={closeMobileMenu}
                    className="mt-1 rounded-lg bg-indigo-600 px-3 py-2.5 text-sm font-semibold text-white"
                  >
                    Sign in
                  </Link>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        <Routes>
          <Route path="user" element={<UserLayout />}>
            <Route path="login" element={<Login />} />
            <Route path="create" element={<CreateUser />} />
          </Route>

          <Route path="auth" element={<AuthLayout />}>
            <Route element={<ProtectedRoute requiredPermission="read:admin" />}>
              <Route path="admin" element={<Admin />} />
            </Route>
          </Route>

          <Route path="unauthorized" element={<Unauthorized />} />
          <Route path="about" element={<About />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<About />} />
            <Route path="/home" element={<About />} />
            <Route path="/store" element={<FileStore />} />
            <Route path="/chat/:conversationId?" element={<DocumentChat />} />
          </Route>

          <Route path="*" element={<Navigate to="/about" replace />} />
        </Routes>
      </main>
    </div>
  );
}
