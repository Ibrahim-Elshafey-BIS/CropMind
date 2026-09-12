/**
 * CropMind - Task Card Component
 * Displays a single task for the worker mobile app
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TouchableNativeFeedback,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const TaskCard = ({ task, onComplete, onPress }) => {
  const {
    task_id,
    task_name,
    priority = 'medium',
    status = 'pending',
    due_date,
    assigned_to,
    estimated_hours = 0,
  } = task;

  // Priority color mapping
  const priorityColors = {
    high: {
      bg: '#fee2e2',
      text: '#dc2626',
      border: '#fca5a5',
    },
    medium: {
      bg: '#fef3c7',
      text: '#d97706',
      border: '#fcd34d',
    },
    low: {
      bg: '#d1fae5',
      text: '#059669',
      border: '#6ee7b7',
    },
  };

  // Priority label mapping
  const priorityLabels = {
    high: 'عالية',
    medium: 'متوسطة',
    low: 'منخفضة',
  };

  // Status label mapping
  const statusLabels = {
    completed: 'مكتملة',
    in_progress: 'جارية',
    pending: 'معلقة',
  };

  // Status icon mapping
  const statusIcons = {
    completed: 'checkmark-circle',
    in_progress: 'time',
    pending: 'ellipse-outline',
  };

  // Priority icon mapping
  const priorityIcons = {
    high: 'alert',
    medium: 'warning',
    low: 'information-circle',
  };

  const isCompleted = status === 'completed';
  const priorityStyle = priorityColors[priority] || priorityColors.medium;

  const handleComplete = () => {
    if (!isCompleted && onComplete) {
      onComplete(task_id);
    }
  };

  const TaskContent = () => (
    <View style={styles.cardContainer}>
      <View style={styles.card}>
        {/* Status Bar */}
        <View style={[styles.statusBar, { backgroundColor: priorityStyle.border }]} />

        <View style={styles.cardContent}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <Ionicons
                name={priorityIcons[priority] || 'information-circle'}
                size={20}
                color={priorityStyle.text}
              />
              <View style={[styles.priorityBadge, { backgroundColor: priorityStyle.bg }]}>
                <Text style={[styles.priorityText, { color: priorityStyle.text }]}>
                  {priorityLabels[priority] || priority}
                </Text>
              </View>
              <View style={styles.statusBadge}>
                <Ionicons
                  name={statusIcons[status] || 'ellipse-outline'}
                  size={16}
                  color={isCompleted ? '#059669' : '#6b7280'}
                />
                <Text style={[styles.statusText, isCompleted && styles.statusCompleted]}>
                  {statusLabels[status] || status}
                </Text>
              </View>
            </View>
          </View>

          {/* Task Name */}
          <TouchableOpacity
            onPress={onPress}
            activeOpacity={0.7}
            style={styles.taskNameContainer}
          >
            <Text style={styles.taskName} numberOfLines={2}>
              {task_name || 'Unnamed Task'}
            </Text>
          </TouchableOpacity>

          {/* Details */}
          <View style={styles.detailsContainer}>
            <View style={styles.detailItem}>
              <Ionicons name="person-outline" size={16} color="#6b7280" />
              <Text style={styles.detailText}>
                {assigned_to || 'غير معين'}
              </Text>
            </View>

            {estimated_hours > 0 && (
              <View style={styles.detailItem}>
                <Ionicons name="time-outline" size={16} color="#6b7280" />
                <Text style={styles.detailText}>
                  {estimated_hours} ساعة
                </Text>
              </View>
            )}

            {due_date && (
              <View style={styles.detailItem}>
                <Ionicons name="calendar-outline" size={16} color="#6b7280" />
                <Text style={styles.detailText}>
                  {new Date(due_date).toLocaleDateString('ar-EG')}
                </Text>
              </View>
            )}
          </View>

          {/* Action Button */}
          {!isCompleted && onComplete && (
            <TouchableOpacity
              style={[styles.completeButton, { backgroundColor: '#2d6a4f' }]}
              onPress={handleComplete}
              activeOpacity={0.8}
            >
              <Ionicons name="checkmark" size={20} color="#ffffff" />
              <Text style={styles.completeButtonText}>
                إتمام المهمة
              </Text>
            </TouchableOpacity>
          )}

          {isCompleted && (
            <View style={styles.completedBadge}>
              <Ionicons name="checkmark-circle" size={20} color="#059669" />
              <Text style={styles.completedText}>✓ مكتملة</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );

  // Use TouchableNativeFeedback for Android ripple effect
  if (Platform.OS === 'android' && TouchableNativeFeedback.canUseNativeForeground()) {
    return (
      <TouchableNativeFeedback
        onPress={onPress}
        useForeground
        background={TouchableNativeFeedback.Ripple('#e5e7eb', false)}
      >
        <View>{TaskContent}</View>
      </TouchableNativeFeedback>
    );
  }

  return TaskContent();
};

// ============================================
// Styles
// ============================================

const styles = StyleSheet.create({
  cardContainer: {
    marginHorizontal: 16,
    marginVertical: 6,
    borderRadius: 12,
    backgroundColor: '#ffffff',
    ...Platform.select({
      ios: {
        shadowColor: '#000000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 3,
      },
    }),
  },
  card: {
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  statusBar: {
    height: 4,
    width: '100%',
  },
  cardContent: {
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    marginLeft: 4,
  },
  priorityText: {
    fontSize: 11,
    fontWeight: '600',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 8,
    gap: 4,
  },
  statusText: {
    fontSize: 11,
    color: '#6b7280',
    fontWeight: '500',
  },
  statusCompleted: {
    color: '#059669',
  },
  taskNameContainer: {
    marginBottom: 10,
  },
  taskName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    lineHeight: 22,
  },
  detailsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
    gap: 12,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailText: {
    fontSize: 13,
    color: '#6b7280',
  },
  completeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    gap: 8,
  },
  completeButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  completedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    gap: 8,
  },
  completedText: {
    color: '#059669',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default TaskCard;
