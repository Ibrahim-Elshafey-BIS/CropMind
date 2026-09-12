/**
 * CropMind - Report Issue Screen
 * Worker issue reporting screen
 * 
 * Author: CropMind Team
 * Date: 2026
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  StatusBar,
  Alert,
  ActivityIndicator,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Picker } from '@react-native-picker/picker';
import * as ImagePicker from 'expo-image-picker';
import { reportIssue, getCurrentUser } from '../services/api';

const ReportIssue = ({ navigation, route }) => {
  // Get params from navigation
  const params = route?.params || {};
  const { cropName, diseaseName, severity: diseaseSeverity } = params;

  // Form state
  const [issueType, setIssueType] = useState(params.cropName ? 'crop_health' : '');
  const [severity, setSeverity] = useState(diseaseSeverity ? 'high' : 'medium');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [image, setImage] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [farmId, setFarmId] = useState(null);
  const [workerId, setWorkerId] = useState(null);

  // Auto-fill from FieldScan
  useEffect(() => {
    if (cropName && diseaseName) {
      setDescription(
        `تم اكتشاف مرض ${diseaseName} في محصول ${cropName}`
      );
    }
  }, [cropName, diseaseName]);

  // Get user data
  useEffect(() => {
    const loadUser = async () => {
      const user = await getCurrentUser();
      if (user) {
        setFarmId(user.farm_id);
        setWorkerId(user.id);
      }
    };
    loadUser();
  }, []);

  // Issue types with labels and icons
  const issueTypes = [
    { value: 'crop_health', label: 'مرض نبات', icon: 'leaf-outline' },
    { value: 'irrigation', label: 'مشكلة ري', icon: 'water-outline' },
    { value: 'equipment', label: 'آلة معطلة', icon: 'construct-outline' },
    { value: 'labor', label: 'مشكلة عمال', icon: 'people-outline' },
    { value: 'other', label: 'أخرى', icon: 'alert-circle-outline' },
  ];

  // Severity options
  const severityOptions = [
    { value: 'low', label: 'منخفض', color: '#2563eb' },
    { value: 'medium', label: 'متوسط', color: '#d97706' },
    { value: 'high', label: 'مرتفع', color: '#dc2626' },
  ];

  // Pick image
  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('خطأ', 'يرجى منح صلاحية الوصول إلى المعرض');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled) {
      setImage(result.assets[0]);
    }
  };

  // Remove image
  const removeImage = () => {
    setImage(null);
  };

  // Submit report
  const handleSubmit = async () => {
    // Validate form
    if (!issueType) {
      Alert.alert('تنبيه', 'يرجى اختيار نوع المشكلة');
      return;
    }

    if (!description.trim()) {
      Alert.alert('تنبيه', 'يرجى كتابة وصف المشكلة');
      return;
    }

    if (!location.trim()) {
      Alert.alert('تنبيه', 'يرجى تحديد موقع المشكلة');
      return;
    }

    setIsSubmitting(true);

    try {
      const issueData = {
        type: issueType,
        severity: severity,
        description: description,
        location: location,
        crop_name: cropName || null,
        disease_name: diseaseName || null,
      };

      const result = await reportIssue(farmId, workerId, issueData);

      if (result.success) {
        setIsSuccess(true);
        Alert.alert(
          '✅ تم الإرسال',
          'تم إرسال تقرير المشكلة بنجاح. سيتم مراجعته قريباً.',
          [{ text: 'حسناً', onPress: () => setIsSuccess(false) }]
        );
        // Navigate back after success
        setTimeout(() => {
          navigation.goBack();
        }, 1500);
      } else {
        Alert.alert('فشل الإرسال', result.error || 'حدث خطأ أثناء إرسال التقرير');
      }
    } catch (error) {
      console.error('[ReportIssue] Submit error:', error);
      Alert.alert('خطأ', 'فشل إرسال التقرير، يرجى المحاولة مرة أخرى');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get issue label
  const getIssueLabel = (value) => {
    const found = issueTypes.find((item) => item.value === value);
    return found ? found.label : value;
  };

  // Get issue icon
  const getIssueIcon = (value) => {
    const found = issueTypes.find((item) => item.value === value);
    return found ? found.icon : 'alert-circle-outline';
  };

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
        <Text style={styles.headerTitle}>تقرير مشكلة</Text>
        <View style={styles.headerPlaceholder} />
      </View>

      {isSuccess ? (
        <View style={styles.successContainer}>
          <Ionicons name="checkmark-circle" size={80} color="#059669" />
          <Text style={styles.successTitle}>تم الإرسال بنجاح!</Text>
          <Text style={styles.successText}>
            سيتم مراجعة تقريرك قريباً
          </Text>
        </View>
      ) : (
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Issue Type */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>نوع المشكلة *</Text>
            <View style={styles.pickerContainer}>
              <Picker
                selectedValue={issueType}
                onValueChange={(value) => setIssueType(value)}
                style={styles.picker}
                dropdownIconColor="#6b7280"
              >
                <Picker.Item label="اختر نوع المشكلة" value="" />
                {issueTypes.map((type) => (
                  <Picker.Item
                    key={type.value}
                    label={type.label}
                    value={type.value}
                  />
                ))}
              </Picker>
              {issueType && (
                <View style={styles.pickerIcon}>
                  <Ionicons
                    name={getIssueIcon(issueType)}
                    size={20}
                    color="#2d6a4f"
                  />
                </View>
              )}
            </View>
          </View>

          {/* Severity */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>درجة الخطورة *</Text>
            <View style={styles.severityContainer}>
              {severityOptions.map((option) => (
                <TouchableOpacity
                  key={option.value}
                  style={[
                    styles.severityOption,
                    severity === option.value && styles.severityOptionSelected,
                    { borderColor: option.color },
                  ]}
                  onPress={() => setSeverity(option.value)}
                >
                  <View
                    style={[
                      styles.severityDot,
                      { backgroundColor: option.color },
                    ]}
                  />
                  <Text
                    style={[
                      styles.severityOptionText,
                      severity === option.value && styles.severityOptionTextSelected,
                    ]}
                  >
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Description */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>وصف المشكلة *</Text>
            <TextInput
              style={[styles.textArea, styles.textInput]}
              placeholder="صف المشكلة بالتفصيل..."
              placeholderTextColor="#9ca3af"
              multiline
              numberOfLines={4}
              textAlignVertical="top"
              value={description}
              onChangeText={setDescription}
            />
          </View>

          {/* Location */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>الموقع *</Text>
            <View style={styles.locationInput}>
              <Ionicons
                name="location-outline"
                size={20}
                color="#9ca3af"
                style={styles.locationIcon}
              />
              <TextInput
                style={[styles.textInput, styles.locationTextInput]}
                placeholder="حدد موقع المشكلة (مثل: حقل رقم 3)"
                placeholderTextColor="#9ca3af"
                value={location}
                onChangeText={setLocation}
              />
            </View>
          </View>

          {/* Image Upload */}
          <View style={styles.formGroup}>
            <Text style={styles.label}>صورة (اختياري)</Text>
            {image ? (
              <View style={styles.imagePreviewContainer}>
                <Image
                  source={{ uri: image.uri }}
                  style={styles.imagePreview}
                  resizeMode="cover"
                />
                <TouchableOpacity
                  style={styles.removeImageButton}
                  onPress={removeImage}
                >
                  <Ionicons name="close-circle" size={28} color="#dc2626" />
                </TouchableOpacity>
              </View>
            ) : (
              <TouchableOpacity
                style={styles.uploadButton}
                onPress={pickImage}
              >
                <Ionicons name="camera-outline" size={32} color="#9ca3af" />
                <Text style={styles.uploadText}>إضافة صورة</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Auto-filled info from FieldScan */}
          {cropName && diseaseName && (
            <View style={styles.infoBox}>
              <Ionicons name="information-circle" size={20} color="#2d6a4f" />
              <Text style={styles.infoText}>
                تم ملء البيانات تلقائياً من مسح المحصول
              </Text>
            </View>
          )}

          {/* Submit Button */}
          <TouchableOpacity
            style={[styles.submitButton, isSubmitting && styles.submitDisabled]}
            onPress={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <ActivityIndicator size="small" color="#ffffff" />
            ) : (
              <>
                <Ionicons name="send-outline" size={20} color="#ffffff" />
                <Text style={styles.submitButtonText}>إرسال التقرير</Text>
              </>
            )}
          </TouchableOpacity>
        </ScrollView>
      )}
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
  headerPlaceholder: {
    width: 40,
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 20,
  },
  formGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  pickerContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    position: 'relative',
  },
  picker: {
    height: 50,
  },
  pickerIcon: {
    position: 'absolute',
    right: 12,
    top: 15,
  },
  textInput: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 15,
    color: '#1f2937',
    minHeight: 48,
  },
  textArea: {
    minHeight: 120,
    paddingTop: 12,
  },
  locationInput: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  locationIcon: {
    marginLeft: 12,
  },
  locationTextInput: {
    flex: 1,
    borderWidth: 0,
  },
  severityContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  severityOption: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 2,
    backgroundColor: '#ffffff',
    gap: 6,
  },
  severityOptionSelected: {
    backgroundColor: '#f0fdf4',
  },
  severityDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  severityOptionText: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: '500',
  },
  severityOptionTextSelected: {
    color: '#1f2937',
    fontWeight: '600',
  },
  uploadButton: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderStyle: 'dashed',
    paddingVertical: 30,
    alignItems: 'center',
    justifyContent: 'center',
  },
  uploadText: {
    color: '#6b7280',
    fontSize: 14,
    marginTop: 8,
  },
  imagePreviewContainer: {
    position: 'relative',
    borderRadius: 12,
    overflow: 'hidden',
  },
  imagePreview: {
    width: '100%',
    height: 200,
    borderRadius: 12,
  },
  removeImageButton: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#ffffff',
    borderRadius: 14,
  },
  infoBox: {
    backgroundColor: '#f0fdf4',
    borderRadius: 10,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#bbf7d0',
  },
  infoText: {
    fontSize: 14,
    color: '#065f46',
    flex: 1,
  },
  submitButton: {
    backgroundColor: '#2d6a4f',
    borderRadius: 12,
    paddingVertical: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 30,
  },
  submitDisabled: {
    opacity: 0.7,
  },
  submitButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  successContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 40,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 16,
  },
  successText: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default ReportIssue;
