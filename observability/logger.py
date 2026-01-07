import logging
import sys
import time
from typing import Optional

# Professional format for agentic tracing
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s"

class AgentLogger:
    """
    Framework-wide logger for monitoring and benchmarking.
    Supports real-time console output and structured metrics collection.
    """
    def __init__(self, name: str = "Framework"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.start_times = {}

        if not self.logger.handlers:
            # Console Handler
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    # --- Benchmarking Features (Intel DevCloud Requirement) ---

    def start_timer(self, label: str):
        """Starts a timer for a specific task to measure latency."""
        self.start_times[label] = time.perf_counter()

    def stop_timer(self, label: str) -> float:
        """Stops timer and returns elapsed time in milliseconds."""
        if label in self.start_times:
            elapsed = (time.perf_counter() - self.start_times[label]) * 1000
            self.info(f"PERF | {label} completed in {elapsed:.2f}ms")
            return elapsed
        return 0.0

    def log_intel_metric(self, model_name: str, latency: float, device: str):
        """Specifically logs metrics for Intel OpenVINO optimization reports."""
        self.info(f"INTEL_TECH | Model: {model_name} | Latency: {latency:.2f}ms | Device: {device}")
