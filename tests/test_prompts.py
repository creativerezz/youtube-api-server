"""
Performance tests for Prompt Management endpoints.
"""
from config import BASE_URL, PERFORMANCE_ITERATIONS, REQUEST_TIMEOUT
from utils import make_request, measure_performance, print_test_header, Colors


def get_first_prompt_name():
    """Get the name of the first available prompt."""
    response, error = make_request("GET", f"{BASE_URL}/prompts/")
    if response and not error:
        data = response.json()
        prompts = data.get("prompts", [])
        if prompts:
            return prompts[0].get("name")
    return None


def get_first_category():
    """Get the name of the first available category."""
    response, error = make_request("GET", f"{BASE_URL}/prompts/categories")
    if response and not error:
        data = response.json()
        categories = data.get("categories", [])
        if categories:
            return categories[0]
    return None


def test_prompts_list():
    """Test GET /prompts/ endpoint."""
    def _test():
        return make_request(
            "GET",
            f"{BASE_URL}/prompts/",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_prompts_categories():
    """Test GET /prompts/categories endpoint."""
    def _test():
        return make_request(
            "GET",
            f"{BASE_URL}/prompts/categories",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_prompts_by_category():
    """Test GET /prompts/category/{category} endpoint."""
    category = get_first_category()

    if not category:
        print(f"{Colors.WARNING}  No categories found, skipping test{Colors.ENDC}")
        return None

    def _test():
        return make_request(
            "GET",
            f"{BASE_URL}/prompts/category/{category}",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_prompts_get():
    """Test GET /prompts/{name} endpoint."""
    prompt_name = get_first_prompt_name()

    if not prompt_name:
        print(f"{Colors.WARNING}  No prompts found, skipping test{Colors.ENDC}")
        return None

    def _test():
        return make_request(
            "GET",
            f"{BASE_URL}/prompts/{prompt_name}",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, PERFORMANCE_ITERATIONS)


def test_prompts_refresh():
    """Test POST /prompts/refresh endpoint."""
    def _test():
        return make_request(
            "POST",
            f"{BASE_URL}/prompts/refresh",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 2)  # Refresh only a few times


def test_prompt_not_found():
    """Test 404 error handling for non-existent prompt."""
    def _test():
        return make_request(
            "GET",
            f"{BASE_URL}/prompts/nonexistent_prompt_12345",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 1)


def test_category_not_found():
    """Test 404 error handling for non-existent category."""
    def _test():
        return make_request(
            "GET",
            f"{BASE_URL}/prompts/category/nonexistent_category_12345",
            timeout=REQUEST_TIMEOUT
        )

    return measure_performance(_test, 1)


def test_prompts_availability():
    """Test that prompts are actually available and contain content."""
    print(f"\n{Colors.OKBLUE}Testing prompt content availability...{Colors.ENDC}")

    response, error = make_request("GET", f"{BASE_URL}/prompts/")

    if error:
        print(f"  {Colors.FAIL}✗ Failed to fetch prompt list: {error}{Colors.ENDC}")
        return False

    data = response.json()
    total_prompts = data.get("total", 0)
    prompts = data.get("prompts", [])

    print(f"  Total prompts available: {total_prompts}")

    if not prompts:
        print(f"  {Colors.WARNING}⚠ No prompts found{Colors.ENDC}")
        return False

    # Test first few prompts have content
    test_count = min(3, len(prompts))
    content_ok = True

    for i in range(test_count):
        prompt_name = prompts[i].get("name")
        response, error = make_request("GET", f"{BASE_URL}/prompts/{prompt_name}")

        if error or not response:
            print(f"  {Colors.FAIL}✗ Failed to fetch prompt '{prompt_name}'{Colors.ENDC}")
            content_ok = False
            continue

        prompt_data = response.json()
        content = prompt_data.get("content", "")

        if content:
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} Prompt '{prompt_name}': {len(content)} characters")
        else:
            print(f"  {Colors.FAIL}✗ Prompt '{prompt_name}': No content{Colors.ENDC}")
            content_ok = False

    return content_ok


def run_all_tests():
    """Run all prompt endpoint tests."""
    print_test_header("PROMPT MANAGEMENT ENDPOINTS")

    results = []

    # Test list prompts
    metrics = test_prompts_list()
    if metrics:
        metrics.endpoint_name = "prompts_list"
        passed = metrics.print_report()
        results.append(("GET /prompts/", passed))

    # Test categories
    metrics = test_prompts_categories()
    if metrics:
        metrics.endpoint_name = "prompts_categories"
        passed = metrics.print_report()
        results.append(("GET /prompts/categories", passed))

    # Test prompts by category
    metrics = test_prompts_by_category()
    if metrics:
        metrics.endpoint_name = "prompts_by_category"
        passed = metrics.print_report()
        results.append(("GET /prompts/category/{category}", passed))

    # Test get prompt
    metrics = test_prompts_get()
    if metrics:
        metrics.endpoint_name = "prompts_get"
        passed = metrics.print_report()
        results.append(("GET /prompts/{name}", passed))

    # Test refresh
    metrics = test_prompts_refresh()
    if metrics:
        metrics.endpoint_name = "prompts_refresh"
        passed = metrics.print_report()
        results.append(("POST /prompts/refresh", passed))

    # Test error handling
    print_test_header("ERROR HANDLING")

    metrics = test_prompt_not_found()
    if metrics:
        metrics.endpoint_name = "error_handling"
        metrics.print_report()
        error_passed = any("404" in str(err) for err in metrics.errors) if metrics.errors else False
        results.append(("404 - Prompt Not Found", error_passed))

    metrics = test_category_not_found()
    if metrics:
        metrics.endpoint_name = "error_handling"
        metrics.print_report()
        error_passed = any("404" in str(err) for err in metrics.errors) if metrics.errors else False
        results.append(("404 - Category Not Found", error_passed))

    # Test content availability
    print_test_header("CONTENT AVAILABILITY")
    content_passed = test_prompts_availability()
    results.append(("Prompt Content Availability", content_passed))

    return results


if __name__ == "__main__":
    from utils import print_summary

    results = run_all_tests()
    if results:
        print_summary(results)
