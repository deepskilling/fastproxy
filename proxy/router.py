"""
Router - Path-based routing and configuration management
"""
import yaml
import logging
from typing import Dict, List, Optional
from pathlib import Path

from security.ssrf_protection import validate_route_targets, SSRFValidationError

logger = logging.getLogger(__name__)


class Router:
    """
    Manages route configuration and path matching
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.routes: List[Dict[str, str]] = []
        self.config: Dict = {}
        
    def load_config(self) -> Dict:
        """
        Load and parse configuration from YAML file
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            self.routes = self.config.get('routes', [])
            
            # Validate routes
            self._validate_routes()
            
            # SSRF Protection: Validate all target URLs
            try:
                validate_route_targets(self.routes)
            except SSRFValidationError as e:
                logger.error(f"SSRF validation failed: {e}")
                raise ValueError(f"Security validation failed: {e}")
            
            logger.info(f"Loaded {len(self.routes)} routes from {self.config_path}")
            return self.config
            
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _validate_routes(self):
        """
        Validate route configuration
        """
        if not self.routes:
            raise ValueError("No routes defined in configuration")
        
        for idx, route in enumerate(self.routes):
            if 'path' not in route or 'target' not in route:
                raise ValueError(f"Route {idx} missing 'path' or 'target' field")
            
            if not route['path'].startswith('/'):
                raise ValueError(f"Route path must start with '/': {route['path']}")
            
            if not route['target'].startswith('http'):
                raise ValueError(f"Route target must be valid HTTP URL: {route['target']}")
    
    def match_route(self, path: str) -> Optional[Dict[str, str]]:
        """
        Find matching route for given path
        Uses prefix matching - longest match wins
        Route must be followed by '/' or be an exact match
        """
        best_match = None
        best_match_length = 0
        
        for route in self.routes:
            route_path = route['path']
            # Check if path matches: exact match OR starts with route_path followed by /
            if path == route_path or path.startswith(route_path + '/') or (route_path == '/' and path.startswith('/')):
                if len(route_path) > best_match_length:
                    best_match = route
                    best_match_length = len(route_path)
        
        return best_match
    
    def get_routes(self) -> List[Dict[str, str]]:
        """
        Get all configured routes
        """
        return self.routes
    
    def get_config(self) -> Dict:
        """
        Get full configuration
        """
        return self.config
    
    def get_rate_limit_config(self) -> Dict:
        """
        Get rate limiting configuration
        """
        return self.config.get('rate_limit', {'requests_per_minute': 100})
    
    def get_cors_config(self) -> Dict:
        """
        Get CORS configuration
        """
        return self.config.get('cors', {'allow_origins': ['*']})

