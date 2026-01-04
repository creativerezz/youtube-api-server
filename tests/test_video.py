"""
Performance tests for Video Data & Transcript endpoints.
"""
import json
from config import BASE_URL, PERFORMANCE_ITERATIONS, TEST_VIDEOS, TEST_LANGUAGES, REQUEST_TIMEOUT
from utils import make_request, measure_performance, print_test_header


def test_video_data():
    """Test POST /video-data endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-data",
            json={"url": TEST_VIDEOS["short"]},
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_video_captions():
    """Test POST /video-captions endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-captions",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["primary"]
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_video_captions_fallback():
    """Test POST /video-captions with language fallback."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-captions",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["fallback"]
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_video_timestamps():
    """Test POST /video-timestamps endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-timestamps",
            json={
                "url": TEST_VIDEOS["short"],
                "languages": TEST_LANGUAGES["primary"]
            },
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_video_transcript_languages():
    """Test POST /video-transcript-languages endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-transcript-languages",
            json={"url": TEST_VIDEOS["short"]},
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_invalid_url():
    """Test error handling with invalid URL."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/video-data",
            json={"url": "https://invalid-url.com"},
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 1)


def test_cache_effectiveness():
    """Test cache effectiveness by making repeated requests."""
    print("\n  Testing cache effectiveness (3 iterations)...")

    times = []

    for i in range(3):
        response, error = make_request(
            "POST",
            f"{BASE_URL}/video-data",
            json={"url": TEST_VIDEOS["short"]},
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT
        )

        if response and not error:
            import time
            # Simple timing
            start = time.time()
            make_request(
                "POST",
                f"{BASE_URL}/video-data",
                json={"url": TEST_VIDEOS["short"]},
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT
            )
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"    Request {i+1}: {elapsed:.3f}s")

    if len(times) >= 2:
        improvement = ((times[0] - times[-1]) / times[0]) * 100
        print(f"    Cache improvement: {improvement:.1f}%")


def run_all_tests():
    """Run all video endpoint tests."""
    print_test_header("VIDEO DATA & TRANSCRIPT ENDPOINTS")

    results = []

    # Test video data
    metrics = test_video_data()
    metrics.endpoint_name = "video_data"
    passed = metrics.print_report()
    results.append(("POST /video-data", passed))

    # Test captions
    metrics = test_video_captions()
    metrics.endpoint_name = "video_captions"
    passed = metrics.print_report()
    results.append(("POST /video-captions", passed))

    # Test captions with fallback
    metrics = test_video_captions_fallback()
    metrics.endpoint_name = "video_captions"
    passed = metrics.print_report()
    results.append(("POST /video-captions (fallback)", passed))

    # Test timestamps
    metrics = test_video_timestamps()
    metrics.endpoint_name = "video_timestamps"
    passed = metrics.print_report()
    results.append(("POST /video-timestamps", passed))

    # Test languages
    metrics = test_video_transcript_languages()
    metrics.endpoint_name = "video_languages"
    passed = metrics.print_report()
    results.append(("POST /video-transcript-languages", passed))

    # Test error handling
    print_test_header("ERROR HANDLING")
    metrics = test_invalid_url()
    metrics.endpoint_name = "error_handling"
    metrics.print_report()
    # Error handling test - expect 400 error in error messages
    error_passed = any("400" in str(err) for err in metrics.errors) if metrics.errors else False
    results.append(("Error Handling (Invalid URL)", error_passed))

    # Test cache effectiveness
    print_test_header("CACHE EFFECTIVENESS")
    test_cache_effectiveness()

    return results


if __name__ == "__main__":
    from utils import print_summary

    results = run_all_tests()
    print_summary(results)
