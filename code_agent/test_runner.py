#!/usr/bin/env python3
"""
Test runner script that validates the environment and runs unit tests
before initializing any models or performing operations.
"""

import os
import sys
import unittest
import argparse
import logging
import importlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_runner")

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = {
        "GITHUB_TOKEN": "GitHub Personal Access Token",
        "GITHUB_USERNAME": "GitHub Username",
        "HF_TOKEN": "Hugging Face API Token (optional for some models)"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if var != "HF_TOKEN" and not os.environ.get(var):  # HF_TOKEN is optional
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.warning("Missing environment variables:")
        for var in missing_vars:
            logger.warning(f"  - {var}")
        return False
    
    return True

def check_dependencies():
    """Check if all required Python packages are installed"""
    required_packages = [
        "smolagents",
        "pygithub",
        "pytest",
        "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning("Missing Python packages:")
        for package in missing_packages:
            logger.warning(f"  - {package}")
        logger.warning("Install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def run_config_validation():
    """Validate the configuration without initializing models"""
    try:
        from code_agent.config import Config
        
        logger.info("Validating configuration...")
        config = Config()
        
        if config.validate():
            logger.info("Configuration is valid")
            return True
        else:
            logger.warning("Configuration is incomplete or invalid")
            logger.warning("GitHub token and username are required for full functionality")
            return False
            
    except Exception as e:
        logger.error(f"Error validating configuration: {str(e)}")
        return False

def run_tests(test_pattern=None, skip_validation=False):
    """Run unit tests with optional pattern matching"""
    # Validate environment first unless skipped
    if not skip_validation:
        env_valid = check_environment()
        deps_valid = check_dependencies()
        config_valid = run_config_validation()
        
        if not all([env_valid, deps_valid, config_valid]):
            logger.warning("Environment validation failed. Use --skip-validation to run tests anyway.")
            if not input("Continue anyway? (y/n): ").lower().startswith('y'):
                return False
    
    # Discover and run tests
    logger.info("Running unit tests...")
    
    # Determine the test directory (relative to this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)  # Go up one level
    test_dir = os.path.join(root_dir, "tests")
    
    if not os.path.exists(test_dir):
        logger.error(f"Test directory not found: {test_dir}")
        return False
    
    # Use unittest discovery
    loader = unittest.TestLoader()
    
    if test_pattern:
        logger.info(f"Running tests matching pattern: {test_pattern}")
        suite = loader.discover(test_dir, pattern=f"*{test_pattern}*.py")
    else:
        suite = loader.discover(test_dir)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    logger.info(f"Test results: {result.testsRun} tests run")
    logger.info(f"  - Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        logger.warning(f"  - Failures: {len(result.failures)}")
        for test, traceback in result.failures:
            logger.warning(f"    - {test}")
    
    if result.errors:
        logger.warning(f"  - Errors: {len(result.errors)}")
        for test, traceback in result.errors:
            logger.warning(f"    - {test}")
    
    return len(result.failures) == 0 and len(result.errors) == 0

def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(description="Run unit tests for Code Agent with environment validation")
    parser.add_argument("--pattern", "-p", help="Pattern to match test files (e.g. 'config' for test_config.py)")
    parser.add_argument("--skip-validation", "-s", action="store_true", help="Skip environment validation")
    
    args = parser.parse_args()
    
    success = run_tests(args.pattern, args.skip_validation)
    
    # Set exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()