"""
Environment validator script that checks if all prerequisites are met
before attempting to use any model operations.
"""

import os
import sys
import logging
import importlib
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("validator")

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = {
        "GITHUB_TOKEN": "GitHub Personal Access Token",
        "GITHUB_USERNAME": "GitHub Username"
    }
    
    optional_vars = {
        "HF_TOKEN": "Hugging Face API Token (recommended for model access)"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"{var} ({description})")
    
    missing_optional_vars = []
    for var, description in optional_vars.items():
        if not os.environ.get(var):
            missing_optional_vars.append(f"{var} ({description})")
    
    # Report findings
    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        return False
    
    if missing_optional_vars:
        logger.warning("Missing optional environment variables:")
        for var in missing_optional_vars:
            logger.warning(f"  - {var}")
    
    logger.info("All required environment variables are set.")
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
        logger.error("Missing required Python packages:")
        for package in missing_packages:
            logger.error(f"  - {package}")
        logger.error("Install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("All required Python packages are installed.")
    return True

def check_config():
    """Check if the configuration file is valid"""
    try:
        from code_agent.config import Config
        
        config = Config()
        if config.validate():
            logger.info("Configuration is valid.")
            return True
        else:
            logger.warning("Configuration is incomplete or invalid.")
            if not config.github.token:
                logger.warning("  - GitHub token is missing.")
            if not config.github.username:
                logger.warning("  - GitHub username is missing.")
            return False
    except Exception as e:
        logger.error(f"Error checking configuration: {str(e)}")
        return False

def main():
    """Main entry point for the validator"""
    parser = argparse.ArgumentParser(description="Validate the environment for Code Agent")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only show errors, not warnings or info messages")
    
    args = parser.parse_args()
    
    # Adjust logging level if quiet mode is enabled
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Run all checks
    env_valid = check_environment()
    deps_valid = check_dependencies()
    config_valid = check_config()
    
    # Summarize results
    if all([env_valid, deps_valid, config_valid]):
        logger.info("✅ Environment validation successful! Your system is ready to use Code Agent.")
        return 0
    else:
        logger.error("❌ Environment validation failed. Please fix the issues above before using Code Agent.")
        return 1

if __name__ == "__main__":
    sys.exit(main())