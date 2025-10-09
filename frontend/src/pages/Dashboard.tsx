import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, TrendingUp, Calendar, AlertCircle } from 'lucide-react';
import { customerApi, interactionApi, statsApi } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { PipelineStats, Interaction, PipelineStatus, Stats } from '../types';

const Dashboard: React.FC = () => {
  const [pipelineStats, setPipelineStats] = useState<PipelineStats>({});
  const [upcomingInteractions, setUpcomingInteractions] = useState<Interaction[]>([]);
  const [allStats, setAllStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [pipelineStatsData, interactionsData, allStatsData] = await Promise.all([
          customerApi.getStats(),
          interactionApi.getUpcoming(10),
          statsApi.getStats()
        ]);
        setPipelineStats(pipelineStatsData);
        setUpcomingInteractions(interactionsData);
        setAllStats(allStatsData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const totalCustomers = allStats ? Object.values(allStats.countsByStatus).reduce((sum, count) => sum + count, 0) : 0;

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
              <h2 className="text-sm font-medium text-gray-500">Overdue Follow-ups</h2>
              <p className="text-2xl font-bold text-gray-900">{allStats?.extraCounts?.overdue_followups || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Demographics */}
      {allStats?.customerDemographics && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Customer Demographics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h3 className="text-md font-medium text-gray-700 mb-2">By Country</h3>
              <ul className="space-y-1">
                {Object.entries(allStats.customerDemographics.byCountry).map(([country, count]) => (
                  <li key={country} className="flex justify-between text-sm text-gray-600">
                    <span>{country || 'Unknown'}</span>
                    <span>{count}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-md font-medium text-gray-700 mb-2">By Language</h3>
              <ul className="space-y-1">
                {Object.entries(allStats.customerDemographics.byLanguage).map(([language, count]) => (
                  <li key={language} className="flex justify-between text-sm text-gray-600">
                    <span>{language || 'Unknown'}</span>
                    <span>{count}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-md font-medium text-gray-700 mb-2">By Source</h3>
              <ul className="space-y-1">
                {Object.entries(allStats.customerDemographics.bySource).map(([source, count]) => (
                  <li key={source} className="flex justify-between text-sm text-gray-600">
                    <span>{source || 'Unknown'}</span>
                    <span>{count}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Interaction Summary */}
        {allStats?.interactionSummary && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Interaction Summary</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Total Interactions:</span>
                <span className="text-lg font-bold text-gray-900">{allStats.interactionSummary.totalInteractions}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Avg. Interactions per Customer:</span>
                <span className="text-lg font-bold text-gray-900">{allStats.interactionSummary.avgInteractionsPerCustomer.toFixed(2)}</span>
              </div>
              <h3 className="text-md font-medium text-gray-700 mt-4 mb-2">Interactions by Type</h3>
              <ul className="space-y-1">
                {Object.entries(allStats.interactionSummary.byType).map(([type, count]) => (
                  <li key={type} className="flex justify-between text-sm text-gray-600">
                    <span>{type.charAt(0).toUpperCase() + type.slice(1)}</span>
                    <span>{count}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Pipeline Conversion Rates */}
        {allStats?.pipelineConversionRates && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Conversion Rates</h2>
            <div className="space-y-3">
              {Object.entries(allStats.pipelineConversionRates).map(([stagePair, rate]) => (
                <div key={stagePair} className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">{stagePair.replace(/_/g, ' ').replace(/to/g, 'to').replace(/\b\w/g, (l) => l.toUpperCase())}:</span>
                  <span className="text-lg font-bold text-gray-900">{rate.toFixed(2)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pipeline Overview */}
        <div className="bg-white p-6 rounded-lg shadow lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Overview</h2>
          <div className="flex overflow-x-auto pb-4 -mx-6 px-6">
            {pipelineSteps.map((step) => (
              <div key={step.key} className="flex-shrink-0 w-64 mr-4">
                <div className="bg-gray-100 rounded-lg p-4 h-full flex flex-col">
                  <h3 className="font-semibold text-gray-800 mb-2 flex items-center">
                    <span className={`w-3 h-3 rounded-full ${step.color} mr-2`}></span>
                    {step.label}
                  </h3>
                  <p className="text-2xl font-bold text-gray-900">{stats[step.key] || 0}</p>
                  <p className="text-sm text-gray-500">customers</p>
                  <Link
                    to={`/customers?status=${step.key}`}
                    className="mt-auto inline-flex items-center text-primary-600 hover:text-primary-700 text-sm font-medium pt-2"
                  >
                    View Customers <ArrowRight size={16} className="ml-1" />
                  </Link>
                </div>
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
                  <div className="flex items-center space-x-3">
                    <div className="text-xs text-gray-400">
                      {interaction.scheduled_for && new Date(interaction.scheduled_for).toLocaleDateString()}
                    </div>
                    <CompleteButton
                      interaction={interaction}
                      onComplete={() => setUpcomingInteractions((prev) => prev.filter((i) => i.id !== interaction.id))}
                    />
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

// Small local component for completing an interaction
type CompleteButtonProps = {
  interaction: Interaction;
  onComplete: () => void;
};

const CompleteButton: React.FC<CompleteButtonProps> = ({ interaction, onComplete }) => {
  const [loading, setLoading] = React.useState(false);
  const { push } = useToast();

  const handleComplete = async () => {
    if (loading) return;
    setLoading(true);
    try {
      await interactionApi.complete(interaction.id);
      onComplete();
      push('Interaction completed', 'success');
    } catch (err: unknown) {
      console.error('Failed to complete interaction', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to complete interaction';
      push(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleComplete}
      disabled={loading}
      className={`text-sm px-2 py-1 rounded ${loading ? 'bg-gray-300 text-gray-600' : 'bg-green-500 text-white hover:bg-green-600'}`}
    >
      {loading ? 'Completing...' : 'Complete'}
    </button>
  );
};