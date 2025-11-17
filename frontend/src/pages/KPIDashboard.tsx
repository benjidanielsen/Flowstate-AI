import React, { useState, useEffect } from 'react';
import { Card, Title, Text, Metric, Flex, Badge, TabGroup, TabList, Tab, TabPanels, TabPanel } from '@tremor/react';
import { ChartBarIcon, ChartPieIcon, ArrowUpIcon, ArrowDownIcon, ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { LineChart, BarChart } from '@tremor/react';
import { api } from '../services/api';
import logger from '../utils/logger';

interface KPI {
  name: string;
  value: number | string;
  unit?: string;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  description?: string;
  status?: 'success' | 'warning' | 'error' | 'info';
}

interface ChartData {
  date: string;
  value: number;
}

const KPIDashboard: React.FC = () => {
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<string>('executive');

  useEffect(() => {
    fetchKPIs();
  }, [selectedTab]);

  const fetchKPIs = async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate API call based on selectedTab
      const response = await api.get(`/kpis?category=${selectedTab}`);
      setKpis(response.data);
    } catch (err) {
      logger.error('Failed to fetch KPIs', err);
      setError('Failed to load KPIs. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const renderKPIs = () => {
    if (loading) return <Text>Loading KPIs...</Text>;
    if (error) return <Text className="text-red-500">Error: {error}</Text>;
    if (kpis.length === 0) return <Text>No KPIs available for this category.</Text>;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {kpis.map((kpi, index) => (
          <Card key={index} className="flex flex-col justify-between">
            <div>
              <Flex justifyContent="between" alignItems="center">
                <Text>{kpi.name}</Text>
                {kpi.status && (
                  <Badge color={kpi.status === 'success' ? 'emerald' : kpi.status === 'warning' ? 'amber' : 'rose'}>
                    {kpi.status.toUpperCase()}
                  </Badge>
                )}
              </Flex>
              <Metric className="mt-2">
                {typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}
                {kpi.unit && <span className="text-sm text-gray-500"> {kpi.unit}</span>}
              </Metric>
              {kpi.change !== undefined && (
                <Flex className="mt-4" justifyContent="start" alignItems="center">
                  {kpi.changeType === 'increase' && <ArrowUpIcon className="h-4 w-4 text-emerald-500" />}
                  {kpi.changeType === 'decrease' && <ArrowDownIcon className="h-4 w-4 text-rose-500" />}
                  <Text className={`ml-1 ${kpi.changeType === 'increase' ? 'text-emerald-500' : kpi.changeType === 'decrease' ? 'text-rose-500' : ''}`}>
                    {kpi.change > 0 ? '+' : ''}{kpi.change.toLocaleString()}{kpi.unit && <span className="text-sm text-gray-500"> {kpi.unit}</span>}
                  </Text>
                  <Text className="ml-2 text-gray-500">vs. previous period</Text>
                </Flex>
              )}
            </div>
            {kpi.description && <Text className="mt-4 text-sm text-gray-500">{kpi.description}</Text>}
          </Card>
        ))}
      </div>
    );
  };

  const chartData: ChartData[] = [
    { date: 'Jan 23', value: 2890 }, { date: 'Feb 23', value: 2756 }, { date: 'Mar 23', value: 3322 },
    { date: 'Apr 23', value: 3470 }, { date: 'May 23', value: 3750 }, { date: 'Jun 23', value: 3880 },
    { date: 'Jul 23', value: 3830 }, { date: 'Aug 23', value: 3900 }, { date: 'Sep 23', value: 3950 },
    { date: 'Oct 23', value: 4000 }, { date: 'Nov 23', value: 4100 }, { date: 'Dec 23', value: 4200 },
  ];

  return (
    <main className="p-6">
      <Title>Flowstate-AI KPI Dashboard</Title>
      <Text>Key Performance Indicators for Flowstate-AI operations and business impact.</Text>

      <TabGroup className="mt-6" onIndexChange={(index) => setSelectedTab(['executive', 'operational', 'business', 'quality', 'learning'][index])}>
        <TabList variant="line" defaultValue="executive">
          <Tab value="executive" icon={ChartPieIcon}>Executive Summary</Tab>
          <Tab value="operational" icon={ChartBarIcon}>Operational</Tab>
          <Tab value="business" icon={ChartBarIcon}>Business Impact</Tab>
          <Tab value="quality" icon={CheckCircleIcon}>Quality</Tab>
          <Tab value="learning" icon={ExclamationTriangleIcon}>Learning & Evolution</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <div className="mt-6">
              <Title>Executive Summary KPIs</Title>
              {renderKPIs()}
              <Card className="mt-6">
                <Title>Monthly Active Users</Title>
                <LineChart
                  className="mt-4 h-72"
                  data={chartData}
                  index="date"
                  categories={['value']}
                  colors={['blue']}
                  yAxisWidth={30}
                />
              </Card>
            </div>
          </TabPanel>
          <TabPanel>
            <div className="mt-6">
              <Title>Operational KPIs</Title>
              {renderKPIs()}
              <Card className="mt-6">
                <Title>API Latency (ms)</Title>
                <BarChart
                  className="mt-4 h-72"
                  data={chartData.map(d => ({ ...d, value: d.value / 10 }))} // Simulate latency
                  index="date"
                  categories={['value']}
                  colors={['teal']}
                  yAxisWidth={30}
                />
              </Card>
            </div>
          </TabPanel>
          <TabPanel>
            <div className="mt-6">
              <Title>Business Impact KPIs</Title>
              {renderKPIs()}
            </div>
          </TabPanel>
          <TabPanel>
            <div className="mt-6">
              <Title>Quality KPIs</Title>
              {renderKPIs()}
            </div>
          </TabPanel>
          <TabPanel>
            <div className="mt-6">
              <Title>Learning & Evolution KPIs</Title>
              {renderKPIs()}
            </div>
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </main>
  );
};

export default KPIDashboard;

