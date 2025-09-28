import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, TrendingUp, Calendar, AlertCircle } from 'lucide-react';
import { customerApi, interactionApi } from '../services/api';
import { PipelineStats, Interaction, PipelineStatus } from '../types';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<PipelineStats>({});
  const [upcomingInteractions, setUpcomingInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsData, interactionsData] = await Promise.all([
          customerApi.getStats(),
          interactionApi.getUpcoming(10)
        ]);
        setStats(statsData);
        setUpcomingInteractions(interactionsData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const totalCustomers = Object.values(stats).reduce((sum, count) => sum + count, 0);

  const pipelineSteps = [
    { key: PipelineStatus.LEAD, label: 'Leads', color: 'bg-gray-500' },
    { key: PipelineStatus.RELATIONSHIP, label: 'Relationship', color: 'bg-blue-500' },
    { key: PipelineStatus.INVITED, label: 'Invited', color: 'bg-yellow-500' },
    { key: PipelineStatus.QUALIFIED, label: 'Qualified', color: 'bg-orange-500' },
    { key: PipelineStatus.PRESENTATION_SENT, label: 'Presentation Sent', color: 'bg-purple-500' },
    { key: PipelineStatus.FOLLOW_UP, label: 'Follow-up', color: 'bg-indigo-500' },
    { key: PipelineStatus.SIGNED_UP, label: 'Signed Up', color: 'bg-green-500' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Your Flowstate-AI CRM overview</p>
        </div>
        <Link
          to="/customers"
          className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
        >
          View All Customers
        </Link>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-md">
              <Users className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <h2 className="text-sm font-medium text-gray-500">Total Customers</h2>
              <p className="text-2xl font-bold text-gray-900">{totalCustomers}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-md">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <h2 className="text-sm font-medium text-gray-500">Signed Up</h2>
              <p className="text-2xl font-bold text-gray-900">{stats[PipelineStatus.SIGNED_UP] || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-md">
              <Calendar className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <h2 className="text-sm font-medium text-gray-500">Upcoming</h2>
              <p className="text-2xl font-bold text-gray-900">{upcomingInteractions.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-md">
              <AlertCircle className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <h2 className="text-sm font-medium text-gray-500">Follow-ups</h2>
              <p className="text-2xl font-bold text-gray-900">{stats[PipelineStatus.FOLLOW_UP] || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pipeline Overview */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Overview</h2>
          <div className="space-y-4">
            {pipelineSteps.map((step) => (
              <div key={step.key} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`w-4 h-4 rounded ${step.color} mr-3`}></div>
                  <span className="text-sm font-medium text-gray-900">{step.label}</span>
                </div>
                <span className="text-sm text-gray-500">{stats[step.key] || 0} customers</span>
              </div>
            ))}
          </div>
        </div>

        {/* Upcoming Interactions */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Interactions</h2>
          {upcomingInteractions.length === 0 ? (
            <p className="text-gray-500 text-sm">No upcoming interactions</p>
          ) : (
            <div className="space-y-3">
              {upcomingInteractions.slice(0, 5).map((interaction) => (
                <div key={interaction.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {interaction.type.charAt(0).toUpperCase() + interaction.type.slice(1)}
                    </p>
                    <p className="text-xs text-gray-500">{interaction.content}</p>
                  </div>
                  <div className="text-xs text-gray-400">
                    {interaction.scheduled_for && new Date(interaction.scheduled_for).toLocaleDateString()}
                  </div>
                </div>
              ))}
              {upcomingInteractions.length > 5 && (
                <div className="text-center pt-2">
                  <span className="text-sm text-gray-500">
                    +{upcomingInteractions.length - 5} more interactions
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;