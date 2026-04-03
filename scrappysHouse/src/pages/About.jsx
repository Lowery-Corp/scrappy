export default function About() {
  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "0 auto" }}>
      <h1>About</h1>
      <p>
        This is a RAG (Retrieval-Augmented Generation) service built with React and Vite,
        featuring intelligent document retrieval and AI-powered responses.
      </p>
      <div style={{
        backgroundColor: "#fff3cd",
        border: "1px solid #ffeaa7",
        padding: "1rem",
        borderRadius: "4px",
        marginBottom: "1rem"
      }}>
        <strong>🚧 Under Development</strong>
        <p style={{ margin: "0.5rem 0 0 0" }}>
          This RAG service is currently under active development and will be available soon.
        </p>
      </div>
      <h2>Features</h2>
      <ul style={{ textAlign: "left" }}>
        <li>Document ingestion and intelligent indexing</li>
        <li>AI-powered question answering with source citations</li>
        <li>User authentication with role-based permissions</li>
        <li>Protected routes for secure content access</li>
        <li>Admin panel for document management and system configuration</li>
        <li>Modern React with hooks and context</li>
      </ul>
    </div>
  );
}