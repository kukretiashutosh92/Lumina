LuminaLib Frontend
The LuminaLib Frontend is a modern web application built with Next.js that provides the user interface for the LuminaLib library management system. It communicates with the backend API to handle authentication, book management, borrowing, reviews, and recommendations.
This frontend is designed with scalability, maintainability, and clean architecture in mind.

Technology Stack
The frontend is built using the following technologies:
Core Framework
•	Next.js 14.2.5 (App Router)
•	React 18.2.0
•	TypeScript 5.x
Next.js App Router is used for modern routing, layouts, and server/client component separation.

Styling and UI
•	Tailwind CSS 3.4.1
•	@tabler/icons-react
Tailwind CSS is used for utility-first styling, ensuring consistency and rapid UI development.

Testing
•	Jest
•	React Testing Library
These tools are used for unit testing components, utilities, and page-level logic.

Installation and Setup
You can run the frontend either using Docker (recommended for full-stack setup) or locally for development.

Running with Docker
To run the entire application (frontend + backend + database), refer to the main project README:
../README.md
Docker Compose will handle container orchestration and networking automatically.

Local Development Setup
Follow the steps below to run the frontend locally.

Step 1: Install Dependencies
Navigate to the frontend directory and install required packages:
cd frontend
npm install
This will install:
•	Next.js
•	React
•	TypeScript
•	Tailwind CSS
•	Testing libraries
•	All project dependencies

Step 2: Configure Environment Variables
Set the backend API URL.
By default, the frontend expects the backend to run at:
http://localhost:8000
To override this, set the environment variable:
export NEXT_PUBLIC_API_URL=http://localhost:8000
On Windows (PowerShell):
setx NEXT_PUBLIC_API_URL "http://localhost:8000"
You may also create a .env.local file inside the frontend/ directory:
NEXT_PUBLIC_API_URL=http://localhost:8000
Environment variables prefixed with NEXT_PUBLIC_ are accessible in the browser.

Step 3: Start the Development Server
Run:
npm run dev
The application will start at:
http://localhost:3000
Hot reloading is enabled, meaning changes will automatically refresh the browser.

Available Scripts
The following npm scripts are available:
npm run dev
Starts the development server with hot reloading.
npm run build
Creates an optimized production build.
npm start
Runs the production build locally.
npm run lint
Runs ESLint to check for code quality issues.
npm test
Runs all Jest test suites.

Project Structure
The frontend follows a modular and clean architecture.
frontend/
 └── src/
      ├── app/
      ├── components/
      └── lib/

src/app/
Contains Next.js App Router pages and layouts.
Responsibilities:
•	Page routing
•	Layout definitions
•	Page-level logic
•	Client and server components
Each route corresponds to a folder in this directory.

src/components/
Contains reusable React components.
Examples:
•	BookCard
•	Navigation components
•	Modals
•	Loading indicators
•	Error components
Components are designed to be:
•	Reusable
•	Stateless when possible
•	Well-tested
•	UI-focused (no direct API calls)

src/lib/
Contains shared utilities and core logic.
Key files:
api.ts
Centralized API client.
Responsibilities:
•	All HTTP requests
•	Authentication token injection
•	Error handling
•	Request abstraction
Important rule:
Components must never call fetch() directly.
All network communication must go through:
api.auth.*
api.books.*
api.recommendations.*
This ensures:
•	Centralized error handling
•	Consistent token management
•	Easier testing and mocking

auth-context.tsx
Handles global authentication state.
Responsibilities:
•	Login
•	Logout
•	Token storage
•	User session persistence
•	React context provider
This allows authentication state to be accessed throughout the application.

API Communication Flow
1.	User interacts with UI component.
2.	Component calls a function from api.ts.
3.	API client attaches JWT token (if available).
4.	Request is sent to backend.
5.	Response is handled centrally.
6.	Component updates state.
This pattern ensures separation of concerns and clean architecture.

Code Quality Standards
The project enforces strict code quality guidelines.

Linting
Run:
npm run lint
This checks:
•	Unused variables
•	Incorrect React patterns
•	TypeScript issues
•	Code style violations
Lint errors should be fixed before committing code.

Testing
Run:
npm test
Testing includes:
•	Component rendering
•	User interactions
•	API mocking
•	Authentication flows
•	Utility functions
Tests should pass before merging any feature.

Development Guidelines
To maintain consistency:
•	Use TypeScript for all new files.
•	Do not use any unless absolutely necessary.
•	Keep components small and reusable.
•	Do not call APIs directly inside components.
•	Use Tailwind utility classes for styling.
•	Keep business logic out of UI components.
•	Write tests for new features.

Production Build
To generate a production build:
npm run build
Then run:
npm start
This serves the optimized application.
Production build includes:
•	Code splitting
•	Tree shaking
•	Optimized bundles
•	Minified assets

