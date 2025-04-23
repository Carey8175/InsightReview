import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Bar, Pie, Line, Radar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement, RadialLinearScale } from 'chart.js';

// 注册ChartJS组件
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend, 
  ArcElement, 
  PointElement, 
  LineElement,
  RadialLinearScale
);

const SearchDashboard = () => {
  // 日期范围过滤器状态
  const [startDate, setStartDate] = useState(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)); // 默认30天前
  const [endDate, setEndDate] = useState(new Date());
  
  // 图表数据状态
  const [queryDistributionData, setQueryDistributionData] = useState({ labels: [], datasets: [] });
  const [responseTimeData, setResponseTimeData] = useState({ labels: [], datasets: [] });
  const [subQueryEfficiencyData, setSubQueryEfficiencyData] = useState({ labels: [], datasets: [] });
  const [searchRelevanceData, setSearchRelevanceData] = useState({ labels: [], datasets: [] });
  
  // 加载状态
  const [loading, setLoading] = useState(true);
  
  // 格式化日期用于API请求
  const formatDate = (date) => {
    if (!date) return null;
    return date.toISOString().split('T')[0]; // 格式化为YYYY-MM-DD
  };
  
  // 构建查询参数
  const buildQueryParams = () => {
    const params = {};
    
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    return params;
  };
  
  // 从后端API获取搜索仪表盘数据
  const fetchSearchDashboardData = async () => {
    setLoading(true);
    const params = buildQueryParams();
    
    try {
      // 获取查询分布数据
      const queryDistributionResponse = await axios.get('/api/search_dashboard/query_distribution', { params });
      const queryDistData = queryDistributionResponse.data.data;
      const queryDistribution = {
        labels: queryDistData.map(item => item.type),
        datasets: [{
          label: '查询分布',
          data: queryDistData.map(item => item.percentage),
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
      setQueryDistributionData(queryDistribution);
      
      // 获取响应时间数据
      const responseTimeResponse = await axios.get('/api/search_dashboard/response_time', { params });
      const responseTimeData = responseTimeResponse.data.data;
      const responseTime = {
        labels: responseTimeData.map(item => item.type),
        datasets: [{
          label: '平均响应时间 (ms)',
          data: responseTimeData.map(item => item.time),
          backgroundColor: [
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 99, 132, 0.6)'
          ],
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 99, 132, 1)'
          ],
          borderWidth: 1
        }]
      };
      setResponseTimeData(responseTime);
      
      // 获取子查询生成效率数据
      const subQueryEfficiencyResponse = await axios.get('/api/search_dashboard/sub_query_efficiency', { params });
      const subQueryData = subQueryEfficiencyResponse.data.data;
      const subQueryEfficiency = {
        labels: subQueryData.map(item => item.month),
        datasets: [{
          label: '平均子查询数',
          data: subQueryData.map(item => item.avg_count),
          fill: false,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          tension: 0.1
        }, {
          label: '子查询生成时间 (ms)',
          data: subQueryData.map(item => item.avg_time),
          fill: false,
          backgroundColor: 'rgba(255, 159, 64, 0.6)',
          borderColor: 'rgba(255, 159, 64, 1)',
          tension: 0.1
        }]
      };
      setSubQueryEfficiencyData(subQueryEfficiency);
      
      // 获取搜索结果相关性数据
      const searchQualityResponse = await axios.get('/api/search_dashboard/search_quality', { params });
      const searchQualityData = searchQualityResponse.data.data;
      const searchRelevance = {
        labels: searchQualityData.map(item => item.aspect),
        datasets: [{
          label: '搜索质量评分',
          data: searchQualityData.map(item => item.score),
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          pointBackgroundColor: 'rgba(54, 162, 235, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
        }]
      };
      setSearchRelevanceData(searchRelevance);
      
    } catch (error) {
      console.error('获取搜索仪表盘数据时出错:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 在组件挂载和过滤器变化时获取数据
  useEffect(() => {
    fetchSearchDashboardData();
  }, [startDate, endDate]);
  
  // 图表选项
  const pieOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '搜索查询分布' }
    }
  };
  
  const barOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '搜索响应时间对比' }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: '响应时间 (ms)' }
      }
    }
  };
  
  const lineOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '子查询生成效率趋势' }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: '数值' }
      }
    }
  };
  
  const radarOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '搜索结果质量评估' }
    },
    scales: {
      r: {
        min: 0,
        max: 5,
        ticks: {
          stepSize: 1
        }
      }
    }
  };
  
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold text-gray-800">搜索功能仪表盘</h1>
      
      {/* 过滤器 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">日期过滤器</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
            <DatePicker
              selected={startDate}
              onChange={date => setStartDate(date)}
              selectsStart
              startDate={startDate}
              endDate={endDate}
              className="w-full p-2 border border-gray-300 rounded-md"
              placeholderText="选择开始日期"
              isClearable
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">结束日期</label>
            <DatePicker
              selected={endDate}
              onChange={date => setEndDate(date)}
              selectsEnd
              startDate={startDate}
              endDate={endDate}
              minDate={startDate}
              className="w-full p-2 border border-gray-300 rounded-md"
              placeholderText="选择结束日期"
              isClearable
            />
          </div>
        </div>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-xl text-gray-600">加载中...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 查询分布图表 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">搜索查询分布</h2>
            <div className="h-80">
              <Pie data={queryDistributionData} options={pieOptions} />
            </div>
          </div>
          
          {/* 响应时间图表 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">搜索响应时间</h2>
            <div className="h-80">
              <Bar data={responseTimeData} options={barOptions} />
            </div>
          </div>
          
          {/* 子查询生成效率图表 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">子查询生成效率</h2>
            <div className="h-80">
              <Line data={subQueryEfficiencyData} options={lineOptions} />
            </div>
          </div>
          
          {/* 搜索结果相关性图表 */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">搜索结果质量评估</h2>
            <div className="h-80">
              <Radar data={searchRelevanceData} options={radarOptions} />
            </div>
          </div>
        </div>
      )}
      
      {/* 搜索性能摘要 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">搜索性能摘要</h2>
        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="text-xl text-gray-600">加载中...</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-blue-700">平均响应时间</h3>
              <p className="text-3xl font-bold text-blue-900">
                {responseTimeData.datasets && responseTimeData.datasets[0] && 
                 responseTimeData.datasets[0].data ? 
                 Math.round((responseTimeData.datasets[0].data.reduce((a, b) => a + b, 0) / responseTimeData.datasets[0].data.length)) : 0}ms
              </p>
              <p className="text-sm text-blue-600">实时监测数据</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-green-700">平均子查询数</h3>
              <p className="text-3xl font-bold text-green-900">
                {subQueryEfficiencyData.datasets && subQueryEfficiencyData.datasets[0] && 
                 subQueryEfficiencyData.datasets[0].data && subQueryEfficiencyData.datasets[0].data.length > 0 ? 
                 subQueryEfficiencyData.datasets[0].data[subQueryEfficiencyData.datasets[0].data.length - 1].toFixed(1) : 0}
              </p>
              <p className="text-sm text-green-600">最新统计数据</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-purple-700">搜索成功率</h3>
              <p className="text-3xl font-bold text-purple-900">98.5%</p>
              <p className="text-sm text-purple-600">系统稳定性指标</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-yellow-700">用户满意度</h3>
              <p className="text-3xl font-bold text-yellow-900">
                {searchRelevanceData.datasets && searchRelevanceData.datasets[0] && 
                 searchRelevanceData.datasets[0].data ? 
                 (searchRelevanceData.datasets[0].data.reduce((a, b) => a + b, 0) / searchRelevanceData.datasets[0].data.length).toFixed(1) : 0}/5
              </p>
              <p className="text-sm text-yellow-600">基于搜索质量评分</p>
            </div>
          </div>
        )}
      </div>
      
      {/* 系统说明 */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">系统说明</h2>
        <div className="prose max-w-none">
          <p>本仪表盘展示了InsightReview系统搜索功能的关键性能指标。系统使用了先进的RAG（检索增强生成）技术，包括：</p>
          <ul>
            <li><strong>普通搜索</strong>：直接使用用户查询在知识库中检索相关文档</li>
            <li><strong>深度搜索</strong>：使用AI模型生成多个子查询，然后聚合搜索结果，提高搜索覆盖面和相关性</li>
          </ul>
          <p>数据更新频率：每日</p>
        </div>
      </div>
    </div>
  );
};

export default SearchDashboard;