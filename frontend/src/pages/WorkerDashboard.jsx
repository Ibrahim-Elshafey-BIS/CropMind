/**
 * CropMind - Worker Dashboard
 * Mobile-first dashboard for farm workers (Arabic interface)
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { 
  FiLogOut, 
  FiUser, 
  FiCalendar, 
  FiCheckCircle, 
  FiCamera, 
  FiAlertTriangle,
  FiLoader,
  FiSend,
  FiX,
  FiImage
} from 'react-icons/fi';
import { FaSeedling } from 'react-icons/fa';

import useAuthStore from '../store/authStore';
import useFarmStore from '../store/farmStore';
import api, { workforce, agents, alerts } from '../services/api';

const WorkerDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { currentFarm } = useFarmStore();
  
  const [tasks, setTasks] = useState([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isSubmittingReport, setIsSubmittingReport] = useState(false);
  
  // Report form
  const [reportType, setReportType] = useState('crop_health');
  const [reportDescription, setReportDescription] = useState('');
  
  const fileInputRef = useRef(null);

  const farmId = currentFarm?.id;

  // Get today's date in Arabic
  const getTodayDate = () => {
    const now = new Date();
    return now.toLocaleDateString('ar-EG', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Fetch tasks
  useEffect(() => {
    const fetchTasks = async () => {
      if (!farmId) {
        setIsLoadingTasks(false);
        return;
      }

      setIsLoadingTasks(true);
      try {
        const data = await workforce.getActiveWorkers(farmId);
        setTasks(data || []);
      } catch (err) {
        console.error('Error fetching tasks:', err);
        setTasks([]);
      } finally {
        setIsLoadingTasks(false);
      }
    };

    fetchTasks();
  }, [farmId]);

  // Handle logout
  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Handle image selection
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setAnalysisResult(null);
      analyzeImage(file);
    }
  };

  // Analyze image using CV service
  const analyzeImage = async (file) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/cv/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;
      
      setAnalysisResult({
        disease: data.disease || 'غير معروف',
        confidence: data.confidence || 0,
        health_score: data.health_score || 0,
        recommendation: data.recommendation || 'يرجى استشارة خبير زراعي',
      });
      
      toast.success('تم تحليل المحصول بنجاح');
    } catch (err) {
      console.error('Analysis error:', err);
      toast.error(err.response?.data?.detail || 'فشل تحليل الصورة');
      setAnalysisResult(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle report submission
  const handleSubmitReport = async (e) => {
    e.preventDefault();
    
    if (!farmId) {
      toast.error('يرجى تحديد المزرعة أولاً');
      return;
    }

    if (!reportDescription.trim()) {
      toast.error('يرجى كتابة وصف المشكلة');
      return;
    }

    setIsSubmittingReport(true);

    try {
      await alerts.getFarmAlerts(farmId); // Just to verify
      // Send report via alerts endpoint
      const response = await api.post(`/alerts/farms/${farmId}`, {
        type: reportType,
        severity: 'high',
        message: reportDescription,
        data: {}
      });

      if (response.status === 200 || response.status === 201) {
        toast.success('تم إرسال التقرير بنجاح');
        setReportDescription('');
        setReportType('crop_health');
      } else {
        throw new Error('Failed to submit report');
      }
    } catch (err) {
      console.error('Error submitting report:', err);
      toast.error('فشل إرسال التقرير');
    } finally {
      setIsSubmittingReport(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-[#1a5c38] text-white p-4 sticky top-0 z-10 shadow-md">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <FiUser className="text-xl" />
            </div>
            <div>
              <h1 className="font-bold text-lg">{user?.full_name || 'فلاح'}</h1>
              <p className="text-xs text-[#a8d5a2]">عامل مزرعة</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              title="تسجيل الخروج"
            >
              <FiLogOut className="text-xl" />
            </button>
          </div>
        </div>
        <div className="max-w-lg mx-auto mt-2 flex items-center gap-2 text-sm text-[#a8d5a2]">
          <FiCalendar />
          <span>{getTodayDate()}</span>
        </div>
      </header>

      <main className="max-w-lg mx-auto p-4 space-y-6">
        {/* Today's Tasks */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h2 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
            <FiCheckCircle className="text-[#1a5c38]" />
            مهام اليوم
          </h2>
          
          {isLoadingTasks ? (
            <div className="flex justify-center py-8">
              <FiLoader className="animate-spin text-2xl text-[#1a5c38]" />
            </div>
          ) : tasks.length === 0 ? (
            <p className="text-gray-500 text-center py-6">لا توجد مهام اليوم</p>
          ) : (
            <div className="space-y-3">
              {tasks.map((worker) => (
                <div key={worker.worker_id || worker.id} className="border border-gray-100 rounded-lg p-3 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-800">{worker.name}</p>
                      <p className="text-sm text-gray-500">{worker.role}</p>
                    </div>
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">نشط</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Plant Scanner */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h2 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
            <FiCamera className="text-[#1a5c38]" />
            مسح المحصول
          </h2>
          
          <div className="space-y-4">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isAnalyzing}
              className="w-full py-3 px-4 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <FiCamera />
              {isAnalyzing ? 'جاري التحليل...' : 'افتح الكاميرا'}
            </button>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={handleImageSelect}
            />

            {selectedImage && (
              <div className="relative">
                <img
                  src={URL.createObjectURL(selectedImage)}
                  alt="المحصول"
                  className="w-full h-48 object-cover rounded-lg border border-gray-200"
                />
                <button
                  onClick={() => {
                    setSelectedImage(null);
                    setAnalysisResult(null);
                  }}
                  className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600 transition-colors"
                >
                  <FiX className="text-sm" />
                </button>
              </div>
            )}

            {isAnalyzing && (
              <div className="flex justify-center py-4">
                <FiLoader className="animate-spin text-3xl text-[#1a5c38]" />
              </div>
            )}

            {analysisResult && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">المرض المكتشف:</span>
                  <span className="font-bold text-[#1a5c38]">{analysisResult.disease}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">نسبة الثقة:</span>
                  <span className="font-bold text-[#1a5c38]">{(analysisResult.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">درجة الصحة:</span>
                  <span className="font-bold text-[#1a5c38]">{analysisResult.health_score}%</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">التوصية:</span>
                  <p className="text-sm text-gray-600 mt-1">{analysisResult.recommendation}</p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Report Issue */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <h2 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
            <FiAlertTriangle className="text-[#1a5c38]" />
            تقرير مشكلة
          </h2>
          
          <form onSubmit={handleSubmitReport} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                نوع المشكلة
              </label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent"
                disabled={isSubmittingReport}
              >
                <option value="crop_health">صحة المحصول</option>
                <option value="irrigation">مشكلة ري</option>
                <option value="equipment">عطل في المعدات</option>
                <option value="labor">مشكلة عمال</option>
                <option value="other">أخرى</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                وصف المشكلة
              </label>
              <textarea
                value={reportDescription}
                onChange={(e) => setReportDescription(e.target.value)}
                placeholder="اكتب وصف المشكلة هنا..."
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1a5c38] focus:border-transparent resize-none"
                disabled={isSubmittingReport}
              />
            </div>

            <button
              type="submit"
              disabled={isSubmittingReport || !reportDescription.trim()}
              className="w-full py-3 px-4 bg-[#1a5c38] text-white rounded-lg hover:bg-[#2d7a4a] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isSubmittingReport ? (
                <FiLoader className="animate-spin" />
              ) : (
                <FiSend />
              )}
              {isSubmittingReport ? 'جاري الإرسال...' : 'إرسال التقرير'}
            </button>
          </form>
        </section>

        {/* Footer */}
        <div className="text-center text-xs text-gray-400 py-4">
          CropMind v1.0.0 · الكلية الفنية العسكرية 2026
        </div>
      </main>
    </div>
  );
};

export default WorkerDashboard;