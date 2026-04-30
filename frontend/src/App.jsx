import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Upload from "./pages/Upload";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"          element={<Home />} />
        <Route path="/upload"    element={<Upload />} />
        <Route path="/dashboard/:tableName" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}