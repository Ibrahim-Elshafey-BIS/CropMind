/**
 * CropMind - Alert Notification Component
 * Displays an alert notification for the worker mobile app
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

const AlertNotification = ({
  alert,
  onDismiss,
  onPress,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const slideAnim = useRef(new Animated.Value(0)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const {
    type = 'general',
    severity = 'medium',
    message = '',
    data = {},
    timestamp = new Date().toISOString(),
  } = alert || {};

  // Animation on mount
  useEffect(() => {
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  // Auto dismiss after 8 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      handleDismiss();
    }, 8000);

    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = () => {
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start(() => {
      setIsVisible(false);
      if (onDismiss) {
        onDismiss(alert);
      }
    });
  };

  const handlePress = () => {
    if (onPress) {
      onPress(alert);
    }
  };

  // Get icon based on alert type
  const getIcon = (type) => {
    const iconMap = {
      low_stock: 'cart-outline',
      sensor_anomaly: 'warning-outline',
      crop_health: 'leaf-outline',
      weather_warning: 'cloudy-outline',
      disease_detected: 'bug-outline',
      system: 'information-circle-outline',
      general: 'notifications-outline',
    };
    return iconMap[type] || iconMap.general;
  };

  // Get color based on severity
  const getColor = (severity) => {
    const colorMap = {
      critical: { bg: '#fee2e2', border: '#dc2626', text: '#dc2626' },
      high: { bg: '#fef3c7', border: '#d97706', text: '#d97706' },
      medium: { bg: '#fef9c3', border: '#ca8a04', text: '#ca8a04' },
      low: { bg: '#dbeafe', border: '#2563eb', text: '#2563eb' },
    };
    return colorMap[severity] || colorMap.medium;
  };

  // Get severity label in Arabic
  const getSeverityLabel = (severity) => {
    const labelMap = {
      critical: 'حرج',
      high: 'مرتفع',
      medium: 'متوسط',
      low: 'منخفض',
    };
    return labelMap[severity] || severity;
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('ar-EG', {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '';
    }
  };

  if (!isVisible || !alert) {
    return null;
  }

  const colors = getColor(severity);
  const icon = getIcon(type);
  const severityLabel = getSeverityLabel(severity);

  const translateY = slideAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [-100, 0],
  });

  return (
    <Animated.View
      style={[
        styles.container,
        {
          transform: [{ translateY }],
          opacity: fadeAnim,
        },
      ]}
    >
      <TouchableOpacity
        style={[styles.card, { borderLeftColor: colors.border }]}
        onPress={handlePress}
        activeOpacity={0.8}
      >
        {/* Left Icon */}
        <View style={[styles.iconContainer, { backgroundColor: colors.bg }]}>
          <Ionicons name={icon} size={24} color={colors.text} />
        </View>

        {/* Content */}
        <View style={styles.contentContainer}>
          <View style={styles.headerRow}>
            <Text style={[styles.severityText, { color: colors.text }]} numberOfLines={1}>
              {severityLabel}
            </Text>
            <Text style={styles.timeText}>{formatTime(timestamp)}</Text>
          </View>

          <Text style={styles.messageText} numberOfLines={2}>
            {message || 'تنبيه جديد'}
          </Text>

          {/* Optional data preview */}
          {data?.item_name && (
            <View style={styles.dataRow}>
              <Text style={styles.dataText}>
                {data.item_name}
                {data.quantity !== undefined && `: ${data.quantity}`}
                {data.unit && ` ${data.unit}`}
              </Text>
            </View>
          )}
        </View>

        {/* Dismiss Button */}
        <TouchableOpacity
          style={styles.dismissButton}
          onPress={handleDismiss}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        >
          <Ionicons name="close" size={20} color="#9ca3af" />
        </TouchableOpacity>
      </TouchableOpacity>
    </Animated.View>
  );
};

// ============================================
// Styles
// ============================================

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 4,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 14,
    borderLeftWidth: 4,
    borderLeftColor: '#d97706',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
  },
  iconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  contentContainer: {
    flex: 1,
    marginRight: 8,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  severityText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#d97706',
  },
  timeText: {
    fontSize: 11,
    color: '#9ca3af',
  },
  messageText: {
    fontSize: 14,
    color: '#1f2937',
    fontWeight: '500',
    lineHeight: 20,
  },
  dataRow: {
    marginTop: 2,
  },
  dataText: {
    fontSize: 12,
    color: '#6b7280',
  },
  dismissButton: {
    padding: 4,
    marginLeft: 4,
    alignSelf: 'flex-start',
  },
});

export default AlertNotification;
