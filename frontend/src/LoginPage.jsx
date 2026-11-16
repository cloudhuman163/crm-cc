import { useState } from "react";
import { api } from "./api";

export default function LoginPage({ onLogin }) {
  const [mode, setMode] = useState("login"); // login | register
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const path = mode === "login" ? "/auth/login" : "/auth/register";
      const data = await api(path, {
        method: "POST",
        body: { username, password, full_name: fullName },
      });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("username", data.username);
      onLogin(data.username);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: "10vh auto", fontFamily: "sans-serif" }}>
      <h2>{mode === "login" ? "Вход оператора" : "Регистрация"}</h2>
      <form onSubmit={submit} style={{ display: "grid", gap: 10 }}>
        <input placeholder="Логин" value={username} onChange={e => setUsername(e.target.value)} required />
        {mode === "register" && (
          <input placeholder="Имя оператора" value={fullName} onChange={e => setFullName(e.target.value)} />
        )}
        <input type="password" placeholder="Пароль" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} />
        {error && <div style={{ color: "crimson" }}>{error}</div>}
        <button disabled={busy}>{busy ? "..." : mode === "login" ? "Войти" : "Зарегистрироваться"}</button>
      </form>
      <button
        onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}
        style={{ marginTop: 12, background: "none", border: "none", cursor: "pointer", color: "#06c" }}
      >
        {mode === "login" ? "Нет аккаунта? Зарегистрироваться" : "Уже есть аккаунт? Войти"}
      </button>
    </div>
  );
}
