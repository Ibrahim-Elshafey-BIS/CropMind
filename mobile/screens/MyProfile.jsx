/**
 * CropMind - My Profile Screen
 * Worker profile display and edit screen
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  ScrollView,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { getCurrentUser, getWorkerProfile, updateWorkerProfile, logout } from '../services/api';

const MyProfile = ({ navigation }) => {
  const [worker, setWorker] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Edit form state
  const [formData, setFormData] = useState({
    phone: '',
    notes: '',
  });

  // Load worker data
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    setError(null);

    try {
      const user = await getCurrentUser();
      if (!user?.id) {
        setError('لم يتم العثور على بيانات العامل');
        setLoading(false);
        return;
      }

      const result = await getWorkerProfile(user.id);

      if (result.success) {
        setWorker(result.data);
        setFormData({
          phone: result.data.phone || '',
          notes: result.data.notes || '',
        });
      } else {
        setError(result.error || 'فشل تحميل بيانات البروفايل');
      }
    } catch (error) {
      console.error('[MyProfile] Load error:', error);
      setError('حدث خطأ أثناء تحميل البيانات');
    } finally {
      setLoading(false);
    }
  };

  // Handle edit toggle
  const toggleEdit = () => {
    if (editMode) {
      // Cancel edit - reset form
      setFormData({
        phone: worker?.phone || '',
        notes: worker?.notes || '',
      });
    }
    setEditMode(!editMode);
  };

  // Handle save
  const handleSave = async () => {
    if (!worker) return;

    setSaving(true);
    try {
      const result = await updateWorkerProfile(worker.id, {
        phone: formData.phone,
        notes: formData.notes,
      });

      if (result.success) {
        setWorker(result.data);
        setEditMode(false);
        Alert.alert('✅ تم التحديث', 'تم تحديث البروفايل بنجاح');
      } else {
        Alert.alert('فشل التحديث', result.error || 'حدث خطأ أثناء التحديث');
      }
    } catch (error) {
      console.error('[MyProfile] Save error:', error);
      Alert.alert('خطأ', 'فشل تحديث البروفايل');
    } finally {
      setSaving(false);
    }
  };

  // Handle logout
  const handleLogout = () => {
    Alert.alert(
      'تسجيل الخروج',
      'هل أنت متأكد من رغبتك في تسجيل الخروج؟',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'تسجيل الخروج',
          style: 'destructive',
          onPress: async () => {
            await logout();
            navigation.replace('Login');
          },
        },
      ]
    );
  };

  // Get role in Arabic
  const getRoleLabel = (role) => {
    const roleMap = {
      laborer: 'عامل',
      supervisor: 'مشرف',
      irrigation_specialist: 'أخصائي ري',
    };
    return roleMap[role] || role || 'غير محدد';
  };

  // Get initials for avatar
  const getInitials = (name) => {
    if (!name) return '?';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  // Loading state
  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2d6a4f" />
          <Text style={styles.loadingText}>جاري تحميل البروفايل...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Error state
  if (error) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={64} color="#dc2626" />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadProfile}>
            <Text style={styles.retryButtonText}>إعادة المحاولة</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2d6a4f" />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <Ionicons name="arrow-back" size={24} color="#ffffff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>البروفايل الشخصي</Text>
        <TouchableOpacity
          onPress={toggleEdit}
          style={styles.editButton}
        >
          <Text style={styles.editButtonText}>
            {editMode ? 'إلغاء' : 'تعديل'}
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Avatar Section */}
        <View style={styles.avatarSection}>
          <View style={styles.avatarContainer}>
            <Text style={styles.avatarText}>
              {getInitials(worker?.full_name)}
            </Text>
          </View>
          <Text style={styles.nameText}>{worker?.full_name || 'غير معروف'}</Text>
          <Text style={styles.roleText}>{getRoleLabel(worker?.role)}</Text>
        </View>

        {/* Stats Section */}
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>12</Text>
            <Text style={styles.statLabel}>مهام مكتملة</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>45</Text>
            <Text style={styles.statLabel}>أيام عمل</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>
              {worker?.is_active ? 'نشط' : 'غير نشط'}
            </Text>
            <Text style={styles.statLabel}>الحالة</Text>
          </View>
        </View>

        {/* Info Section */}
        <View style={styles.infoSection}>
          {/* Phone */}
          <View style={styles.infoRow}>
            <View style={styles.infoIconContainer}>
              <Ionicons name="call-outline" size={20} color="#2d6a4f" />
            </View>
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>رقم الهاتف</Text>
              {editMode ? (
                <TextInput
                  style={styles.infoInput}
                  value={formData.phone}
                  onChangeText={(text) => setFormData({ ...formData, phone: text })}
                  placeholder="أدخل رقم الهاتف"
                  placeholderTextColor="#9ca3af"
                  keyboardType="phone-pad"
                />
              ) : (
                <Text style={styles.infoValue}>{worker?.phone || 'غير محدد'}</Text>
              )}
            </View>
          </View>

          {/* Daily Wage */}
          <View style={styles.infoRow}>
            <View style={styles.infoIconContainer}>
              <Ionicons name="cash-outline" size="20" color="#2d6a4f" />
            </View>
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>الأجر اليومي</Text>
              <Text style={styles.infoValue}>
                {worker?.daily_wage ? `${worker.daily_wage} جنيه` : 'غير محدد'}
              </Text>
            </View>
          </View>

          {/* Hire Date */}
          <View style={styles.infoRow}>
            <View style={styles.infoIconContainer}>
              <Ionicons name="calendar-outline" size="20" color="#2d6a4f" />
            </View>
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>تاريخ التعيين</Text>
              <Text style={styles.infoValue}>
                {worker?.hire_date
                  ? new Date(worker.hire_date).toLocaleDateString('ar-EG')
                  : 'غير محدد'}
              </Text>
            </View>
          </View>

          {/* Notes */}
          <View style={styles.infoRow}>
            <View style={styles.infoIconContainer}>
              <Ionicons name="document-text-outline" size="20" color="#2d6a4f" />
            </View>
            <View style={styles.infoContent}>
              <Text style={styles.infoLabel}>ملاحظات</Text>
              {editMode ? (
                <TextInput
                  style={[styles.infoInput, styles.notesInput]}
                  value={formData.notes}
                  onChangeText={(text) => setFormData({ ...formData, notes: text })}
                  placeholder="أضف ملاحظات..."
                  placeholderTextColor="#9ca3af"
                  multiline
                  numberOfLines={3}
                  textAlignVertical="top"
                />
              ) : (
                <Text style={styles.infoValue}>
                  {worker?.notes || 'لا توجد ملاحظات'}
                </Text>
              )}
            </View>
          </View>
        </View>

        {/* Save Button (Edit Mode) */}
        {editMode && (
          <TouchableOpacity
            style={[styles.saveButton, saving && styles.saveButtonDisabled]}
            onPress={handleSave}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator size="small" color="#ffffff" />
            ) : (
              <>
                <Ionicons name="save-outline" size={20} color="#ffffff" />
                <Text style={styles.saveButtonText}>حفظ التعديلات</Text>
              </>
            )}
          </TouchableOpacity>
        )}

        {/* Logout Button */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
        >
          <Ionicons name="log-out-outline" size={20} color="#dc2626" />
          <Text style={styles.logoutButtonText}>تسجيل الخروج</Text>
        </TouchableOpacity>

        {/* App Version */}
        <Text style={styles.versionText}>
          CropMind v1.0.0 • MTC Cairo 2026
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
};

