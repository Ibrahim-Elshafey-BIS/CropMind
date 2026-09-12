import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  FiHome,
  FiBarChart2,
  FiDollarSign,
  FiPackage,
  FiUsers,
  FiDroplet,
  FiTrendingUp,
  FiFileText,
  FiSettings,
  FiChevronLeft,
  FiChevronRight,
} from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const navLinks = [
    { path: '/', label: 'Dashboard', icon: FiHome },
    { path: '/crops', label: 'Crops', icon: FaSeedling },
    { path: '/finance', label: 'Finance', icon: FiDollarSign },
    { path: '/inventory', label: 'Inventory', icon: FiPackage },
    { path: '/workforce', label: 'Workforce', icon: FiUsers },
    { path: '/irrigation', label: 'Irrigation', icon: FiDroplet },
    { path: '/market', label: 'Market', icon: FiTrendingUp },
    { path: '/reports', label: 'Reports', icon: FiFileText },
    { path: '/settings', label: 'Settings', icon: FiSettings },
  ];

  return (
    <aside
      className={`bg-[#1a5c38] text-white transition-all duration-300 flex flex-col ${
        isCollapsed ? 'w-16' : 'w-64'
      } min-h-screen sticky top-0`}
    >
      {/* Logo / Brand */}
      <div className={`flex items-center gap-2 px-4 py-6 border-b border-[#2d7a4a] ${isCollapsed ? 'justify-center' : ''}`}>
        <FaSeedling className="text-[#a8d5a2] text-2xl flex-shrink-0" />
        {!isCollapsed && (
          <span className="text-lg font-bold truncate">CropMind</span>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navLinks.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-[#2d7a4a] text-white shadow-md'
                  : 'text-[#a8d5a2] hover:bg-[#2d7a4a] hover:text-white'
              } ${isCollapsed ? 'justify-center' : ''}`
            }
            title={isCollapsed ? label : ''}
          >
            <Icon className={`text-xl ${isCollapsed ? '' : 'flex-shrink-0'}`} />
            {!isCollapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Farm DNA Score */}
      {!isCollapsed && (
        <div className="px-4 py-4 border-t border-[#2d7a4a]">
          <div className="bg-[#2d7a4a] rounded-lg p-4">
            <div className="text-xs text-[#a8d5a2] uppercase tracking-wider">Farm DNA Score</div>
            <div className="text-2xl font-bold mt-1">84</div>
            <div className="w-full bg-[#1a5c38] rounded-full h-2 mt-2">
              <div className="bg-[#a8d5a2] h-2 rounded-full" style={{ width: '84%' }} />
            </div>
            <div className="text-xs text-[#a8d5a2] mt-1">Overall Health</div>
          </div>
        </div>
      )}

      {/* Collapse Toggle Button */}
      <button
        onClick={toggleCollapse}
        className="absolute -right-3 top-20 bg-[#2d7a4a] rounded-full p-1.5 shadow-lg hover:bg-[#3d8a5a] transition-colors border border-[#1a5c38]"
        aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {isCollapsed ? <FiChevronRight size={16} /> : <FiChevronLeft size={16} />}
      </button>

      {/* Mobile overlay for small screens - collapsed state indicator */}
      {isCollapsed && (
        <div className="hidden md:block absolute -right-3 top-1/2 transform -translate-y-1/2">
          <div className="bg-[#2d7a4a] rounded-l-lg px-1 py-2 text-xs text-[#a8d5a2]">
            ▶
          </div>
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
