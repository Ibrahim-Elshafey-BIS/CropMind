/**
 * CropMind - Complete Button Component
 * Task completion button with loading and state management
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React, { useState } from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  View,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { completeTask } from '../services/api';

const CompleteButton = ({
  taskId,
  onSuccess,
  onError,
  disabled = false,
  label = 'إتمام المهمة',
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  const handlePress = async () => {
    if (disabled || isLoading || isCompleted) return;

    setIsLoading(true);
    try {
      const result = await completeTask(taskId);
      
      if (result.success) {
        setIsCompleted(true);
        setIsLoading(false);
        if (onSuccess) {
          onSuccess(result.data);
        }
      } else {
        setIsLoading(false);
        if (onError) {
          onError(result.error || 'Failed to complete task');
        }
      }
    } catch (error) {
      setIsLoading(false);
      const errorMessage = error.response?.data?.detail || error.message || 'Network error';
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  // Completed state
  if (isCompleted) {
    return (
      <View style={[styles.button, styles.completedButton]}>
        <Ionicons name="checkmark-circle" size={20} color="#059669" />
        <Text style={styles.completedText}>✓ مكتملة</Text>
      </View>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <View style={[styles.button, styles.loadingButton]}>
        <ActivityIndicator size="small" color="#ffffff" />
        <Text style={styles.loadingText}>جاري الإتمام...</Text>
      </View>
    );
  }

  // Normal/Disabled state
  return (
    <TouchableOpacity
      style={[
        styles.button,
        styles.activeButton,
        disabled && styles.disabledButton,
      ]}
      onPress={handlePress}
      disabled={disabled || isLoading}
      activeOpacity={0.8}
    >
      <Ionicons name="checkmark" size={18} color="#ffffff" />
      <Text style={styles.buttonText}>{label}</Text>
    </TouchableOpacity>
  );
};

// ============================================
// Styles
// ============================================

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    gap: 6,
    minHeight: 40,
    minWidth: 120,
  },
  activeButton: {
    backgroundColor: '#2d6a4f',
  },
  disabledButton: {
    backgroundColor: '#9ca3af',
    opacity: 0.6,
  },
  loadingButton: {
    backgroundColor: '#2d6a4f',
    opacity: 0.8,
  },
  completedButton: {
    backgroundColor: '#d1fae5',
    borderWidth: 1,
    borderColor: '#6ee7b7',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  loadingText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
  },
  completedText: {
    color: '#059669',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default CompleteButton;
