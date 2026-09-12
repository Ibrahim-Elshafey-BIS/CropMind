/**
 * CropMind - Today Tasks Screen
 * Worker's main screen showing today's tasks
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  ScrollView,
  SafeAreaView,
  StatusBar,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import TaskCard from '../components/TaskCard';
import AlertNotification from '../components/AlertNotification';
import { getTodayTasks, getAlerts, getCurrentUser } from '../services/api';

const TodayTasks = ({ navigation }) => {
  const [tasks, setTasks] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [worker, setWorker] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get current user from storage
      const user = await getCurrentUser();
      if (user) {
        setWorker(user);
      }

      // Get farm ID from user or storage
      const farmId = user?.farm_id || await AsyncStorage.getItem('farmId');
      const workerId = user?.id;

      if (!farmId) {
        setError('No farm assigned to this worker');
        setLoading(false);
        return;
      }

      // Fetch tasks and alerts in parallel
      const [tasksResult, alertsResult] = await Promise.all([
        getTodayTasks(farmId, workerId),
        getAlerts(farmId),
      ]);

      if (tasksResult.success) {
        setTasks(tasksResult.data || []);
      } else {
        setError(tasksResult.error || 'Failed to load tasks');
      }

      if (alertsResult.success) {
        // Show only unread or recent alerts (last 24 hours)
        const now = new Date();
        const recentAlerts = (alertsResult.data?.alerts || []).filter(
          (alert) => {
            const alertTime = new Date(alert.timestamp);
            const diffHours = (now - alertTime) / (1000 * 60 * 60);
            return diffHours < 24;
          }
        );
        setAlerts(recentAlerts);
      }

      setLoading(false);
    } catch (error) {
      console.error('[TodayTasks] Load error:', error);
      setError('Failed to load data');
      setLoading(false);
    }
  };

  // Handle refresh (pull to refresh)
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }, []);

  // Handle task completion
  const handleTaskComplete = (taskId) => {
    // Update task status locally
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.task_id === taskId || task.id === taskId
          ? { ...task, status: 'completed' }
          : task
      )
    );

    // Show success message
    Alert.alert(
      '✅ مهمة مكتملة',
      'تم إتمام المهمة بنجاح!',
      [{ text: 'حسناً' }]
    );
  };

  // Handle task press
  const handleTaskPress = (task) => {
    // Navigate to task detail if needed
    // navigation.navigate('TaskDetail', { task });
  };

  // Handle alert press
  const handleAlertPress = (alert) => {
    // Navigate to relevant section
    if (alert.type === 'low_stock') {
      // navigation.navigate('Inventory');
    } else if (alert.type === 'sensor_anomaly') {
      // navigation.navigate('Irrigation');
    } else if (alert.type === 'crop_health') {
      // navigation.navigate('Crops');
    }
  };

  // Handle alert dismiss
  const handleAlertDismiss = (alert) => {
    setAlerts((prev) => prev.filter((a) => a !== alert));
  };

  // Calculate task stats
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.status === 'completed').length;
  const completionRate = totalTasks > 0
    ? Math.round((completedTasks / totalTasks) * 100)
    : 0;

  // Get today's date in Arabic format
  const getTodayDate = () => {
    const now = new Date();
    return now.toLocaleDateString('ar-EG', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Render task item
  const renderTaskItem = ({ item }) => (
    <TaskCard
      task={item}
      onComplete={handleTaskComplete}
      onPress={() => handleTaskPress(item)}
    />
  );

  // Render alert item
  const renderAlertItem = ({ item }) => (
    <AlertNotification
      alert={item}
      onDismiss={handleAlertDismiss}
      onPress={() => handleAlertPress(item)}
    />
  );

  // Loading state
  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2d6a4f" />
          <Text style={styles.loadingText}>جاري تحميل المهام...</Text>
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
          <TouchableOpacity style={styles.retryButton} onPress={loadData}>
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
        <View>
          <Text style={styles.headerTitle}>مهام اليوم</Text>
          <Text style={styles.headerSubtitle}>
            {worker?.full_name || 'العامل'}
          </Text>
          <Text style={styles.headerDate}>{getTodayDate()}</Text>
        </View>
        <View style={styles.headerStats}>
          <Text style={styles.statsText}>
            {completedTasks}/{totalTasks}
          </Text>
          <Text style={styles.statsLabel}>مكتملة</Text>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        <View style={styles.progressBackground}>
          <View
            style={[
              styles.progressFill,
              { width: `${completionRate}%` },
            ]}
          />
        </View>
        <Text style={styles.progressText}>
          {completionRate}% مكتمل
        </Text>
      </View>

      <FlatList
        data={tasks}
        renderItem={renderTaskItem}
        keyExtractor={(item) => String(item.task_id || item.id)}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#2d6a4f']}
            tintColor="#2d6a4f"
          />
        }
        ListHeaderComponent={
          alerts.length > 0 ? (
            <View style={styles.alertsSection}>
              <View style={styles.alertsHeader}>
                <Ionicons name="notifications" size={20} color="#d97706" />
                <Text style={styles.alertsTitle}>تنبيهات ({alerts.length})</Text>
              </View>
              <FlatList
                data={alerts}
                renderItem={renderAlertItem}
                keyExtractor={(item, index) => String(item.alert_id || index)}
                scrollEnabled={false}
              />
            </View>
          ) : null
        }
        ListEmptyComponent={
          !loading && (
            <View style={styles.emptyContainer}>
              <Ionicons name="checkmark-circle-outline" size={64} color="#9ca3af" />
              <Text style={styles.emptyTitle}>لا توجد مهام اليوم</Text>
              <Text style={styles.emptySubtitle}>
                تم إنجاز جميع المهام! 🎉
              </Text>
            </View>
          )
        }
        contentContainerStyle={[
          styles.listContent,
          tasks.length === 0 && styles.emptyListContent,
        ]}
        showsVerticalScrollIndicator={false}
      />
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
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#a8d5ba',
    marginTop: 2,
  },
  headerDate: {
    fontSize: 12,
    color: '#a8d5ba',
    marginTop: 4,
  },
  headerStats: {
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 12,
  },
  statsText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  statsLabel: {
    fontSize: 11,
    color: '#a8d5ba',
  },
  progressContainer: {
    backgroundColor: '#ffffff',
    paddingHorizontal: 20,
    paddingVertical: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  progressBackground: {
    flex: 1,
    height: 6,
    backgroundColor: '#e5e7eb',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2d6a4f',
    borderRadius: 3,
  },
  progressText: {
    fontSize: 12,
    color: '#6b7280',
    fontWeight: '500',
    minWidth: 50,
  },
  alertsSection: {
    paddingTop: 8,
  },
  alertsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 8,
  },
  alertsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#d97706',
  },
  listContent: {
    paddingBottom: 20,
  },
  emptyListContent: {
    flex: 1,
    justifyContent: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#4b5563',
    marginTop: 12,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#9ca3af',
    marginTop: 4,
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
});

export default TodayTasks;
