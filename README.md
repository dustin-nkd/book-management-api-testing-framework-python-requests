# Book Management API Testing Framework

An automated API testing framework for the Book Management system (`https://book.anhtester.com`). Built with Python, `pytest`, `requests`, and `Allure Report`.

## 🚀 Key Features

- **Service Object Model Architecture**: Clean separation between low-level HTTP clients, API services, and test logic.
- **Dynamic Test Data**: Automated generation of unique books, categories, and dummy data to ensure test isolation.
- **Robust Authentication**: Centralized JWT token management via `conftest.py` with support for both session-wide and isolated test-scoped sessions.
- **Comprehensive Reporting**: Integrated with `allure-pytest` to generate detailed, visually appealing HTML reports with logs and network traffic captured.
- **Bug Traceability**: Explicit mappings to manual test cases and known server bugs (tracked via `pytest.xfail`).

## 📁 Project Structure

```text
book-management-api-testing-framework-python-requests/
├── clients/          # Base HTTP client (wrapper around requests with logging)
├── data/             # Test data generators (auth, books, categories)
├── resources/        # Manual test cases (Markdown) and raw JSON specs
├── services/         # API Service classes (AuthService, BookService, CategoryService)
├── tests/            # Test suite (test_auth.py, test_book.py, test_category.py, conftest.py)
├── utils/            # Utility functions (logger, formatting)
├── .env.example      # Environment variables template
├── config.py         # Global configuration loader
├── pytest.ini        # Pytest configuration and markers
└── requirements.txt  # Python dependencies
```

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dustin-nkd/book-management-api-testing-framework-python-requests.git
   cd book-management-api-testing-framework-python-requests
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   # On Windows:
   .\.venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   - Create a `.env` file in the root directory (you can copy from a template if available).
   - Ensure the following variables are set:
     ```env
     BASE_URL=https://book.anhtester.com
     TEST_EMAIL=admin@test.com
     TEST_PASSWORD=password
     ```

## ▶️ Running the Tests

**Run all tests:**
```bash
pytest
```

**Run specific test modules:**
```bash
pytest tests/test_book.py
pytest tests/test_auth.py
```

**Run tests by marker:**
```bash
pytest -m book
pytest -m auth
```

## 📊 Generating Allure Reports

This framework uses Allure for reporting. Test results are automatically collected into the `allure-results` directory when running tests (configured via `pytest.ini` or CLI flags).

1. **Run tests and collect results:**
   ```bash
   pytest --alluredir=allure-results
   ```

2. **Serve the HTML report:**
   *(Requires [Allure Commandline](https://docs.qameta.io/allure/#_installing_a_commandline) installed on your system)*
   ```bash
   allure serve allure-results
   ```

## 📝 Test Cases Documentation
Manual test scenarios and expected results can be found in the `resources/test_cases/` directory. The automated scripts are strictly mapped to these documents.
