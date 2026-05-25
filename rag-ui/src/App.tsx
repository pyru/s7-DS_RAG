import { Routes, Route, Navigate } from 'react-router-dom';
import { RunsProvider } from './context/RunsContext';
import Navbar from './components/Navbar';
import QueriesPage from './components/QueriesPage';
import DocumentsPage from './components/DocumentsPage';

export default function App() {
  return (
    <RunsProvider>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to="/queries" replace />} />
        <Route path="/queries" element={<QueriesPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
      </Routes>
    </RunsProvider>
  );
}
