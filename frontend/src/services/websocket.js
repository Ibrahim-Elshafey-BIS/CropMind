class WebSocketService {
  constructor() {
    this.socket = null;
    this.farmId = null;
    this.status = 'disconnected';
    this.messageHandlers = [];
    this.connectHandlers = [];
    this.disconnectHandlers = [];
    this.errorHandlers = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = null;
    this.reconnectDelay = 1000;
    this.isConnecting = false;
  }

  /**
   * Connect to WebSocket server
   * @param {string} farmId - Farm ID for the WebSocket endpoint
   */
  connect(farmId) {
    if (this.isConnecting) {
      console.log('WebSocket: Connection already in progress');
      return;
    }

    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      console.log('WebSocket: Already connected');
      return;
    }

    if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket: Connection in progress');
      return;
    }

    this.farmId = farmId;
    this.isConnecting = true;
    this.status = 'connecting';
    this.notifyStatusChange('connecting');

    try {
      const wsUrl = `ws://localhost:8000/ws/${farmId}`;
      console.log(`WebSocket: Connecting to ${wsUrl}`);
      
      this.socket = new WebSocket(wsUrl);
      
      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('WebSocket: Connection error', error);
      this.isConnecting = false;
      this.status = 'error';
      this.notifyStatusChange('error');
      this.notifyError(error);
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket open event
   */
  handleOpen(event) {
    console.log('WebSocket: Connected');
    this.isConnecting = false;
    this.status = 'connected';
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    this.notifyStatusChange('connected');
    this.notifyConnect(event);
  }

  /**
   * Handle WebSocket message event
   * @param {MessageEvent} event
   */
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      this.notifyMessage(data);
    } catch (error) {
      console.error('WebSocket: Failed to parse message', error);
      // Still notify raw data if parsing fails
      this.notifyMessage({ raw: event.data, error: 'Invalid JSON' });
    }
  }

  /**
   * Handle WebSocket close event
   * @param {CloseEvent} event
   */
  handleClose(event) {
    console.log(`WebSocket: Disconnected (code: ${event.code})`);
    this.isConnecting = false;
    this.status = 'disconnected';
    this.notifyStatusChange('disconnected');
    this.notifyDisconnect(event);

    // Attempt reconnect if not closed cleanly
    if (event.code !== 1000 && event.code !== 1001) {
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket error event
   * @param {Event} event
   */
  handleError(event) {
    console.error('WebSocket: Error', event);
    this.status = 'error';
    this.notifyStatusChange('error');
    this.notifyError(event);
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('WebSocket: Max reconnection attempts reached');
      this.status = 'error';
      this.notifyStatusChange('error');
      return;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    console.log(`WebSocket: Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      if (this.farmId) {
        this.connect(this.farmId);
      }
    }, delay);
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    this.reconnectAttempts = 0;
    this.isConnecting = false;
    this.status = 'disconnected';
    this.notifyStatusChange('disconnected');

    if (this.socket) {
      this.socket.onopen = null;
      this.socket.onmessage = null;
      this.socket.onclose = null;
      this.socket.onerror = null;
      
      if (this.socket.readyState === WebSocket.OPEN) {
        this.socket.close(1000, 'Client disconnected');
      }
      this.socket = null;
    }
  }

  /**
   * Send data through WebSocket
   * @param {object} data - JSON-serializable data
   * @returns {boolean} - True if message was sent
   */
  send(data) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket: Cannot send message, not connected');
      return false;
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
      return true;
    } catch (error) {
      console.error('WebSocket: Send error', error);
      return false;
    }
  }

  /**
   * Register message handler
   * @param {function} callback - Function to handle incoming messages
   * @returns {function} - Unsubscribe function
   */
  onMessage(callback) {
    if (typeof callback !== 'function') {
      throw new Error('onMessage callback must be a function');
    }
    this.messageHandlers.push(callback);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(handler => handler !== callback);
    };
  }

  /**
   * Register connect handler
   * @param {function} callback - Function to call on connection
   * @returns {function} - Unsubscribe function
   */
  onConnect(callback) {
    if (typeof callback !== 'function') {
      throw new Error('onConnect callback must be a function');
    }
    this.connectHandlers.push(callback);
    return () => {
      this.connectHandlers = this.connectHandlers.filter(handler => handler !== callback);
    };
  }

  /**
   * Register disconnect handler
   * @param {function} callback - Function to call on disconnection
   * @returns {function} - Unsubscribe function
   */
  onDisconnect(callback) {
    if (typeof callback !== 'function') {
      throw new Error('onDisconnect callback must be a function');
    }
    this.disconnectHandlers.push(callback);
    return () => {
      this.disconnectHandlers = this.disconnectHandlers.filter(handler => handler !== callback);
    };
  }

  /**
   * Register error handler
   * @param {function} callback - Function to call on error
   * @returns {function} - Unsubscribe function
   */
  onError(callback) {
    if (typeof callback !== 'function') {
      throw new Error('onError callback must be a function');
    }
    this.errorHandlers.push(callback);
    return () => {
      this.errorHandlers = this.errorHandlers.filter(handler => handler !== callback);
    };
  }

  /**
   * Notify all message handlers
   * @param {object} data - Message data
   */
  notifyMessage(data) {
    this.messageHandlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error('WebSocket: Message handler error', error);
      }
    });
  }

  /**
   * Notify all connect handlers
   * @param {Event} event - WebSocket event
   */
  notifyConnect(event) {
    this.connectHandlers.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error('WebSocket: Connect handler error', error);
      }
    });
  }

  /**
   * Notify all disconnect handlers
   * @param {CloseEvent} event - WebSocket close event
   */
  notifyDisconnect(event) {
    this.disconnectHandlers.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error('WebSocket: Disconnect handler error', error);
      }
    });
  }

  /**
   * Notify all error handlers
   * @param {Event} event - WebSocket error event
   */
  notifyError(event) {
    this.errorHandlers.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error('WebSocket: Error handler error', error);
      }
    });
  }

  /**
   * Notify status change
   * @param {string} status - Connection status
   */
  notifyStatusChange(status) {
    this.status = status;
    // Additional status notification can be added here if needed
  }

  /**
   * Get current connection status
   * @returns {string} - 'connected', 'connecting', 'disconnected', 'error'
   */
  getStatus() {
    return this.status;
  }

  /**
   * Check if WebSocket is connected
   * @returns {boolean}
   */
  isConnected() {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }

  /**
   * Reset reconnection state
   */
  resetReconnection() {
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }
}

// Singleton instance
const websocket = new WebSocketService();
export default websocket;
