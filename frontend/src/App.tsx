import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Home from './pages/Home';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import AIDecisionLogs from './pages/AIDecisionLogs';
import EvolutionDashboard from './pages/EvolutionDashboard';
import KPIDashboard from './pages/KPIDashboard';
import AdminDashboard from './pages/AdminDashboard';
import CRMBoard from './pages/CRMBoard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-decision-logs"
          element={
            <ProtectedRoute>
              <AIDecisionLogs />
            </ProtectedRoute>
          }
        />
        <Route
          path="/evolution"
          element={
            <ProtectedRoute>
              <EvolutionDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/kpis"
          element={
            <ProtectedRoute>
              <KPIDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/crm"
          element={
            <ProtectedRoute>
              <CRMBoard />
            </ProtectedRoute>
          }
        />
        {/* Other protected routes will go here */}
      </Routes>
    </Router>
  );
}

export default App;

