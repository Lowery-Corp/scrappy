export default function About() {
    return (
      <div style={{ padding: "2rem", maxWidth: "600px", margin: "0 auto" }}>
        <h1>About</h1>
        <p>
          This is a React application built with Vite, featuring authentication
          and protected routes.
        </p>
        <h2>Features</h2>
        <ul style={{ textAlign: "left" }}>
          <li>User authentication with role-based permissions</li>
          <li>Protected routes for secure content</li>
          <li>Admin panel for privileged users</li>
          <li>Modern React with hooks and context</li>
        </ul>
      </div>
    );
  }