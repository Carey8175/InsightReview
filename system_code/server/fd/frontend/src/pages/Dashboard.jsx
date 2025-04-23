import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Bar, Pie, Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from 'chart.js';
import ReactWordcloud from 'react-wordcloud';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement);

const Dashboard = () => {
  // State for date range filter
  const [startDate, setStartDate] = useState(new Date('2022-09-01'));
  const [endDate, setEndDate] = useState(new Date('2022-10-31'));
  
  // State for other filters
  const [realReviews, setRealReviews] = useState('');
  const [sentiment, setSentiment] = useState('');
  
  // State for chart data
  const [botRateData, setBotRateData] = useState({ labels: [], datasets: [] });
  const [sentimentData, setSentimentData] = useState({ labels: [], datasets: [] });
  const [wordcloudData, setWordcloudData] = useState([]);
  const [reviewTrendData, setReviewTrendData] = useState({ labels: [], datasets: [] });
  
  // State for loading status
  const [loading, setLoading] = useState(true);
  
  // Function to format date for API requests
  const formatDate = (date) => {
    if (!date) return null;
    return date.toISOString().split('T')[0]; // Format as YYYY-MM-DD
  };
  
  // Function to build query parameters
  const buildQueryParams = () => {
    const params = {};
    
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    if (realReviews) params.real_reviews = realReviews;
    if (sentiment) params.sentiment = sentiment;
    
    return params;
  };
  
  // Function to fetch all dashboard data
  const fetchDashboardData = async () => {
    setLoading(true);
    const params = buildQueryParams();
    
    try {
      // Fetch bot rate data
      const botRateResponse = await axios.get('/api/dashboard/bot_rate', { params });
      const botRateChartData = {
        labels: botRateResponse.data.data.map(item => item.date),
        datasets: [{
          label: 'Bot Rate (%)',
          data: botRateResponse.data.data.map(item => item.bot_rate),
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      };
      setBotRateData(botRateChartData);
      
      // Fetch sentiment distribution data
      const sentimentResponse = await axios.get('/api/dashboard/sentiment', { params });
      const sentimentChartData = {
        labels: sentimentResponse.data.data.map(item => item.sentiment),
        datasets: [{
          label: 'Sentiment Distribution',
          data: sentimentResponse.data.data.map(item => item.count),
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)'
          ],
          borderWidth: 1
        }]
      };
      setSentimentData(sentimentChartData);
      
      // Fetch wordcloud data
      const wordcloudResponse = await axios.get('/api/dashboard/wordcloud', { params });
      setWordcloudData(wordcloudResponse.data.data);
      
      // Fetch review trend data
      const reviewTrendResponse = await axios.get('/api/dashboard/review_trend', { params });
      const reviewTrendChartData = {
        labels: reviewTrendResponse.data.data.map(item => item.date),
        datasets: [{
          label: 'Review Count',
          data: reviewTrendResponse.data.data.map(item => item.review_count),
          fill: false,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          tension: 0.1
        }]
      };
      setReviewTrendData(reviewTrendChartData);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Fetch data on component mount and when filters change
  useEffect(() => {
    fetchDashboardData();
  }, [startDate, endDate, realReviews, sentiment]);
  
  // Chart options
  const barOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Bot Rate by Date' }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Bot Rate (%)' }
      }
    }
  };
  
  const pieOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Sentiment Distribution' }
    }
  };
  
  const lineOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Review Count Trend' }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Review Count' }
      }
    }
  };
  
  // Wordcloud options
  const wordcloudOptions = {
    rotations: 2,
    rotationAngles: [0, 90],
    fontSizes: [10, 60],
    padding: 5
  };
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Merchant Review Dashboard</h1>
      
      {/* Filters */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <DatePicker
              selected={startDate}
              onChange={date => setStartDate(date)}
              selectsStart
              startDate={startDate}
              endDate={endDate}
              className="input"
              placeholderText="Select start date"
              isClearable
              maxDate={new Date('2022-10-31')}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <DatePicker
              selected={endDate}
              onChange={date => setEndDate(date)}
              selectsEnd
              startDate={startDate}
              endDate={endDate}
              minDate={startDate}
              className="input"
              placeholderText="Select end date"
              isClearable
              maxDate={new Date('2022-10-31')}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Real Reviews</label>
            <select
              value={realReviews}
              onChange={e => setRealReviews(e.target.value)}
              className="select"
            >
              <option value="">All Reviews</option>
              <option value="true">Real Reviews Only</option>
              <option value="false">Bot Reviews Only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sentiment</label>
            <select
              value={sentiment}
              onChange={e => setSentiment(e.target.value)}
              className="select"
            >
              <option value="">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>
        </div>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64 bg-gray-50 rounded-lg animate-pulse">
          <div className="text-xl text-gray-400">Loading...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Bot Rate Chart */}
          <div className="chart-container group transform transition-all duration-300 hover:scale-[1.01]">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Bot Review Trend
            </h2>
            <div className="h-80 transition-all duration-300 group-hover:opacity-95">
              {botRateData.labels.length > 0 ? (
                <Bar data={botRateData} options={barOptions} />
              ) : (
                <div className="flex justify-center items-center h-full text-gray-500">No Data Available</div>
              )}
            </div>
          </div>
          
          {/* Sentiment Distribution Chart */}
          <div className="chart-container group transform transition-all duration-300 hover:scale-[1.01]">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Sentiment Distribution
            </h2>
            <div className="h-80 transition-all duration-300 group-hover:opacity-95">
              {sentimentData.labels.length > 0 ? (
                <Pie data={sentimentData} options={pieOptions} />
              ) : (
                <div className="flex justify-center items-center h-full text-gray-500">No Data Available</div>
              )}
            </div>
          </div>
          
          {/* Word Cloud */}
          <div className="chart-container group transform transition-all duration-300 hover:scale-[1.01]">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              Common Keywords
            </h2>
            <div className="h-80 transition-all duration-300 group-hover:opacity-95">
              {wordcloudData.length > 0 ? (
                <ReactWordcloud words={wordcloudData} options={wordcloudOptions} />
              ) : (
                <div className="flex justify-center items-center h-full text-gray-500">No Data Available</div>
              )}
            </div>
          </div>
          
          {/* Review Count Trend */}
          <div className="chart-container group transform transition-all duration-300 hover:scale-[1.01]">
            <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
              Review Count Trend
            </h2>
            <div className="h-80 transition-all duration-300 group-hover:opacity-95">
              {reviewTrendData.labels.length > 0 ? (
                <Line data={reviewTrendData} options={lineOptions} />
              ) : (
                <div className="flex justify-center items-center h-full text-gray-500">No Data Available</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;