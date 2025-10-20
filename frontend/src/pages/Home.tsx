import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home: React.FC = () => {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Welcome to Flowstate-AI</h1>
        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          Logout
        </button>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">You are logged in!</h2>
        <p className="text-gray-700">This is a placeholder for your main application content. You can navigate to the dashboard or other features from here.</p>
        <div className="mt-4 space-y-2">
          <Link to="/dashboard" className="text-blue-500 hover:underline block">Go to Dashboard</Link>
          <Link to="/analytics" className="text-blue-500 hover:underline block">View Analytics Preview</Link>
        </div>
      </div>
    </div>
  );
};

export default Home;

