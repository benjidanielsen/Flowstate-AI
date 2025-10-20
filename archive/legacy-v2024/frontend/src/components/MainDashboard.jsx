import React from 'react';
import { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaChartLine, FaTasks, FaUsers, FaCog } from 'react-icons/fa';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  padding: 2rem;
  background: #f7f9fc;
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-weight: 700;
  font-size: 2.25rem;
  color: #222;
`;

const UserMenu = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 1rem;
  color: #555;
  cursor: pointer;

  &:hover {
    color: #0070f3;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
`;

const StatCard = styled.div`
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  transition: transform 0.25s ease, box-shadow 0.25s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgb(0 0 0 / 0.12);
  }
`;

const IconWrapper = styled.div`
  background: #0070f3;
  color: white;
  padding: 0.75rem;
  border-radius: 50%;
  font-size: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const StatInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const StatNumber = styled.span`
  font-weight: 700;
  font-size: 1.5rem;
  color: #222;
`;

const StatLabel = styled.span`
  font-size: 0.9rem;
  color: #666;
`;

const ChartsSection = styled.section`
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 16px rgb(0 0 0 / 0.08);
`;

const ChartTitle = styled.h2`
  margin-bottom: 1rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #222;
`;

// Placeholder chart component for demo
const ChartPlaceholder = styled.div`
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #0070f3 0%, #00c6ff 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.5rem;
  user-select: none;
`;

export default function MainDashboard() {
  const [stats, setStats] = useState({
    activeProjects: 8,
    tasksCompleted: 152,
    activeUsers: 24,
    systemStatus: 'Operational'
  });

  // Simulate dynamic updates or API fetch
  useEffect(() => {
    // Normally here would be fetching data from backend API
  }, []);

  return (
    <DashboardContainer>
      <Header>
        <Title>Flowstate AI Dashboard</Title>
        <UserMenu>
          <FaUsers />
          <span>Welcome, User</span>
          <FaCog />
        </UserMenu>
      </Header>

      <StatsGrid>
        <StatCard>
          <IconWrapper><FaTasks /></IconWrapper>
          <StatInfo>
            <StatNumber>{stats.activeProjects}</StatNumber>
            <StatLabel>Active Projects</StatLabel>
          </StatInfo>
        </StatCard>

        <StatCard>
          <IconWrapper><FaChartLine /></IconWrapper>
          <StatInfo>
            <StatNumber>{stats.tasksCompleted}</StatNumber>
            <StatLabel>Tasks Completed</StatLabel>
          </StatInfo>
        </StatCard>

        <StatCard>
          <IconWrapper><FaUsers /></IconWrapper>
          <StatInfo>
            <StatNumber>{stats.activeUsers}</StatNumber>
            <StatLabel>Active Users</StatLabel>
          </StatInfo>
        </StatCard>

        <StatCard>
          <IconWrapper><FaCog /></IconWrapper>
          <StatInfo>
            <StatNumber>{stats.systemStatus}</StatNumber>
            <StatLabel>System Status</StatLabel>
          </StatInfo>
        </StatCard>
      </StatsGrid>

      <ChartsSection>
        <ChartTitle>Project Progress Overview</ChartTitle>
        <ChartPlaceholder>Chart Coming Soon</ChartPlaceholder>
      </ChartsSection>
    </DashboardContainer>
  );
}
