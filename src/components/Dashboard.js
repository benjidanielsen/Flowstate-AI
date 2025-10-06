import React, { useEffect, useState } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend } from 'chart.js';
import './Dashboard.css';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend);

const Dashboard = () => {
  const [pipelineData, setPipelineData] = useState(null);

  useEffect(() => {
    // Fake fetch simulation - replace with real API call
    const fetchData = async () => {
      // Example data representing Frazer Method pipeline stages
      const data = {
        stages: ['Lead In', 'Contacted', 'Qualified', 'Proposal Sent', 'Negotiation', 'Closed Won', 'Closed Lost'],
        counts: [120, 90, 70, 55, 45, 30, 15],
        revenue: [0, 0, 0, 15000, 12000, 55000, 0],
        conversionRates: [75, 78, 79, 82, 67, 100, 0]
      };
      setPipelineData(data);
    };

    fetchData();
  }, []);

  if (!pipelineData) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  const lineChartData = {
    labels: pipelineData.stages,
    datasets: [
      {
        label: 'Conversion Rate (%)',
        data: pipelineData.conversionRates,
        fill: false,
        backgroundColor: '#4A90E2',
        borderColor: '#4A90E2',
        tension: 0.3
      }
    ]
  };

  const barChartData = {
    labels: pipelineData.stages,
    datasets: [
      {
        label: 'Number of Leads',
        data: pipelineData.counts,
        backgroundColor: '#50E3C2'
      }
    ]
  };

  const pieChartData = {
    labels: ['Closed Won', 'Closed Lost'],
    datasets: [
      {
        label: 'Sales Outcome',
        data: [pipelineData.counts[5], pipelineData.counts[6]],
        backgroundColor: ['#7ED321', '#D0021B']
      }
    ]
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Frazer Method Pipeline Dashboard</h1>
      </header>
      <section className="dashboard-charts">
        <div className="chart-card">
          <h2>Pipeline Stage Counts</h2>
          <Bar data={barChartData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
        </div>
        <div className="chart-card">
          <h2>Conversion Rates by Stage</h2>
          <Line data={lineChartData} options={{ responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }} />
        </div>
        <div className="chart-card small">
          <h2>Sales Outcomes</h2>
          <Pie data={pieChartData} options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }} />
        </div>
      </section>
      <footer className="dashboard-footer">
        <small>© 2024 Flowstate-AI | Frazer Method CRM</small>
      </footer>
    </div>
  );
};

export default Dashboard;
