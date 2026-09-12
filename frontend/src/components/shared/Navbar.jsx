import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiLogOut, FiUser, FiMenu, FiX } from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';
import { IoNotificationsOutline } from 'react-icons/io5';
import useAuthStore from '../../store/authStore';
import useFarmStore from '../../store/farmStore';
import AlertBadge from './AlertBadge';

const Navbar = () => {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const { currentFarm } = useFarmStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <nav className="bg-[#1a5c38] text-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-xl font-bold">
            <FaSeedling className="text-[#a8d5a2]" />
            <span>CropMind</span>
            <span className="text-xs bg-[#2d7a4a] px-2 py-0.5 rounded-full">
              AI
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {/* Farm Name */}
            {currentFarm && (
              <span className="text-sm text-[#a8d5a2] border-r border-[#2d7a4a] pr-4">
                🌾 {currentFarm.name}
              </span>
            )}

            {/* Alerts */}
            <AlertBadge />

            {/* User Info */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-[#2d7a4a] flex items-center justify-center">
                  <FiUser className="text-white" />
                </div>
                <span className="text-sm font-medium">
                  {user?.full_name || user?.email || 'User'}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-[#2d7a4a] hover:bg-[#3d8a5a] rounded-lg transition-colors"
              >
                <FiLogOut className="text-[#a8d5a2]" />
                Logout
              </button>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-3 md:hidden">
            <AlertBadge />
            <button
              onClick={toggleMobileMenu}
              className="p-2 rounded-lg hover:bg-[#2d7a4a] transition-colors"
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-[#2d7a4a] space-y-3">
            {currentFarm && (
              <div className="text-sm text-[#a8d5a2]">
                🌾 {currentFarm.name}
              </div>
            )}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#2d7a4a] flex items-center justify-center">
                <FiUser className="text-white" />
              </div>
              <span className="text-sm font-medium">
                {user?.full_name || user?.email || 'User'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 w-full px-4 py-2 text-sm bg-[#2d7a4a] hover:bg-[#3d8a5a] rounded-lg transition-colors"
            >
              <FiLogOut className="text-[#a8d5a2]" />
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
