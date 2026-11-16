import { useState } from "react";
import LoginPage from "./LoginPage";

function OperatorWindow({ username, onLogout }) {
  return (
    <div style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h2>CRM — окно оператора</h2>
      <p>Вы вошли как <b>{username}</b>.</p>
      {/* Сюда дальше: список кампаний, старт обзвона, события звонка */}
      <button onClick={onLogout}>Выйти</button>
    </div>
  );
}

export default function App() {
  const [username, setUsername] = useState(() => {
    const hasToken = localStorage.getItem("token");
    return hasToken ? localStorage.getItem("username") : null;
  });

  if (!username) return <LoginPage onLogin={setUsername} />;
  return (
    <OperatorWindow
      username={username}
      onLogout={() => { localStorage.clear(); setUsername(null); }}
    />
  );
}