// ============================================
// Styles
// ============================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  header: {
    backgroundColor: '#2d6a4f',
    paddingHorizontal: 16,
    paddingVertical: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  backButton: {
    padding: 4,
  },
  editButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  editButtonText: {
    color: '#a8d5ba',
    fontSize: 14,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 12,
  },
  errorContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 40,
  },
  errorText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 12,
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#2d6a4f',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  avatarSection: {
    alignItems: 'center',
    paddingTop: 24,
    paddingBottom: 16,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#2d6a4f',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
    borderWidth: 4,
    borderColor: '#ffffff',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  avatarText: {
    fontSize: 40,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  nameText: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  roleText: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    marginHorizontal: 16,
    marginVertical: 12,
    borderRadius: 12,
    paddingVertical: 16,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  statLabel: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 2,
  },
  statDivider: {
    width: 1,
    backgroundColor: '#e5e7eb',
  },
  infoSection: {
    backgroundColor: '#ffffff',
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 8,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  infoRow: {
    flexDirection: 'row',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  infoRowLast: {
    borderBottomWidth: 0,
  },
  infoIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#f0fdf4',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 12,
    color: '#9ca3af',
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 15,
    color: '#1f2937',
    marginTop: 2,
  },
  infoInput: {
    fontSize: 15,
    color: '#1f2937',
    padding: 0,
    marginTop: 2,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
    minHeight: 30,
  },
  notesInput: {
    minHeight: 60,
    textAlignVertical: 'top',
  },
  saveButton: {
    backgroundColor: '#2d6a4f',
    marginHorizontal: 16,
    marginTop: 16,
    marginBottom: 8,
    paddingVertical: 14,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  saveButtonDisabled: {
    opacity: 0.7,
  },
  saveButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 16,
    marginTop: 8,
    marginBottom: 16,
    paddingVertical: 14,
    borderRadius: 12,
    backgroundColor: '#fef2f2',
    borderWidth: 1,
    borderColor: '#fca5a5',
    gap: 8,
  },
  logoutButtonText: {
    color: '#dc2626',
    fontSize: 16,
    fontWeight: '600',
  },
  versionText: {
    textAlign: 'center',
    fontSize: 12,
    color: '#9ca3af',
    marginBottom: 20,
  },
});

export default MyProfile;
