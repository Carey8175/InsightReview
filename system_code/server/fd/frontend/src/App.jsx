import React, { useState, useEffect } from 'react';
import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Search from './pages/Search';

function App() {
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  
  // 监听滚动事件，用于导航栏样式变化
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [scrolled]);
  
  // 页面切换时添加淡入动画
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);
  
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <nav className={`sticky top-0 z-10 transition-all duration-300 ${scrolled ? 'bg-white shadow-md' : 'bg-gradient-to-r from-indigo-600 to-indigo-800'}`}>
        <div className="container mx-auto px-6 py-3 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="relative h-10 w-10 flex items-center justify-center rounded-lg bg-white bg-opacity-20 backdrop-blur-sm shadow-inner overflow-hidden">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className={`text-xl font-extrabold tracking-tight ${scrolled ? 'text-indigo-700' : 'text-white'}`}>
              <span className="inline-block transform transition-transform hover:scale-105">Insight</span>
              <span className="inline-block ml-1 text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-indigo-400">Review</span>
            </div>
          </div>
          
          <div className="flex space-x-1 md:space-x-6">
            <NavLink 
              to="/" 
              className={({ isActive }) => 
                `px-3 py-2 rounded-lg transition-all duration-300 ${isActive 
                  ? (scrolled ? 'bg-indigo-100 text-indigo-700 font-bold' : 'bg-white bg-opacity-20 text-white font-bold') 
                  : (scrolled ? 'text-gray-700 hover:bg-gray-100' : 'text-white hover:bg-white hover:bg-opacity-10')}`
              }
              end
            >
              <div className="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>Dashboard</span>
              </div>
            </NavLink>
            <NavLink 
              to="/search" 
              className={({ isActive }) => 
                `px-3 py-2 rounded-lg transition-all duration-300 ${isActive 
                  ? (scrolled ? 'bg-indigo-100 text-indigo-700 font-bold' : 'bg-white bg-opacity-20 text-white font-bold') 
                  : (scrolled ? 'text-gray-700 hover:bg-gray-100' : 'text-white hover:bg-white hover:bg-opacity-10')}`
              }
            >
              <div className="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Search</span>
              </div>
            </NavLink>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-8 flex-grow fade-in">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/search" element={<Search />} />
        </Routes>
      </main>

      <footer className="bg-gradient-to-b from-gray-50 to-gray-100 py-8 mt-auto border-t border-gray-200">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center mb-4 md:mb-0">
              <div className="h-8 w-8 rounded-md bg-indigo-600 flex items-center justify-center mr-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <div className="font-bold text-indigo-700">Insight Review</div>
                <div className="text-xs text-gray-500">Data-driven merchant review analysis platform</div>
              </div>
            </div>
            
            <div className="flex space-x-4 mb-4 md:mb-0">
              <a href="#" className="text-gray-500 hover:text-indigo-600 transition-colors duration-200 transform hover:scale-110">
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.342-3.369-1.342-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.934.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.161 22 16.418 22 12c0-5.523-4.477-10-10-10z"></path>
                </svg>
              </a>
              <a href="#" className="text-gray-500 hover:text-indigo-600 transition-colors duration-200 transform hover:scale-110">
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M22.162 5.656a8.384 8.384 0 01-2.402.658A4.196 4.196 0 0021.6 4c-.82.488-1.719.83-2.656 1.015a4.182 4.182 0 00-7.126 3.814 11.874 11.874 0 01-8.62-4.37 4.168 4.168 0 00-.566 2.103c0 1.45.738 2.731 1.86 3.481a4.168 4.168 0 01-1.894-.523v.052a4.185 4.185 0 003.355 4.101 4.21 4.21 0 01-1.89.072A4.185 4.185 0 007.97 16.65a8.394 8.394 0 01-6.191 1.732 11.83 11.83 0 006.41 1.88c7.693 0 11.9-6.373 11.9-11.9 0-.18-.005-.362-.013-.54a8.496 8.496 0 002.087-2.165z"></path>
                </svg>
              </a>
              <a href="#" className="text-gray-500 hover:text-indigo-600 transition-colors duration-200 transform hover:scale-110">
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
                </svg>
              </a>
            </div>
            
            <div className="text-center md:text-right text-gray-600">
              <p>© {new Date().getFullYear()} Insight Review. All rights reserved.</p>
              <p className="text-xs mt-1">版本 1.0.0</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;