/**
 * CropMind - Field Scan Screen
 * Camera-based crop disease detection for workers
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
  Image,
  ActivityIndicator,
  ScrollView,
  Alert,
  SafeAreaView,
  StatusBar,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Camera } from 'expo-camera';
import * as ImagePicker from 'expo-image-picker';
import { scanCrop, getCurrentUser } from '../services/api';

const FieldScan = ({ navigation }) => {
  const [hasPermission, setHasPermission] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [farmId, setFarmId] = useState(null);
  const [scanMode, setScanMode] = useState('camera'); // 'camera' | 'gallery' | 'results'
  
  const cameraRef = useRef(null);

  // Get camera permission
  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
      
      // Get farm ID from user
      const user = await getCurrentUser();
      if (user?.farm_id) {
        setFarmId(user.farm_id);
      }
    })();
  }, []);

  // Take picture
  const takePicture = async () => {
    if (!cameraRef.current || !cameraReady) return;
    
    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: true,
      });
      setCapturedImage(photo);
      setScanMode('preview');
    } catch (error) {
      console.error('[FieldScan] Take picture error:', error);
      Alert.alert('خطأ', 'فشل التقاط الصورة، يرجى المحاولة مرة أخرى');
    }
  };

  // Pick image from gallery
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
      setCapturedImage(result.assets[0]);
      setScanMode('preview');
    }
  };

  // Analyze image
  const analyzeImage = async () => {
    if (!capturedImage) return;
    
    setIsAnalyzing(true);
    try {
      // Convert image to base64
      const base64 = capturedImage.base64 || capturedImage.uri;
      const result = await scanCrop(base64, farmId);
      
      if (result.success) {
        setResult(result.data);
        setScanMode('results');
      } else {
        Alert.alert('فشل التحليل', result.error || 'حدث خطأ أثناء تحليل الصورة');
      }
    } catch (error) {
      console.error('[FieldScan] Analyze error:', error);
      Alert.alert('خطأ', 'فشل تحليل الصورة، يرجى المحاولة مرة أخرى');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Reset scan
  const resetScan = () => {
    setCapturedImage(null);
    setResult(null);
    setScanMode('camera');
    setIsAnalyzing(false);
  };

  // Get severity color and label
  const getSeverityInfo = (severity) => {
    const map = {
      Healthy: { color: '#059669', label: 'سليم' },
      Low: { color: '#2563eb', label: 'منخفض' },
      Medium: { color: '#d97706', label: 'متوسط' },
      High: { color: '#dc2626', label: 'مرتفع' },
      Critical: { color: '#991b1b', label: 'حرج' },
    };
    return map[severity] || map.Medium;
  };

  // Go to report issue
  const handleReportIssue = () => {
    navigation.navigate('ReportIssue', {
      cropName: result?.crop || '',
      diseaseName: result?.disease_name || '',
      severity: result?.severity || '',
    });
  };

  // Camera permission loading
  if (hasPermission === null) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2d6a4f" />
          <Text style={styles.loadingText}>طلب صلاحية الكاميرا...</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Camera permission denied
  if (hasPermission === false) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="camera-off-outline" size={64} color="#dc2626" />
          <Text style={styles.errorTitle}>لا يوجد صلاحية للكاميرا</Text>
          <Text style={styles.errorText}>
            يرجى منح صلاحية الكاميرا في إعدادات الجهاز
          </Text>
          <TouchableOpacity
            style={styles.permissionButton}
            onPress={() => {
              if (Platform.OS === 'ios') {
                // iOS: open settings
                Linking.openURL('app-settings:');
              } else {
                // Android: request again
                Camera.requestCameraPermissionsAsync().then(({ status }) => {
                  setHasPermission(status === 'granted');
                });
              }
            }}
          >
            <Text style={styles.permissionButtonText}>فتح الإعدادات</Text>
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
        <Text style={styles.headerTitle}>مسح المحصول</Text>
        {scanMode !== 'camera' && (
          <TouchableOpacity onPress={resetScan} style={styles.closeButton}>
            <Ionicons name="close" size={24} color="#ffffff" />
          </TouchableOpacity>
        )}
      </View>

      {/* Camera View */}
      {scanMode === 'camera' && (
        <View style={styles.cameraContainer}>
          <Camera
            ref={cameraRef}
            style={styles.camera}
            onCameraReady={() => setCameraReady(true)}
            type={Camera.Constants.Type.back}
          >
            <View style={styles.overlay}>
              <View style={styles.scanFrame} />
            </View>
          </Camera>
          
          {/* Camera Controls */}
          <View style={styles.cameraControls}>
            <TouchableOpacity
              style={styles.galleryButton}
              onPress={pickImage}
            >
              <Ionicons name="images-outline" size={28} color="#ffffff" />
              <Text style={styles.controlLabel}>معرض</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.captureButton}
              onPress={takePicture}
              disabled={!cameraReady}
            >
              <View style={styles.captureInner} />
            </TouchableOpacity>

            <View style={styles.galleryButtonPlaceholder} />
          </View>

          <Text style={styles.instructionText}>
            قم بتصوير ورقة النبات المصابة
          </Text>
        </View>
      )}

      {/* Preview Mode */}
      {scanMode === 'preview' && capturedImage && (
        <View style={styles.previewContainer}>
          <Image
            source={{ uri: capturedImage.uri }}
            style={styles.previewImage}
            resizeMode="cover"
          />
          
          <View style={styles.previewControls}>
            <TouchableOpacity
              style={styles.retakeButton}
              onPress={resetScan}
            >
              <Ionicons name="refresh-outline" size={24} color="#4b5563" />
              <Text style={styles.retakeText}>إعادة</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.analyzeButton}
              onPress={analyzeImage}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <ActivityIndicator size="small" color="#ffffff" />
              ) : (
                <>
                  <Ionicons name="leaf-outline" size={24} color="#ffffff" />
                  <Text style={styles.analyzeButtonText}>تحليل المحصول</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Results Mode */}
      {scanMode === 'results' && result && (
        <ScrollView style={styles.resultsContainer} showsVerticalScrollIndicator={false}>
          {/* Result Header */}
          <View style={styles.resultHeader}>
            <View style={styles.resultIconContainer}>
              <Ionicons name="leaf-outline" size={40} color="#ffffff" />
            </View>
            <Text style={styles.resultTitle}>نتيجة التحليل</Text>
          </View>

          {/* Disease Info */}
          <View style={styles.resultCard}>
            <Text style={styles.resultLabel}>المرض المكتشف</Text>
            <Text style={styles.resultValue}>
              {result.disease_name || 'غير معروف'}
            </Text>
          </View>

          {/* Confidence */}
          <View style={styles.resultCard}>
            <Text style={styles.resultLabel}>نسبة الثقة</Text>
            <View style={styles.confidenceContainer}>
              <View style={styles.confidenceBar}>
                <View
                  style={[
                    styles.confidenceFill,
                    { width: `${Math.min(result.confidence || 0, 100)}%` },
                  ]}
                />
              </View>
              <Text style={styles.confidenceText}>
                {result.confidence?.toFixed(1) || 0}%
              </Text>
            </View>
          </View>

          {/* Severity */}
          <View style={styles.resultCard}>
            <Text style={styles.resultLabel}>درجة الخطورة</Text>
            <View style={styles.severityContainer}>
              <View
                style={[
                  styles.severityBadge,
                  { backgroundColor: getSeverityInfo(result.severity).color + '20' },
                ]}
              >
                <Text
                  style={[
                    styles.severityText,
                    { color: getSeverityInfo(result.severity).color },
                  ]}
                >
                  {getSeverityInfo(result.severity).label}
                </Text>
              </View>
            </View>
          </View>

          {/* Treatment */}
          {result.treatment && (
            <View style={styles.resultCard}>
              <Text style={styles.resultLabel}>خطة العلاج</Text>
              <Text style={styles.treatmentText}>{result.treatment}</Text>
            </View>
          )}

          {/* Actions */}
          <View style={styles.actionsContainer}>
            <TouchableOpacity
              style={styles.rescanButton}
              onPress={resetScan}
            >
              <Ionicons name="camera-outline" size={20} color="#2d6a4f" />
              <Text style={styles.rescanText}>مسح مرة أخرى</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.reportButton}
              onPress={handleReportIssue}
            >
              <Ionicons name="flag-outline" size={20} color="#ffffff" />
              <Text style={styles.reportButtonText}>تقرير مشكلة</Text>
            </TouchableOpacity>
          </View>

          {/* Crop info */}
          {result.crop && (
            <Text style={styles.cropInfoText}>
              المحصول: {result.crop}
            </Text>
          )}
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
    paddingHorizontal: 20,
    paddingVertical: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  closeButton: {
    position: 'absolute',
    right: 16,
    top: 16,
    padding: 4,
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
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1f2937',
    marginTop: 12,
  },
  errorText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 20,
  },
  permissionButton: {
    backgroundColor: '#2d6a4f',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  permissionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  cameraContainer: {
    flex: 1,
    backgroundColor: '#000000',
  },
  camera: {
    flex: 1,
  },
  overlay: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  scanFrame: {
    width: 250,
    height: 250,
    borderWidth: 2,
    borderColor: '#ffffff',
    borderRadius: 16,
    backgroundColor: 'transparent',
  },
  cameraControls: {
    position: 'absolute',
    bottom: 40,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  captureButton: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  captureInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#ffffff',
    borderWidth: 3,
    borderColor: '#2d6a4f',
  },
  galleryButton: {
    alignItems: 'center',
  },
  galleryButtonPlaceholder: {
    width: 48,
    height: 48,
  },
  controlLabel: {
    color: '#ffffff',
    fontSize: 12,
    marginTop: 4,
  },
  instructionText: {
    position: 'absolute',
    bottom: 120,
    left: 0,
    right: 0,
    textAlign: 'center',
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
    textShadowColor: 'rgba(0,0,0,0.5)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 4,
  },
  previewContainer: {
    flex: 1,
    backgroundColor: '#1f2937',
    alignItems: 'center',
    justifyContent: 'center',
  },
  previewImage: {
    width: '100%',
    height: '70%',
  },
  previewControls: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 20,
    gap: 12,
  },
  retakeButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f3f4f6',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  retakeText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4b5563',
  },
  analyzeButton: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2d6a4f',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  analyzeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  resultsContainer: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  resultHeader: {
    alignItems: 'center',
    marginBottom: 20,
  },
  resultIconContainer: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#2d6a4f',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  resultTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  resultCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  resultLabel: {
    fontSize: 12,
    color: '#9ca3af',
    fontWeight: '500',
    marginBottom: 4,
  },
  resultValue: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
  },
  confidenceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  confidenceBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    overflow: 'hidden',
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#2d6a4f',
    borderRadius: 4,
  },
  confidenceText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    minWidth: 50,
  },
  severityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  severityBadge: {
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 20,
  },
  severityText: {
    fontSize: 16,
    fontWeight: '600',
  },
  treatmentText: {
    fontSize: 15,
    color: '#4b5563',
    lineHeight: 22,
  },
  actionsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
    marginBottom: 16,
  },
  rescanButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    paddingVertical: 14,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#2d6a4f',
    gap: 8,
  },
  rescanText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2d6a4f',
  },
  reportButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#dc2626',
    paddingVertical: 14,
    borderRadius: 12,
    gap: 8,
  },
  reportButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  cropInfoText: {
    textAlign: 'center',
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 20,
  },
});

export default FieldScan;
