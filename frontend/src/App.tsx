import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Home from './pages/Home';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import AIDecisionLogs from './pages/AIDecisionLogs';
import EvolutionDashboard from './pages/EvolutionDashboard';

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
        {/* Other protected routes will go here */}
      </Routes>
    </Router>
  );
}

export default App;

