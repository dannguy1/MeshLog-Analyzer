"""
Monitoring and metrics - Simplified for demo
"""

class MetricsCollector:
    """Metrics collector - disabled for demo"""
    def __init__(self):
        pass
    
    def collect(self, *args, **kwargs):
        """Collect metrics - disabled for demo"""
        pass
    
    def record_metric(self, *args, **kwargs):
        """Record metric - disabled for demo"""
        pass
    
    def increment_counter(self, *args, **kwargs):
        """Increment counter - disabled for demo"""
        pass
    
    def record_histogram(self, *args, **kwargs):
        """Record histogram - disabled for demo"""
        pass
    
    def set_gauge(self, *args, **kwargs):
        """Set gauge - disabled for demo"""
        pass

class HealthChecker:
    """Health checker - simplified for demo"""
    def __init__(self):
        pass
    
    def check(self):
        return {"status": "healthy"}

class RequestMetricsMiddleware:
    """Request metrics middleware - disabled for demo"""
    def __init__(self, *args, **kwargs):
        pass

# Create instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()
