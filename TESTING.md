Testing Guide – LuminaLib
This document describes the testing strategy, coverage areas, tools used, and execution steps for LuminaLib.
The project includes:
•	Backend unit and integration tests (FastAPI + pytest)
•	Frontend component and utility tests (Next.js + Jest)
•	ML and LLM validation tests
•	Storage and authentication utility tests

Testing Approach
LuminaLib follows these testing principles:
•	Unit testing for business logic
•	Integration testing for API endpoints
•	Component testing for frontend UI
•	Mock-based isolation for external services (LLM, storage)
•	No dependency on external PostgreSQL during testing
•	Deterministic and repeatable test behavior
Backend tests use in-memory SQLite to avoid requiring PostgreSQL during testing.

Backend Tests
Backend tests are located in:
backend/tests/

Coverage Areas
1. Authentication (tests/test_auth.py)
Covers:
•	User signup
o	Successful registration
o	Duplicate email handling
•	User login
o	Valid credentials
o	Invalid password
o	Non-existent user
•	JWT token validation
•	Get current authenticated user
•	Unauthorized access protection
•	Profile update
•	Signout flow
Validates:
•	Password hashing
•	JWT token generation and decoding
•	Protected route access control

2. Books (tests/test_books.py)
Covers:
Book CRUD:
•	Create book (with file upload)
•	Create book (without file upload)
•	List books (with pagination)
•	Get book details
•	Update book
•	Delete book
Borrow / Return:
•	Borrow book successfully
•	Borrow already borrowed book
•	Borrow non-existing book
•	Return book successfully
•	Return book not borrowed
Reviews:
•	Create review (valid case)
•	Create review without borrowing
•	Invalid rating validation
•	Get book analysis endpoint
Validates:
•	Ownership checks
•	Borrow state transitions
•	Business rule enforcement
•	Validation constraints

3. Recommendations (tests/test_recommendations.py)
Covers:
•	List user preferences
•	Set preferences
•	Update preferences
•	Get personalized recommendations
•	Get similar books
•	Get AI suggestions (by genre)
•	Get AI suggestions (similar to book)
•	Ensure borrowed books are excluded
Validates:
•	Hybrid recommendation logic
•	Filtering correctness
•	Edge cases (empty preferences, empty catalog)

4. Authentication Utilities (tests/test_auth_utils.py)
Covers:
•	Password hashing
•	Password verification
•	JWT creation
•	JWT decoding
•	Token expiration validation
Ensures security logic works independently from API routes.

5. Storage Backend (tests/test_storage.py)
Covers:
•	Local file save
•	File retrieval
•	File deletion
•	Path validation
Uses temporary test directories to avoid modifying real uploads.

6. LLM Backend (tests/test_llm.py)
Covers:
•	Mock summary generation
•	Mock sentiment analysis
•	Mock recommendation ranking
Ensures:
•	Deterministic output
•	No external API dependency
•	Stable AI-related logic

7. Recommendation ML (tests/test_recommendation_ml.py)
Covers:
•	TF-IDF similarity scoring
•	Preference-based filtering
•	Hybrid scoring combination
•	Handling empty datasets
Ensures:
•	Correct ranking order
•	No crashes in edge cases

Running Backend Tests
From the backend directory:
cd backend
pytest
Run with coverage:
pytest --cov=app
Verbose output:
pytest -v
Run a specific file:
pytest tests/test_auth.py
Run a specific test:
pytest tests/test_auth.py::test_signup_success

Backend Test Infrastructure
Framework:
•	pytest
•	pytest-asyncio
Database:
•	SQLite in-memory database
HTTP Client:
•	httpx.AsyncClient
Fixtures:
•	Defined in conftest.py
•	Shared database setup
•	Authenticated user fixtures
•	Test client fixture
Advantages:
•	No external database required
•	Fast execution
•	Fully isolated test runs
•	Repeatable and stable

Frontend Tests
Frontend tests are located inside:
frontend/
Uses:
•	Jest
•	React Testing Library
•	jsdom environment

Component Coverage
Components tested:
•	BookCard (rendering and navigation)
•	ErrorMessage (error display)
•	LoadingSpinner (loading state)
•	Nav (navigation and auth display)
•	BookViewModal (file rendering and pagination)
•	Toaster (notification wrapper)

Page Coverage
LoginPage:
•	Form rendering
•	Input validation
•	API call handling
•	Successful login flow
•	Error display handling

Utility Coverage
api.ts:
•	API request wrapper
•	Error handling
•	Token injection
•	Response parsing
auth-context.tsx:
•	Login logic
•	Logout logic
•	Token storage
•	User state management

Running Frontend Tests
From the frontend directory:
cd frontend
npm test
Watch mode:
npm test -- --watch
Run with coverage:
npm test -- --coverage
Run specific test:
npm test LoginPage

Frontend Test Infrastructure
Framework:
•	Jest
Testing Library:
•	React Testing Library
Environment:
•	jsdom
Mocking:
•	API calls
•	Next.js router
•	Context providers
Advantages:
•	No real backend required
•	Component isolation
•	Fast execution

Coverage Summary
Area	Backend	Frontend
Authentication	Complete	Complete
Books CRUD	Complete	Partial
Borrow/Return	Complete	Partial
Reviews	Complete	Partial
Recommendations	Complete	Partial
File Upload	Complete	Partial
Components	N/A	Complete
Pages	N/A	Partial
Utilities	Complete	Complete
Legend:
Complete – All critical paths covered
Partial – Some paths covered, can be expanded
Missing – No coverage

Adding New Backend Tests
Template:
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_feature_name(client: AsyncClient, auth_headers: dict):
    response = await client.get("/endpoint", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() is not None
Best practices:
•	Test success and failure scenarios
•	Test edge cases
•	Avoid real external dependencies
•	Use fixtures
•	Keep tests isolated

Adding New Frontend Tests
Template:
import { render, screen } from '@testing-library/react'
import Component from './Component'

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
Best practices:
•	Test behavior instead of implementation details
•	Mock API calls
•	Simulate real user interactions
•	Avoid testing internal state directly

Continuous Integration
Tests should run automatically in CI/CD pipelines.
Example GitHub Actions steps:
- name: Run backend tests
  run: |
    cd backend
    pip install -r requirements.txt
    pytest --cov=app

- name: Run frontend tests
  run: |
    cd frontend
    npm install
    npm test -- --coverage
